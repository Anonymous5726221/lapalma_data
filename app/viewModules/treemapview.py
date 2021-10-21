from dash import html, dcc

treemapview_layout = html.Div(children=[
    dcc.Graph(
        id='treemap-earthquakes',
    )
])