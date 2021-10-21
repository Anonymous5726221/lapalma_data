from dash import html, dcc

treemapview_layout = html.Div(children=[
    html.Div("treemap"),
    dcc.Graph(
        id='treemap-earthquakes',
    )
])