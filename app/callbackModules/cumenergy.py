import logging

import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from ..data import database, calculations

# load app
from ..app import app


logger = logging.getLogger(__name__)


# cumulative energy plot with earthquakes plotted on it on a secondary axis
@app.callback(
    Output("line-cumenergy", "figure"),
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def energy_plot(start_date, end_date, magnitude_range, depth_range):

    df = database.get_unfiltered_df()
    date_mask, mag_mask, depth_mask = calculations.filter_data(df, start_date, end_date, magnitude_range, depth_range)

    df = df[date_mask & mag_mask & depth_mask]

    # To prevent exceptions, return empty figure if there are no values
    try:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        subfig1 = px.line(
            df,
            x="time",
            y="cumEnergy",
            labels={
                "cumEnergy": "Energy"
            },
            color_discrete_sequence=["green"],
        )

        subfig1.update_traces(
            line=dict(width=5)
        )

        subfig2 = px.scatter(
            df,
            x="time",
            y="mag",
            size="mag",
            color="mag",
            hover_data=["mag"],
        )

        subfig2.update_traces(yaxis="y2")

        fig.add_traces(subfig2.data + subfig1.data)
        fig.layout.xaxis.title = "Time"
        fig.layout.yaxis.title = "Cumulative energy"
        fig.layout.yaxis2.title = "Magnitude"
        fig.layout.title = "Cumulative energy"
        fig.layout.template="plotly_dark"
        fig.layout.height = 800

        fig.update_xaxes(range=[df.time.min() - pd.Timedelta(hours=1), df.time.max() + pd.Timedelta(hours=1)])
    except Exception as e:
        logger.error(f"Failed to load figure: {e}")
        fig = go.Figure()
        fig.layout.template="plotly_dark"

    return fig