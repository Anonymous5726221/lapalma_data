from dash import html, dcc

magnitudeview_layout = html.Div(children=[
    dcc.Graph(
        id='histogram-range-mag',
    ),
    html.Hr(),
    dcc.Graph(
        id='histogram-mean-mag',
    ),
    html.Hr(),
    dcc.Graph(
        id='line-daily-earthquakes',
    )
])