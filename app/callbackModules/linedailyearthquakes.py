import logging

import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from ..data import database, calculations

# load app
from ..server import app


logger = logging.getLogger(__name__)


@app.callback(
    Output("line-daily-earthquakes", "figure"),
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def line_daily_eq(start_date, end_date, magnitude_range, depth_range):
    df = database.get_unfiltered_df()
    date_mask, mag_mask, depth_mask = calculations.filter_data(df, start_date, end_date, magnitude_range, depth_range)

    df = df[date_mask & mag_mask & depth_mask]
    df = database.get_stats_df("date", df)

    # To prevent exceptions, return empty figure if there are no values
    try:
        fig = px.line(df, x="date", y="earthquakes", title="Daily earthquakes.", text="earthquakes")
        fig.update_traces(textposition="bottom right")
    except Exception as e:
        logger.error(f"Failed to load figure: {e}")
        fig = go.Figure
    return fig