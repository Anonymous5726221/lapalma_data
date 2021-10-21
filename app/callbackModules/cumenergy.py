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
        subfig = make_subplots(specs=[[{"secondary_y": True}]])

        fig = px.line(
            df,
            x="time",
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
    except:
        fig = go.Figure()

    return subfig