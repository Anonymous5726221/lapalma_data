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
    #    Input('date-start', 'start_date'),
    #    Input('date-end', 'end_date'),
        Input('magnitude-slider', 'end_date'),
        Input("depth-slider", "value")
    ]
)
def energy_plot(magnitude_range, depth_range):   #TODO: date picker is not implemented yet 
#def energy_plot(start_date, end_date, magnitude_range, depth_range):
    df = database.get_master_df(None, None, magnitude_range, depth_range)

    subfig = make_subplots(specs=[[{"secondary_y": True}]])


    fig = px.line(
        df, x="time",
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

    return subfig