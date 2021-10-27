from dash import html, dcc

map_3d_view_layout = html.Div(children=[
    html.H5("3d map"),
    dcc.Graph(
        id='scatter-3d-map',
        className="eq-map"
    )
])
