from datetime import datetime as dt
from datetime import timedelta
import os
from urllib.parse import urlparse
import logging

import pandas as pd
import numpy as np
import math
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from flask_caching import Cache

import db_helper.tools


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

    # all the calculations for the plots
    master_df = calculations(master_df)

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

    return master_df.sort_values("time", ascending=False, ignore_index=True)


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

    df = master_df[
        (master_df.lat <= 28.961) &
        (master_df.lat >= 28.324) &
        (master_df.lon <= -17.7935) &
        (master_df.lon >= -17.9478) &
        mask_mag &
        mask_depth &
        mask_date
    ]

    range_x = [28.324, 28.961]
    range_y = [-17.7935, -17.9478]
    range_z = [-40, -0]

    fig = px.scatter_3d(
        df,
        x='lat',
        y='lon',
        z=-df['depth'],
        range_x=range_x,
        range_y=range_y,
        range_z=range_z,
        color='mag',
        size=df['mag'] ** 2,
        labels={
            "z": "Depth (km)",
            "mag": "Magnitude",
        },
        title="3D plot of earthquakes depth"
    )

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
        hover_name="time",
        hover_data=["mag", "depth"],
        color="mag",
        size=df["mag"] ** 2,
        color_discrete_sequence=["fuchsia"],
        zoom=8,
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


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


