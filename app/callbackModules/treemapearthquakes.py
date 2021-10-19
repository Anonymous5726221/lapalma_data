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
    Output("treemap-earthquakes", "figure"),
    [
    #    Input('date-start', 'start_date'),
    #    Input('date-end', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def quakes_treemap(magnitude_range, depth_range):   #TODO: date picker is not implemented yet 
#def quakes_treemap(start_date, end_date, magnitude_range, depth_range):
    df = database.get_master_df(None, None, magnitude_range, depth_range)

    df = df.groupby(['week', 'date', 'mag']).size().reset_index(name='count')

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
    return fig