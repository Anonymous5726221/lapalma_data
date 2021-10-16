from datetime import datetime as dt
from datetime import timedelta
import os
from urllib.parse import urlparse
import logging

import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
from skimage import io
from plotly.subplots import make_subplots
import psycopg2
from flask_caching import Cache

import db_helper.tools
from downloads import kml_to_zip, df_to_csv

logging.basicConfig(level=logging.INFO)

DB_URL = urlparse(os.environ.get("DATABASE_URL"))
DB_HOST = DB_URL.hostname
DB_PORT = DB_URL.port
DB_NAME = DB_URL.path[1:]
DB_USER = DB_URL.username
DB_PASS = DB_URL.password

app = dash.Dash(__name__)
server = app.server

CACHE_CONFIG = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': "/tmp/cached_master_df"
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)


def process_data(d):
    master_df = pd.DataFrame(d)

    ## Tranform data

    # Remove timezone info to remove numpy deprecation warning
    master_df["time"] = master_df["time"].apply(lambda x: x.replace(tzinfo=None))
    master_df["lastupdate"] = master_df["lastupdate"].apply(lambda x: x.replace(tzinfo=None))

    master_df["lastupdate"] = pd.to_datetime(master_df["lastupdate"])
    master_df["time"] = pd.to_datetime(master_df["time"])
    master_df["date"] = master_df["time"].dt.date

    master_df["depth"] = master_df.depth.astype(int)

    # Enrich data

    # Add week number
    master_df['week'] = master_df['time'].dt.isocalendar().week

    # Create magnitude bins
    m_bins = [
        pd.Interval(left=0, right=2),
        pd.Interval(left=2, right=3),
        pd.Interval(left=3, right=4),
        pd.Interval(left=4, right=5),
        pd.Interval(left=5, right=float("inf"))
    ]

    # m_bins_small = [
    #     pd.Interval(left=-float("inf"), right=3),
    #     pd.Interval(left=3, right=float("inf")),
    # ]

    magnitude_ranges = []
    for index, row in master_df.iterrows():
        for r in m_bins:
            if row["mag"] in r:
                magnitude_ranges.append(r)

    master_df['mag_range'] = magnitude_ranges

    # Auto create bins
    # master_df['mag_range'] = pd.cut(master_df['mag'], bins = 5)

    # Add mean magnitude and depth per day
    master_df = pd.merge(master_df, master_df.groupby("date").mean().round(decimals=1)[["mag", "depth"]], on="date", suffixes=("", "_mean"), how="right")
    master_df = pd.merge(master_df, master_df.groupby("date").size().reset_index(name='daily_eq'), how="left", on=["date"])

    # Add Energy equivalent in Joule
    master_df["energy"] = master_df.mag.apply(lambda x: 10 ** (1.5 * x + 4.8))
    master_df = pd.merge(master_df, master_df.groupby("date")["energy"].sum().reset_index(name='daily_energy'), how="left", on=["date"])

    master_df = master_df.sort_values("time", ignore_index=True)
    master_df["cumEnergy"] = master_df.energy.cumsum()

    return master_df


def _get_master_df():

    logging.info(f"master_df requested")
    try:
        conn = psycopg2.connect(f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASS}")
    except Exception as e:
        logging.error(f"Something f'd up with psycopg: {e}")
        exit(1)

    db_data = db_helper.tools.get_all_from_db(conn)
    master_df = process_data(db_data)

    return master_df


@cache.memoize(timeout=60)
def get_master_df():

    return _get_master_df()


def aggregated_df(master_df, agg="date"):

    to_drop = ["depth", "mag"]

    if agg == "all":
        master_df["all"] = 1
        to_drop.append("all")

    agg_df = master_df.groupby(agg).size().reset_index(name="earthquakes")

    # Need to initialize those 2 columns for the first merge to work.
    agg_df[["depth", "mag"]] = np.NaN

    agg_df = pd.merge(agg_df, master_df.groupby(agg)["energy"].sum().round(decimals=4).reset_index(name='energy'), how="left", on=[agg])
    agg_df = pd.merge(agg_df, master_df.groupby(agg)[['depth', 'mag']].min().reset_index(), how="left", on=[agg], suffixes=("", "_min"))
    agg_df = pd.merge(agg_df, master_df.groupby(agg)[['depth', 'mag']].max().reset_index(), how="left", on=[agg], suffixes=("", "_max"))
    agg_df = pd.merge(agg_df, master_df.groupby(agg)[['depth', 'mag']].mean().reset_index(), how="left", on=[agg], suffixes=("", "_mean"))

    agg_df = agg_df.drop(to_drop, axis=1)

    if agg == "date":
        agg_df['week'] = pd.to_datetime(agg_df['date']).dt.isocalendar().week

    return agg_df