def generate_page_layout():
    master_df = get_master_df()
    layout = html.Div(
        [
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
            html.Div(
                today_eqs(),
            ),
            html.Div(
                quakes_treemap(),
            ),
            html.Div(
                energy_plot(),
            ),
            html.Div(
                stat_table_day(),
            ),
            html.Div(
                stat_table_week(),
            ),
            html.Div(
                stat_table_total(),
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
        # style={"display": "flex"}
    )

    return layout

####calculations####
# calculate every column required for plots
def calculations(df):
    #df["depth"] = -1 * df["depth"]
    df = calc_week_number(df)
    df = calculate_joules(df)
    df = calc_cum_energy(df)
    return df

# calculated in plot def
def calculate_daily_mag(df):
    daily_df = df.groupby(['week', 'date', 'mag']).size().reset_index(name='count')
    return daily_df

# changed the column name to _energy, because 'energy' column already exists
def calculate_joules(df):
    ORDER_OF_MAGNITUDE = 10**9
    joules = []
    for mag in df["mag"]:
        joules.append(math.pow(10, 1.5 * mag + 4.8) / ORDER_OF_MAGNITUDE)
    joules.reverse()
    df["_energy"] = joules
    return df

def calc_cum_energy(df):
    cumEnergy = []
    _sum = 0.0
    for energy in df["_energy"]:
        _sum += energy
        cumEnergy.append(_sum)
    cumEnergy.reverse()
    df["cumEnergy"] = cumEnergy
    return df

def calc_week_number(df):
    df['week'] = df['time'].dt.isocalendar().week
    df['week'] = 'Week ' + df['week'].astype(str)
    return df

# calculated in plot def
def calc_stats_total(df_weekly):
    df_weekly['temp'] = [1] * len(df_weekly)
    df_total_min = df_weekly.groupby(['temp']).min()[['depth_min', 'mag_min']].reset_index()
    df_total_max = df_weekly.groupby(['temp']).max()[['depth_max', 'mag_max']].reset_index()
    df_total_mean = df_weekly.groupby(['temp']).mean().round(decimals=2)[['depth_mean', 'mag_mean']].reset_index()
    df_total_eq = df_weekly.groupby(['temp']).size().reset_index(name="earthquakes")
    df_total_energy = df_weekly.groupby(['temp']).sum().round(decimals=4)[['total_energy [GJ]']].reset_index()
    
    df_total_stats = df_total_min.merge(df_total_max)
    df_total_stats = df_total_stats.merge(df_total_mean)
    df_total_stats = df_total_stats.merge(df_total_eq)
    df_total_stats = df_total_stats.merge(df_total_energy)
    df_total_stats = df_total_stats.drop(columns='temp')

    return df_total_stats

# calculated in plot def
def calc_stats_per_week(df_daily):
    df_weekly_min = df_daily.groupby(['week']).min()[['depth_min', 'mag_min']].reset_index()
    df_weekly_max = df_daily.groupby(['week']).max()[['depth_max', 'mag_max']].reset_index()
    df_weekly_mean = df_daily.groupby(['week']).mean().round(decimals=2)[['depth_mean', 'mag_mean']].reset_index()
    df_weekly_eq = df_daily.groupby(['week']).size().reset_index(name="earthquakes")
    df_weekly_energy = df_daily.groupby(['week']).sum().round(decimals=4)[['total_energy [GJ]']].reset_index()

    df_weekly_stats = df_weekly_min.merge(df_weekly_max, on=['week'])
    df_weekly_stats = df_weekly_stats.merge(df_weekly_mean, on=['week'])
    df_weekly_stats = df_weekly_stats.merge(df_weekly_eq, on=['week'])
    df_weekly_stats = df_weekly_stats.merge(df_weekly_energy, on=['week'])
    
    return df_weekly_stats

# calculated in plot def
def calc_stats_per_day(df):
    df_daily_min = df.groupby(['date','week']).min()[['depth', 'mag']].reset_index().rename(columns={"depth": "depth_min", "mag": "mag_min"})
    df_daily_max = df.groupby(['date','week']).max()[['depth', 'mag']].reset_index().rename(columns={"depth": "depth_max", "mag": "mag_max"})
    df_daily_mean = df.groupby(['date','week']).mean().round(decimals=2)[['depth', 'mag']].reset_index().rename(columns={"depth": "depth_mean", "mag": "mag_mean"})
    df_daily_eq = df.groupby(['date','week']).size().reset_index(name="earthquakes")
    df_daily_energy = df.groupby(['date','week']).sum().round(decimals=4)[['_energy']].reset_index().rename(columns={"_energy": "total_energy [GJ]"})

    df_daily_stats = df_daily_min.merge(df_daily_max, on=['date','week'])
    df_daily_stats = df_daily_stats.merge(df_daily_mean, on=['date','week'])
    df_daily_stats = df_daily_stats.merge(df_daily_eq, on=['date','week'])
    df_daily_stats = df_daily_stats.merge(df_daily_energy, on=['date','week'])
    
    return df_daily_stats

####plots####
# fancy info graphic, earthquakes are sorted on week, day and magnitude
@app.callback(
    Output("quakes_treemap", "figure"),
)
def quakes_treemap():
    df = get_master_df()
    df = calculate_daily_mag(df)
    fig = px.treemap(df, path=[px.Constant("La Palma"),'week', 'date', 'mag'], values='count',
                        color='count', hover_data={
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
)
def energy_plot():
    df = get_master_df()
    subfig = make_subplots(specs=[[{"secondary_y": True}]])

    fig = px.line(df, x="time", y="cumEnergy",
                labels={
                    "cumEnergy":"Energy [GJ]"
                },
                color_discrete_sequence=["green"],
            )
    fig.update_traces(
        line=dict(width=5))

    fig2 = px.scatter(df, x="time", y="mag", size="mag", color="mag",
                        hover_data=["mag"],
            )
            
    fig2.update_traces(yaxis="y2")

    subfig.add_traces(fig2.data + fig.data)
    subfig.layout.xaxis.title="Time"
    subfig.layout.yaxis.title="Energy [GJ]"
    subfig.layout.yaxis2.title="Magnitude"

    subfig.update_xaxes(range=[df.time.min()-pd.Timedelta(hours=1), df.time.max()+pd.Timedelta(hours=1)])

    return subfig

# daily stats
@app.callback(
    Output("day_stats", "figure"),
)
def stat_table_day():
    df = get_master_df()
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    align= 'left'),
        cells=dict(values=[
                        df.date,
                        df.week,
                        df.mag_min,
                        df.mag_max,
                        df.mag_mean,
                        df.depth_min,
                        df.depth_max,
                        df.depth_mean,
                        df.earthquakes,
                        df['total_energy [GJ]']
                        ],
               align='left'))
    ])
    return fig

# weekly stats
@app.callback(
    Output("week_stats", "figure"),
)
def stat_table_week():
    df = get_master_df()
    df = calc_stats_per_day(df)
    df = calc_stats_per_week(df)
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    align= 'left'),
        cells=dict(values=[
                        df.week,
                        df.mag_min,
                        df.mag_max,
                        df.mag_mean,
                        df.depth_min,
                        df.depth_max,
                        df.depth_mean,
                        df.earthquakes,
                        df['total_energy [GJ]']
                        ],
               align='left'))
    ])
    return fig

# total stats
@app.callback(
    Output("total_stats", "figure"),
)
def stat_table_total():
    df = get_master_df()
    df = calc_stats_per_day(df)
    df = calc_stats_per_week(df)
    df = calc_stats_total(df)
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    align= 'left'),
        cells=dict(values=[
                        df.mag_min,
                        df.mag_max,
                        df.mag_mean,
                        df.depth_min,
                        df.depth_max,
                        df.depth_mean,
                        df.earthquakes,
                        df['total_energy [GJ]']
                        ],
               align='left'))
    ])
    return fig

app.layout = generate_page_layout

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True, port=8050)
