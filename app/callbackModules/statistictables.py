import dash_bootstrap_components as dbc
from dash import html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime as dt

from ..data import database, calculations
from ..styles import table_styling

# load app
from ..server import app
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
        style_header=dict(
            backgroundColor='rgb(30,30,30)',
            color='white'
            ),
        style_data=dict(
            backgroundColor='rgb(50,50,50)',
            color='white'
            ),
        style_data_conditional=[
            table_styling.every_other_rows(df),
            *table_styling.highlight_max_value(df),
        ],
        style_table={
            'width': '{}%'.format(100)
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
        style_header=dict(
            backgroundColor='rgb(30,30,30)',
            color='white'
            ),
        style_data=dict(
            backgroundColor='rgb(50,50,50)',
            color='white'
            ),
        style_table={
            'width': '{}%'.format(100)
        },
        style_data_conditional=[
            table_styling.every_other_rows(df),
            *table_styling.highlight_max_value(df),
        ],
    )


def stat_table_total():
    df = database.get_stats_df("all")

    # TODO: Work this into a a component so it can be used by all the table stats
    return dash_table.DataTable(
        columns=[{"name": i, "id": i}
                 for i in df.columns],
        data=df.to_dict('records'),
        style_cell=dict(textAlign='left'),
        style_header=dict(
            backgroundColor='rgb(30,30,30)',
            color='white'
            ),
        style_data=dict(
            backgroundColor='rgb(50,50,50)',
            color='white'
            ),
        style_table={
            'width': '{}%'.format(100)
        }
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
        style_header=dict(
            backgroundColor='rgb(30,30,30)',
            color='white'
            ),
        style_data=dict(
            backgroundColor='rgb(50,50,50)',
            color='white'
            ),
        style_table={
            'width': '{}%'.format(100)
        },
        style_data_conditional=[
            table_styling.every_other_rows(df),
            *table_styling.highlight_max_value(df),
        ],
    )