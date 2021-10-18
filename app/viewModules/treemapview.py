import dash_core_components as dcc
from dash import html

treemapview_layout = html.Div(children=[
    html.Div("treemap"),
    dcc.Graph(
        id='treemap-earthquakes',
    )
])