@app.callback(
    Output('dataset_last_update', 'children'),
    Input('interval_10s', 'n_intervals')
)
def dataset_last_update(n):
    df = get_master_df()
    last_update = df.sort_values("lastupdate").iloc[-1].lastupdate
    subtitle = f"Data refreshed on {last_update} UTC. Total earthquake in dataset: {len(df)}."

    return subtitle


@app.callback(
    Output("eq_hist_by_magnitude_range", "figure"),
    [
        Input("slider_mag_hist1", "value"),
        Input('date_picker_hist1', 'start_date'),
        Input('date_picker_hist1', 'end_date')
    ]
)
def eq_hist_by_magnitude_range(slider_mag, start_date, end_date):
    master_df = get_master_df()
    df = master_df[master_df["time"] >= dt(2021, 9, 1)]

    min_mag, max_mag = slider_mag
    mask_mag = (df['mag'] >= min_mag) & (df['mag'] <= max_mag)
    mask_date = (df['date'] >= dt.fromisoformat(start_date).date()) & (df['date'] <= dt.fromisoformat(end_date).date())

    c_map = {
        pd.Interval(left=0, right=2): "rgb(255, 142, 37)",
        pd.Interval(left=2, right=3): "rgb(248, 67, 45)",
        pd.Interval(left=3, right=4): "rgb(217, 13, 57)",
        pd.Interval(left=4, right=5): "rgb(151, 2, 61)",
        pd.Interval(left=5, right=float("inf")): "rgb(49, 49, 49)",
    }

    n_bins = len(df[mask_mag & mask_date].groupby(["date", "mag_range"]))

    fig = px.histogram(
        df[mask_mag & mask_date].sort_values("mag_range"),
        x="date",
        color="mag_range",
        barmode="group",
        color_discrete_map=c_map,
        title="Earthquake over time sorted by Magnitude range",
        nbins=n_bins
    )
    return fig


@app.callback(
    Output("scatter_eq_by_depth", "figure"),
    [
        Input("slider_depth_scatter1", "value"),
        Input('date_picker_scatter1', 'start_date'),
        Input('date_picker_scatter1', 'end_date')
    ]
)
def scatter_eq_by_depth(slider_depth, start_date, end_date):
    master_df = get_master_df()

    min_depth, max_depth = slider_depth
    mask_depth = (master_df['depth'] >= min_depth) & (master_df['depth'] <= max_depth)
    mask_date = (master_df['date'] >= dt.fromisoformat(start_date).date()) & (master_df['date'] <= dt.fromisoformat(end_date).date())

    df = master_df[mask_date & mask_depth]

    fig = px.scatter(
        df,
        x="time",
        y=-df["depth"],
        color="mag",
        size=df["mag"] ** 2 ,
        size_max=15,
        color_discrete_sequence=px.colors.cyclical.IceFire,
        title="Earthquakes over time by depth (colored by magnitude)"
    )
    return fig

@app.callback(
    Output("line_daily_eq", "figure"),
    [
        Input('date_picker_line1', 'start_date'),
        Input('date_picker_line1', 'end_date')
    ]
)
def line_daily_eq(start_date, end_date):
    master_df = get_master_df()

    mask_date = (master_df['date'] >= dt.fromisoformat(start_date).date()) & (master_df['date'] <= dt.fromisoformat(end_date).date())
    df = master_df[mask_date]

    fig = px.line(df, x="date", y="daily_eq", title="Daily earthquakes.")

    return fig

