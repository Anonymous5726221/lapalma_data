from dash import html, dcc
from ..components.map_options import map_option, map_overlay, map_type

mapview_layout = html.Div(children=[
    html.H5("Earthquakes location colored by magnitude"),
    html.Div(
        [
            map_option(),
            map_type(),
            map_overlay(),
        ],
        className="map-options"
    ),
    dcc.Graph(
        id='map-viz',
        className="eq-map"
    ),
])
