import logging

import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from ..data import database, calculations

# load app
from ..app import app


logger = logging.getLogger(__name__)


@app.callback(
    Output("histogram-mean-mag", "figure"),
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def hist_eq_over_time_mag_mean(start_date, end_date, magnitude_range, depth_range):
    df = database.get_unfiltered_df()
    date_mask, mag_mask, depth_mask = calculations.filter_data(df, start_date, end_date, magnitude_range, depth_range)

    n_bins = calculations.get_n_bins(df, ["date"]) + 10
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

    df = df[date_mask & mag_mask & depth_mask]

    # To prevent exceptions, return empty figure if there are no values
    try:
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
    except Exception as e:
        logger.error(f"Failed to load figure: {e}")
        fig = go.Figure()
    return fig