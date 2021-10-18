import dash_core_components as dcc
from dash import html

energyview_layout = html.Div(children=[
    html.Div("Cumulative energy"),
    dcc.Graph(
        id='line-cumenergy',
    ),
])