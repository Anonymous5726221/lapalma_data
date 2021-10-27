from dash import html, dcc

mapview_layout = html.Div(children=[
    html.H5("Earthquakes location colored by magnitude"),
    dcc.Graph(
        id='scatter-map-2d',
        className="eq-map"
    ),
    html.H5("Heatmap (Experimental)"),
    dcc.Graph(
        id='heat-map-2d',
        className="eq-map"
    ),
])
