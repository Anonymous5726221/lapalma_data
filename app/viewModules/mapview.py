from dash import html, dcc

mapview_layout = html.Div(children=[
    html.H5("2d map"),
    dcc.Graph(
        id='scatter-map-2d',
    ),
    html.Hr(),
    html.H5("3d map"),
    dcc.Graph(
        id='scatter-3d-map',
    )
])