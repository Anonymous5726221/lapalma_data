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
    c_map = calculations.get_color_map()
    n_bins = calculations.get_n_bins(df, ["date", "mag_range"])

    df = df[date_mask & mag_mask & depth_mask]

    # To prevent exceptions, return empty figure if there are no values
    try:
        fig = px.histogram(
            df.sort_values("mag_range"),
            x="date",
            color="mag_range",
            barmode="group",
            color_discrete_map=c_map,
            title="Earthquake over time sorted by Magnitude range",
            nbins=n_bins,
            template="plotly_dark",
            height = 600
        )
    except Exception as e:
        logger.error(f"Failed to load figure: {e}")
        fig = go.Figure()
        fig.layout.template="plotly_dark"
    return fig