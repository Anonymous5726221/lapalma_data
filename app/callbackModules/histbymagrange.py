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
    Output("histogram-range-mag", "figure"),
    [
    #    Input('date-start', 'start_date'),
    #    Input('date-end', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def eq_hist_by_magnitude_range(magnitude_range, depth_range):   #TODO: date picker is not implemented yet 
#def eq_hist_by_magnitude_range(start_date, end_date, magnitude_range, depth_range):
    df = database.get_master_df(None, None, magnitude_range, depth_range)
    c_map = calculations.get_color_map()
    n_bins = calculations.get_n_bins(df, ["date", "mag_range"])

    fig = px.histogram(
        df.sort_values("mag_range"),
        x="date",
        color="mag_range",
        barmode="group",
        color_discrete_map=c_map,
        title="Earthquake over time sorted by Magnitude range",
        nbins=n_bins
    )
    return fig