@app.callback(
    Output("eq_hist_by_mean_magnitude", "figure"),
    [
        Input("slider_mag_hist2", "value"),
        Input('date_picker_hist2', 'start_date'),
        Input('date_picker_hist2', 'end_date')
    ]
)
def hist_eq_over_time_mag_mean(slider_range, start_date, end_date):
    master_df = get_master_df()

    min_mag, max_mag = slider_range
    mask_mag = (master_df['mag_mean'] >= min_mag) & (master_df['mag_mean'] <= max_mag)
    mask_date = (master_df['date'] >= dt.fromisoformat(start_date).date()) & (master_df['date'] <= dt.fromisoformat(end_date).date())
    df = master_df[mask_date & mask_mag]

    n_bins = len(master_df.groupby("date")) + 10
    custom_gradient = [
        'rgb(29, 1, 68)',
        'rgb(58, 0, 75)',
        'rgb(85, 0, 81)',
        'rgb(111, 0, 84)',
        'rgb(135, 2, 86)',
        'rgb(158, 17, 86)',
        'rgb(180, 35, 84)',
        'rgb(200, 53, 81)',
        'rgb(217, 73, 77)',
        'rgb(232, 93, 72)',
        'rgb(244, 115, 66)',
        'rgb(254, 137, 61)',
        'rgb(255, 160, 57)',
        'rgb(255, 184, 55)',
        'rgb(255, 207, 58)',
        'rgb(255, 231, 67)',
        'rgb(255, 255, 83)'
    ]
    fig = px.histogram(
        df.sort_values("mag_mean", ascending=False),
        x="date",
        color="mag_mean",
        color_discrete_sequence=custom_gradient,
        nbins=n_bins,
        title="Daily earthquake colored by daily mean magnitude."
    )

    fig.add_trace(go.Scatter(x=df["date"], y=df["daily_energy"], mode="lines+markers", yaxis="y2", line=dict(color='royalblue', width=4)))

    fig.update_layout(
        xaxis={
            "title": "Dates"
        },
        yaxis={
            "title": "Daily earthquakes"
        },
        legend={
            "x": 1.05
        },
        yaxis2=dict(
            color="royalblue",
            title="Energy release",

            anchor="x2",
            overlaying="y",
            side="right",
        ),
    )
    return fig


@app.callback(
    Output("scatter_3d_eq_coord_by_depth", "figure"),
    [
        Input("slider_mag_3d_scatter1", "value"),
        Input("slider_depth_3d_scatter1", "value"),
        Input('date_picker_3d_scatter1', 'start_date'),
        Input('date_picker_3d_scatter1', 'end_date')
    ]
)
def scatter_3d_eq_coord_by_depth(slider_mag, slider_depth, start_date, end_date):
    master_df = get_master_df()

    min_mag, max_mag = slider_mag
    mask_mag = (master_df['mag'] >= min_mag) & (master_df['mag'] <= max_mag)
    min_depth, max_depth = slider_depth
    mask_depth = (master_df['depth'] >= min_depth) & (master_df['depth'] <= max_depth)
    mask_date = (master_df['date'] >= dt.fromisoformat(start_date).date()) & (master_df['date'] <= dt.fromisoformat(end_date).date())

    # get image file location
    root_dir = os.path.dirname(os.path.abspath(__file__))
    img_file = os.path.join(root_dir, 'assets', 'map.png')

    # get image size
    img = io.imread(img_file)
    volume = img.T
    r, c = volume[0].shape

    # coordinates of the map, changing this will fuck up the scaling, need a new map if you want to change this
    lat_min = 28.4007
    lat_max = 28.7105

    lon_min =-17.9915
    lon_max =-17.6973

    #scale lat and lon to row and column size of image, in seperate cols so the real lat and lon is still available while hovering
    # Issue: Map is off coordinates by  only a tiny bit. Shifting entire plot slightly.
    # Do note: Only changes physical location on map, it doesn't change the actual coordinates.
    master_df['lat_scaled'] = scaling(master_df.lat - 0.025, lat_min, lat_max, c)
    master_df['lon_scaled'] = scaling(master_df.lon + 0.025, lon_min, lon_max, r)

    # apart from the masks, filter all the datapoints outside of the map to prevent scaling issues or the map not covering the entire plot
    df = master_df[
        (master_df.lat <= lat_max) &
        (master_df.lat >= lat_min) &
        (master_df.lon <= lon_max) &
        (master_df.lon >= lon_min) &
        mask_mag &
        mask_depth &
        mask_date
    ]

    fig = px.scatter_3d(df, x='lat_scaled', y='lon_scaled', z=-df['depth'],
                        color='mag', size='mag',
                        hover_data={
                            'lat': True,
                            'lon': True,
                            'depth': True,
                            'mag': True,
                            'lat_scaled': False,    # used to plot, is not useful otherwise
                            'lon_scaled': False     # used to plot, is not useful otherwise
                        },
                        title="Earthquake 3d depth map")

    # add grayscale image to plot (impossible have an image with color :( )
    fig.add_trace(go.Surface(
        z=0 * np.ones((r, c)),
        surfacecolor=volume[0],
        colorscale='Gray',
        showscale=False,
        opacity=0.5,
        cmin=0, cmax=255,
        hoverinfo='skip'    # hoverinfo is turned off, but trace is still a plane. Can't get the data underneath it sadly
        ))

    # only show height, because lat and lon are no longer useful. Hoverdata displays real lat/lon, not scaled
    fig.update_layout(
        scene=dict(
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False),
            zaxis=dict(showticklabels=True),
        ))

    fig.update_layout(scene = dict(
                        xaxis_title='Latitude',
                        yaxis_title='Longitude',
                        zaxis_title='Depth'))

    # showing this figure is quite intensive and could take a couple of seconds before it's loaded.
    # not sure how it performs on the website...
    return fig


@app.callback(
    Output("eq_map", "figure"),
    [
        Input('date_picker_eq_map1', 'start_date'),
        Input('date_picker_eq_map1', 'end_date')
    ]
)
def map_eq(start_date, end_date):
    master_df = get_master_df()
    mask_date = (master_df['date'] >= dt.fromisoformat(start_date).date()) & (master_df['date'] <= dt.fromisoformat(end_date).date())

    df = master_df[mask_date]

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="mag",
        size=df["mag"] ** 2,
        color_discrete_sequence=["fuchsia"],
        zoom=8,
        height=600,
        hover_name="time",
        hover_data={
            # "size": False,
            "mag": True,
            "depth": "km"
        },
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


####################################
### CONTRIBUTION FROM DUTCH FREN ###
####################################
@app.callback(
    Output("quakes_treemap", "figure"),
    [
        Input('date_picker_eq_tree_map1', 'start_date'),
        Input('date_picker_eq_tree_map1', 'end_date')

    ]
)
def quakes_treemap(start_date, end_date):
    df = get_master_df()
    mask_date = (df['date'] >= dt.fromisoformat(start_date).date()) & (df['date'] <= dt.fromisoformat(end_date).date())

    df = df[mask_date].groupby(['week', 'date', 'mag']).size().reset_index(name='count')

    fig = px.treemap(
        df,
        path=[px.Constant("La Palma"), 'week', 'date', 'mag'],
        values='count',
        color='count',
        hover_data={
            "count": False,
            "date": True,
            "week": True,
            "mag": True
        },
        title='Earthquakes sorted on week, day, magnitude'
    )
    return fig


# cumulative energy plot with earthquakes plotted on it on a secondary axis
@app.callback(
    Output("energy_plot", "figure"),
    [
        Input('date_picker_eq_energy_plot1', 'start_date'),
        Input('date_picker_eq_energy_plot1', 'end_date')

    ]
)
def energy_plot(start_date, end_date):
    df = get_master_df()
    subfig = make_subplots(specs=[[{"secondary_y": True}]])
    mask_date = (df['date'] >= dt.fromisoformat(start_date).date()) & (df['date'] <= dt.fromisoformat(end_date).date())

    df = df[mask_date]

    fig = px.line(
        df, x="time",
        y="cumEnergy",
        labels={
            "cumEnergy": "Energy"
        },
        color_discrete_sequence=["green"],
    )

    fig.update_traces(
        line=dict(width=5)
    )

    fig2 = px.scatter(
        df,
        x="time",
        y="mag",
        size="mag",
        color="mag",
        hover_data=["mag"],
    )

    fig2.update_traces(yaxis="y2")

    subfig.add_traces(fig2.data + fig.data)
    subfig.layout.xaxis.title = "Time"
    subfig.layout.yaxis.title = "Cumulative energy"
    subfig.layout.yaxis2.title = "Magnitude"

    subfig.update_xaxes(range=[df.time.min() - pd.Timedelta(hours=1), df.time.max() + pd.Timedelta(hours=1)])

    return subfig


