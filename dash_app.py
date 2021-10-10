from datetime import datetime as dt
from datetime import timedelta
import os
import json

import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import flask

from SeismicPortal.dl_quakes import CANARY_BOX, SeismicPortal


# app = flask.Flask(__name__)
# dash_app = dash.Dash(__name__, server = app, url_base_pathname = '/')
app = dash.Dash(__name__)
server = app.server


def get_eq_data(force=False):

    canary_data_path = "resource/canary_eqs.json"
    data_age = dt.now() - dt.fromtimestamp(os.path.getmtime(canary_data_path))

    if data_age > timedelta(hours=6) or force:

        sp = SeismicPortal()
        results = sp.download_earthquakes(start_time=dt.now() - timedelta(days=60), **CANARY_BOX)

        with open(canary_data_path, "w") as outf:
            json.dump(results, outf, indent=2)

    with open(canary_data_path) as inf:
        return json.load(inf)


RESULTS = get_eq_data()

master_df = pd.DataFrame([q.get("properties") for q in RESULTS])

## Tranform data

# Remove timezone info to remove numpy deprecation warning
master_df["time"] = master_df["time"].apply(lambda x: x.strip("Z"))
master_df["lastupdate"] = master_df["lastupdate"].apply(lambda x: x.strip("Z"))

master_df["lastupdate"] = pd.to_datetime(master_df["lastupdate"])
master_df["time"] = pd.to_datetime(master_df["time"])
master_df["date"] = master_df["time"].dt.date

master_df["depth"] = master_df.depth.astype(int)

# Enhance data

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

master_df = master_df.sort_values("time", ascending=False, ignore_index=True)

app.layout = html.Div(
    [
        html.H1(children=f"La Palma 2021 eruption data visualization. Data last refreshed on {dt.fromtimestamp(os.path.getmtime('resource/canary_eqs.json'))}"),
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
        dcc.Graph(id="line_daily_eq"),
        html.P("Date range:"),
        dcc.DatePickerRange(
            id='date_picker_line1',
            start_date=(dt.now() - timedelta(days=60)).date(),
            end_date=dt.now().date(),
            display_format='YYYY/MM/DD'
        ),
        dcc.Graph(id="eq_hist_by_mean_magnitude"),
        html.P("Magnitude:"),
        dcc.RangeSlider(
            id='slider_mag_hist2',
            min=master_df.mag_mean.min(), max=master_df.mag_mean.max(), step=0.1,
            # marks={0: '0', 2.5: '2.5'},
            marks={round(i, 1): str(round(i, 1)) for i in np.arange(master_df.mag_mean.min(), master_df.mag_mean.max(), 0.1)},
            value=[0.0, master_df.mag_mean.max()]
        ),
        html.P("Date range:"),
        dcc.DatePickerRange(
            id='date_picker_hist2',
            start_date=(dt.now() - timedelta(days=60)).date(),
            end_date=dt.now().date(),
            display_format='YYYY/MM/DD'
        ),
        dcc.Graph(id="scatter_3d_eq_coord_by_depth", style={'width': '90vh', 'height': '90vh'}),
        html.P("Magnitude:"),
        dcc.RangeSlider(
            id='slider_mag_3d_scatter1',
            min=master_df.mag.min(), max=master_df.mag.max(), step=0.1,
            # marks={0: '0', 2.5: '2.5'},
            marks={round(i, 1): str(round(i, 1)) for i in np.arange(master_df.mag.min(), master_df.mag.max(), 0.1)},
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
        dcc.Markdown('''
        ## Donation

        If you find this  useful please consider donating to one of my crypto account. Thank you :)
        
        [![Donate](https://img.shields.io/badge/Donate-BTC-green.svg?style=plastic&logo=bitcoin)](https://raw.githubusercontent.com/Anonymous5726221/lapalma_data/master/Donate/BTC_Bitcoin)
        [![Donate](https://img.shields.io/badge/Donate-BNB-green.svg?style=plastic&logo=binance)](https://raw.githubusercontent.com/Anonymous5726221/lapalma_data/master/Donate/BNB_BinanceSmartChain)
        [![Donate](https://img.shields.io/badge/Donate-FTM-green.svg?style=plastic&logo=data:image/svg%2bxml;base64,PHN2ZyBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGZpbGwtcnVsZT0iZXZlbm9kZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLW1pdGVybGltaXQ9IjIiIHZpZXdCb3g9IjAgMCA1NjAgNDAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxjaXJjbGUgY3g9IjI4MCIgY3k9IjIwMCIgZmlsbD0iIzEzYjVlYyIgcj0iMTUwIiBzdHJva2Utd2lkdGg9IjkuMzc1Ii8+PHBhdGggZD0ibTE3LjIgMTIuOSAzLjYtMi4xdjQuMnptMy42IDktNC44IDIuOC00LjgtMi44di00LjlsNC44IDIuOCA0LjgtMi44em0tOS42LTExLjEgMy42IDIuMS0zLjYgMi4xem01LjQgMy4xIDMuNiAyLjEtMy42IDIuMXptLTEuMiA0LjItMy42LTIuMSAzLjYtMi4xem00LjgtOC4zLTQuMiAyLjQtNC4yLTIuNCA0LjItMi41em0tMTAuMi0uNHYxMy4xbDYgMy40IDYtMy40di0xMy4xbC02LTMuNHoiIGZpbGw9IiNmZmYiIHRyYW5zZm9ybT0ibWF0cml4KDkuMzc1IDAgMCA5LjM3NSAxMzAgNTApIi8+PC9zdmc+)](https://raw.githubusercontent.com/Anonymous5726221/lapalma_data/master/Donate/FTM_Fantom)
        ''')
    ]
)


@app.callback(
    Output("eq_hist_by_magnitude_range", "figure"),
    [
        Input("slider_mag_hist1", "value"),
        Input('date_picker_hist1', 'start_date'),
        Input('date_picker_hist1', 'end_date')
    ]
)
def eq_hist_by_magnitude_range(slider_mag, start_date, end_date):
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

    # fig = px.histogram(df.sort_values("mag_range"), x="date", color="mag_range", barmode="group", color_discrete_sequence=px.colors.cyclical.IceFire)
    fig = px.histogram(
        df[mask_mag & mask_date].sort_values("mag_range"),
        x="date",
        color="mag_range",
        barmode="group",
        color_discrete_map=c_map,
        title="Earthquake over time sorted by Magnitude range"
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

    min_mag, max_mag = slider_range
    mask_mag = (master_df['mag'] >= min_mag) & (master_df['mag'] <= max_mag)
    mask_date = (master_df['date'] >= dt.fromisoformat(start_date).date()) & (master_df['date'] <= dt.fromisoformat(end_date).date())
    df = master_df[mask_date & mask_mag]

    n_bins = len(master_df.groupby("date")) + 10

    fig = px.histogram(
        df,
        x="date",
        color="mag_mean",
        color_discrete_sequence=px.colors.sequential.thermal,
        nbins=n_bins,
        title="Daily earthquake colored by daily mean magnitude."
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


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True, port=8050)
