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
    Output("scatter-map-2d", "figure"),
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def map_eq(start_date, end_date, magnitude_range, depth_range):
    df = database.get_unfiltered_df()
    date_mask, mag_mask, depth_mask = calculations.filter_data(df, start_date, end_date, magnitude_range, depth_range)

    df = df[date_mask & mag_mask & depth_mask]

    # To prevent exceptions, return empty figure if there are no values
    try:
        fig = go.Figure(go.Scattermapbox(
            lat=df.lat,
            lon=df.lon,
            mode="markers",
            marker={
                "size": df["mag"] * 2 ** 2,
                "color": df.mag,
                "showscale": True,
            },
        ))
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_center_lon=-17.8470,
            mapbox_center_lat=28.6716,
            mapbox_zoom=8,
            # marker_color=df.mag
        )
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            uirevision=f"{start_date}{end_date}",
            showlegend=False,
        )

    except Exception as e:
        logger.error(f"Failed to load figure: {e}")
        fig = go.Figure()

    return fig