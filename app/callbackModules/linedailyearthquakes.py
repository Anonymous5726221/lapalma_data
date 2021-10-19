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
    Output("line-daily-earthquakes", "figure"),
    [
    #    Input('date-start', 'start_date'),
    #    Input('date-end', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def line_daily_eq(magnitude_range, depth_range):   #TODO: date picker is not implemented yet 
#def line_daily_eq(start_date, end_date, magnitude_range, depth_range):
    df = database.get_unfiltered_df()
    mag_mask, depth_mask = calculations.filter_data(df, None, None, magnitude_range, depth_range)

    # To prevent exceptions, return empty figure if there are no values
    try:
        fig = px.line(df[mag_mask & depth_mask], x="date", y="daily_eq", title="Daily earthquakes.")
    except:
        fig = go.Figure
    return fig