from dash import html, dcc

depthview_layout = html.Div(children=[
    html.Div("depth map"),
    dcc.Graph(
        id='scatter-depth',
    )
])