# daily stats
def stat_table_day():
    df = aggregated_df(get_master_df(), "date")

    return dash_table.DataTable(
        columns=[{"name": i, "id": i}
                 for i in df.columns],
        data=df.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"),
        style_table={
            'overflowY': 'scroll'
        }
    )


# weekly stats
def stat_table_week():
    df = aggregated_df(get_master_df(), "week")

    return dash_table.DataTable(
        columns=[{"name": i, "id": i}
                 for i in df.columns],
        data=df.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"),
    )


def stat_table_total():
    df = aggregated_df(get_master_df(), "all")

    return dash_table.DataTable(
        columns=[{"name": i, "id": i}
                 for i in df.columns],
        data=df.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"),
    )

# Probably could've done this in-line, but it would've been too difficult to read
def scaling(data, minscaling, maxscaling, maxpxcount):
    """scales lat and lon to pixel count row/col
        Args:
            data (list[float]): list with data to be scaled
            minscaling (float): min range of the data
            maxscaling (float): max range of the data
            maxpxcount (int): pixel count for row/col

        Returns:
            list[float]: input data scaled to lie between 0 and pixelcount
    """
    scaled = np.interp(data, (minscaling, maxscaling), (0, maxpxcount))
    return scaled


###########################
### END OF CONTRIBUTION ###
###########################


def today_eqs():
    master_df = get_master_df()

    df = master_df[master_df["date"] == dt.utcnow().date()][["time", "mag", "depth", "lat", "lon"]]

    return dash_table.DataTable(
        id='today_eq',
        columns=[{"name": i, "id": i}
                 for i in df.columns],
        data=df.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender")
    )


@app.callback(
    Output("download-kml", "data"),
    Input("btn_kml", "n_clicks"),
    prevent_initial_call=True,
)
def download_kml(n_clicks):

    df = get_master_df()
    zipfile = kml_to_zip(df)

    return dcc.send_file(
        zipfile
    )

@app.callback(
    Output('dummy_out_kml', 'children'),
    Input('download-kml', 'data'))
def delete_tmp_kml(filepath):
    try:
        os.remove(f"/tmp/{filepath.get('filename')}")
    except AttributeError:
        logging.warning(f"No file to delete yet.")



