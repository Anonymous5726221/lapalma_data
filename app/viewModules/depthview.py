from dash import html, dcc

depthview_layout = html.Div(children=[
    dcc.Graph(
        id='scatter-depth',
    )
])