from dash import html, dcc

energyview_layout = html.Div(children=[
    dcc.Graph(
        id='line-cumenergy',
        className="eq-graph"
    ),
])