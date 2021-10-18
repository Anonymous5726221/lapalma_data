import dash_core_components as dcc
from dash import html

mapview_layout = html.Div(children=[
    html.Div("2d map"),
    dcc.Graph(
        id='scatter-map-2d',
    ),
    html.Div("3d map"),
    dcc.Graph(
        id='scatter-3d-map',
    )
])