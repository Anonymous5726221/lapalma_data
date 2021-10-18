import dash_core_components as dcc
from dash import html

depthview_layout = html.Div(children=[
    html.Div("depth map"),
    dcc.Graph(
        id='scatter-depth',
    )
])