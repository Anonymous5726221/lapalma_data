from dash import html, dcc

energyview_layout = html.Div(children=[
    html.Div("Cumulative energy"),
    dcc.Graph(
        id='line-cumenergy',
    ),
])