@app.callback(
    Output("download-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv(n_clicks):

    df = get_master_df()
    csvfile = df_to_csv(df)

    return dcc.send_file(
        csvfile
    )

@app.callback(
    Output('dummy_out_csv', 'children'),
    Input('download-csv', 'data'))
def delete_tmp_csv(filepath):
    try:
        os.remove(f"/tmp/{filepath.get('filename')}")
    except AttributeError:
        logging.warning(f"No file to delete yet.")



def generate_page_layout():
    master_df = get_master_df()
    layout = html.Div(
        [
            html.Button("Download KML", id="btn_kml"),
            dcc.Download(id="download-kml"),
            html.Div(id='dummy_out_kml'),
            html.Button("Download CSV", id="btn_csv"),
            dcc.Download(id="download-csv"),
            html.Div(id='dummy_out_csv'),
            html.H1(
                children=f"La Palma 2021 eruption data visualization."),
            html.Div(id='dataset_last_update'),
            dcc.Interval(
                id='interval_10s',
                interval=60 * 1000,  # in milliseconds
                n_intervals=0
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(id="eq_hist_by_magnitude_range"),
                            html.P("Magnitude:"),
                            dcc.RangeSlider(
                                id='slider_mag_hist1',
                                min=0, max=9, step=1,
                                # marks={0: '0', 2.5: '2.5'},
                                marks={i: str(i) for i in range(10)},
                                value=[0, 9]
                            ),
                            html.P("Date range:"),
                            dcc.DatePickerRange(
                                id='date_picker_hist1',
                                start_date=(dt.now() - timedelta(days=60)).date(),
                                end_date=dt.now().date(),
                                display_format='YYYY/MM/DD'
                            ),
                        ],
                        # style={'width': '100%', 'display': 'inline-block'},
                        className="chart"
                    ),
                    html.Div(
                        [
                            dcc.Graph(id="scatter_eq_by_depth"),
                            html.P("Depth:"),
                            dcc.RangeSlider(
                                id='slider_depth_scatter1',
                                min=master_df.depth.min(), max=master_df.depth.max(), step=5,
                                # marks={0: '0', 2.5: '2.5'},
                                marks={i: str(i) for i in range(int(master_df.depth.max()) + 1)},
                                value=[0, master_df.depth.max()]
                            ),
                            html.P("Date range:"),
                            dcc.DatePickerRange(
                                id='date_picker_scatter1',
                                start_date=(dt.now() - timedelta(days=60)).date(),
                                end_date=dt.now().date(),
                                display_format='YYYY/MM/DD'
                            ),
                        ],
                        className="chart"
                    ),
                    html.Div(
                        [
                            dcc.Graph(id="line_daily_eq"),
                            html.P("Date range:"),
                            dcc.DatePickerRange(
                                id='date_picker_line1',
                                start_date=(dt.now() - timedelta(days=60)).date(),
                                end_date=dt.now().date(),
                                display_format='YYYY/MM/DD'
                            ),
                        ],
                        className="chart"
                    ),
                    html.Div(
                        [
                            dcc.Graph(id="eq_hist_by_mean_magnitude"),
                            html.P("Magnitude:"),
                            dcc.RangeSlider(
                                id='slider_mag_hist2',
                                min=np.floor(master_df.mag_mean.min()),
                                max=np.ceil(master_df.mag_mean.max()),
                                step=0.5,
                                marks={round(i, 1): str(round(i, 1)) for i in
                                       np.arange(np.floor(master_df.mag_mean.min()), np.ceil(master_df.mag_mean.max()),
                                                 0.5)},
                                value=[np.floor(master_df.mag_mean.min()), np.ceil(master_df.mag_mean.max())]
                            ),
                            html.P("Date range:"),
                            dcc.DatePickerRange(
                                id='date_picker_hist2',
                                start_date=(dt.now() - timedelta(days=60)).date(),
                                end_date=dt.now().date(),
                                display_format='YYYY/MM/DD'
                            ),
                        ],
                        className="chart"
                    ),
                    html.Div(
                        [
                            dcc.Graph(id="scatter_3d_eq_coord_by_depth", style={'width': '90vh', 'height': '90vh'}),
                            html.P("Magnitude:"),
                            dcc.RangeSlider(
                                id='slider_mag_3d_scatter1',
                                min=master_df.mag.min(), max=master_df.mag.max(), step=0.1,
                                # marks={0: '0', 2.5: '2.5'},
                                marks={round(i, 1): str(round(i, 1)) for i in
                                       np.arange(master_df.mag.min(), master_df.mag.max(), 0.1)},
                                value=[0.0, master_df.mag.max()]
                            ),
                            html.P("Depth:"),
                            dcc.RangeSlider(
                                id='slider_depth_3d_scatter1',
                                min=master_df.depth.min(), max=master_df.depth.max(), step=5,
                                # marks={0: '0', 2.5: '2.5'},
                                marks={i: str(i) for i in range(master_df.depth.min(), master_df.depth.max(), 5)},
                                value=[0.0, master_df.depth.max()]
                            ),
                            html.P("Date range:"),
                            dcc.DatePickerRange(
                                id='date_picker_3d_scatter1',
                                start_date=(dt.now() - timedelta(days=60)).date(),
                                end_date=dt.now().date(),
                                display_format='YYYY/MM/DD'
                            ),
                        ],
                        className="chart"
                    ),
                    html.Div(
                        [
                            dcc.Graph(id="eq_map"),
                            html.P("Date range:"),
                            dcc.DatePickerRange(
                                id='date_picker_eq_map1',
                                start_date=(dt.now() - timedelta(days=60)).date(),
                                end_date=dt.now().date(),
                                display_format='YYYY/MM/DD'
                            ),
                        ],
                        className="map"
                    ),
                ],
                className="charts"
            ),
            html.H2(children="These next few charts courtesy of our Dutch fren"),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(id="quakes_treemap"),
                            dcc.DatePickerRange(
                                id='date_picker_eq_tree_map1',
                                start_date=(dt.now() - timedelta(days=60)).date(),
                                end_date=dt.now().date(),
                                display_format='YYYY/MM/DD'
                            ),

                        ],
                        className="chart"
                    ),
                    html.Div(
                        [
                            dcc.Graph(id="energy_plot"),
                            dcc.DatePickerRange(
                                id='date_picker_eq_energy_plot1',
                                start_date=(dt.now() - timedelta(days=60)).date(),
                                end_date=dt.now().date(),
                                display_format='YYYY/MM/DD'
                            ),

                        ],
                        className="chart"
                    ),
                    # html.Div(
                    #     [stat_table_day],
                    #     className="chart"
                    # ),
                ],
                className="charts"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Weekly stats."),
                            stat_table_week(),
                        ],
                        className="DataTable"
                    ),
                    html.Div(
                        [
                            html.Label("Total stats."),
                            stat_table_total(),
                        ],
                        className="DataTable"
                    ),
                    html.Div(
                        [
                            html.Label("List of all earthquakes that happened today"),
                            today_eqs(),
                        ],
                        className="DataTable"
                    ),
                    html.Div(
                        [
                            html.Label("Daily stats."),
                            stat_table_day(),
                        ],
                        className="DataTable"
                    ),
                ],
                className="DataTables"
            ),
            html.Div(
                [
                    dcc.Markdown('''
                        ## Donation
                    
                        If you find this  useful please consider donating to one of my crypto account. Thank you :)
                    
                        [![Donate](https://img.shields.io/badge/Donate-BTC-green.svg?style=plastic&logo=bitcoin)](https://raw.githubusercontent.com/Anonymous5726221/lapalma_data/master/Donate/BTC_Bitcoin)
                        [![Donate](https://img.shields.io/badge/Donate-BNB-green.svg?style=plastic&logo=binance)](https://raw.githubusercontent.com/Anonymous5726221/lapalma_data/master/Donate/BNB_BinanceSmartChain)
                        [![Donate](https://img.shields.io/badge/Donate-FTM-green.svg?style=plastic&logo=data:image/svg%2bxml;base64,PHN2ZyBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGZpbGwtcnVsZT0iZXZlbm9kZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLW1pdGVybGltaXQ9IjIiIHZpZXdCb3g9IjAgMCA1NjAgNDAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxjaXJjbGUgY3g9IjI4MCIgY3k9IjIwMCIgZmlsbD0iIzEzYjVlYyIgcj0iMTUwIiBzdHJva2Utd2lkdGg9IjkuMzc1Ii8+PHBhdGggZD0ibTE3LjIgMTIuOSAzLjYtMi4xdjQuMnptMy42IDktNC44IDIuOC00LjgtMi44di00LjlsNC44IDIuOCA0LjgtMi44em0tOS42LTExLjEgMy42IDIuMS0zLjYgMi4xem01LjQgMy4xIDMuNiAyLjEtMy42IDIuMXptLTEuMiA0LjItMy42LTIuMSAzLjYtMi4xem00LjgtOC4zLTQuMiAyLjQtNC4yLTIuNCA0LjItMi41em0tMTAuMi0uNHYxMy4xbDYgMy40IDYtMy40di0xMy4xbC02LTMuNHoiIGZpbGw9IiNmZmYiIHRyYW5zZm9ybT0ibWF0cml4KDkuMzc1IDAgMCA5LjM3NSAxMzAgNTApIi8+PC9zdmc+)](https://raw.githubusercontent.com/Anonymous5726221/lapalma_data/master/Donate/FTM_Fantom)
                        ''')
                ],
                className="donation"
            ),
        ],
    )

    return layout


app.layout = generate_page_layout


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True, port=8050)
