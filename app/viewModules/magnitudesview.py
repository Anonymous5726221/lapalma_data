from dash import html, dcc

magnitudeview_layout = html.Div(children=[
    dcc.Graph(
        id='histogram-range-mag',
        className="eq-graph"
    ),
    dcc.Graph(
        id='histogram-mean-mag',
        className="eq-graph"
    ),
    dcc.Graph(
        id='line-daily-earthquakes',
        className="eq-graph"
    )
])