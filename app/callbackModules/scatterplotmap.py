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
    Output("scatter-map-2d", "figure"),
    [
    #    Input('date-start', 'start_date'),
    #    Input('date-end', 'end_date'),
        Input('magnitude-slider', 'end_date'),
        Input("depth-slider", "value")
    ]
)
def map_eq(magnitude_range, depth_range):   #TODO: date picker is not implemented yet 
#def hist_eq_over_time_mag_mean(start_date, end_date, magnitude_range, depth_range):
    df = database.get_master_df(None, None, magnitude_range, depth_range)

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="mag",
        size=df["mag"] ** 2,
        color_discrete_sequence=["fuchsia"],
        zoom=8,
        height=600,
        hover_name="time",
        hover_data={
            # "size": False,
            "mag": True,
            "depth": "km"
        },
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig