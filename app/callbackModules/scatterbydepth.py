import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from ..data import database, calculations

# load app
from ..app import app

@app.callback(
    Output("scatter-depth", "figure"),
    [
    #    Input('date-start', 'start_date'),
    #    Input('date-end', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def scatter_eq_by_depth(magnitude_range, depth_range):   #TODO: date picker is not implemented yet 
#def scatter_eq_by_depth(start_date, end_date, magnitude_range, depth_range):
    df = database.get_master_df(None, None, magnitude_range, depth_range)

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