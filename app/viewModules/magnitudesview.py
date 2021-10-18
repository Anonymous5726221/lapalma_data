import dash_core_components as dcc
from dash import html

magnitudeview_layout = html.Div(children=[
    html.Div("Histogram based on range"),
    dcc.Graph(
        id='histogram-range-mag',
    ),
    html.Div("Histogram based on mean values per day"),
    dcc.Graph(
        id='histogram-mean-mag',
    ),
    html.Div("total of earthquakes plotted over time"),
    dcc.Graph(
        id='line-daily-earthquakes',
    )
])