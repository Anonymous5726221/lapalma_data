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
from ..styles.color_fader import custom_discrete_sequence


logger = logging.getLogger(__name__)


@app.callback(
    Output("histogram-range-mag", "figure"),
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def eq_hist_by_magnitude_range(start_date, end_date, magnitude_range, depth_range):
    df = database.get_unfiltered_df()
    date_mask, mag_mask, depth_mask = calculations.filter_data(df, start_date, end_date, magnitude_range, depth_range)
    n_bins = calculations.get_n_bins(df, ["date", "mag_range"])

    df = df[date_mask & mag_mask & depth_mask]

    n = len(df.groupby("mag_range").count())
    custom_gradient = custom_discrete_sequence(n)[::-1]

    # To prevent exceptions, return empty figure if there are no values
    try:
        fig = px.histogram(
            df.sort_values("mag_range"),
            x="date",
            color="mag_range",
            barmode="group",
            color_discrete_sequence=custom_gradient,
            title="Earthquake over time sorted by Magnitude range",
            nbins=n_bins,
        )
    except Exception as e:
        logger.error(f"Failed to load figure: {e}")
        fig = go.Figure()
    return fig