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
    Output("treemap-earthquakes", "figure"),
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def quakes_treemap(start_date, end_date, magnitude_range, depth_range):
    df = database.get_unfiltered_df()
    date_mask, mag_mask, depth_mask = calculations.filter_data(df, start_date, end_date, magnitude_range, depth_range)

    df = df.groupby(['week', 'date', 'mag']).size().reset_index(name='count')
    df = df[date_mask & mag_mask & depth_mask]

    # To prevent exceptions, return empty figure if there are no values
    try:
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
    except Exception as e:
        logger.error(f"Failed to load figure: {e}")
        go.Figure()
    return fig