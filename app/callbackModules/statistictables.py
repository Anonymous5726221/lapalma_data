import dash_bootstrap_components as dbc
from dash import html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime as dt

from ..data import database, calculations

# load app
from ..app import app

# TODO: Not officially a callback, so not sure what to do with this one yet
# for now it's in here

def stat_table_day():
    df = database.get_stats_df("date")

    # TODO: Work this into a a component so it can be used by all the table stats
    # and add a callback with the tabs? Not sure though
    return dash_table.DataTable(
        columns=[{"name": i, "id": i}
                 for i in df.columns],
        data=df.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"),
        style_table={
            'overflowY': 'scroll'
        }
    )

def stat_table_week():
    df = database.get_stats_df("week")

    # TODO: Work this into a a component so it can be used by all the table stats
    return dash_table.DataTable(
        columns=[{"name": i, "id": i}
                 for i in df.columns],
        data=df.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"),
    )


def stat_table_total():
    df = database.get_stats_df("all")

    # TODO: Work this into a a component so it can be used by all the table stats
    return dash_table.DataTable(
        columns=[{"name": i, "id": i}
                 for i in df.columns],
        data=df.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"),
    )

def today_eqs():
    master_df = database.get_unfiltered_df()

    df = master_df[master_df["date"] == dt.utcnow().date()][["time", "mag", "depth", "lat", "lon"]]

    return dash_table.DataTable(
        id='today_eq',
        columns=[{"name": i, "id": i}
                 for i in df.columns],
        data=df.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender")
    )