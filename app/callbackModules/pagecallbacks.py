import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output

# load app
from ..app import app

# TODO: Clean this up and make it more dynamic if possible (probably isn't)
from .. import viewModules

@app.callback(
    Output("content", "children"),
    Input("url", "pathname"),
    )
def render_page_content(pathname):
    if pathname == "/":
        content = viewModules.mainview_layout
    elif pathname == "/magnitudes":
        content = viewModules.magnitudeview_layout
    elif pathname == "/map":
        content = viewModules.mapview_layout
    elif pathname == "/energy":
        content = viewModules.energyview_layout
    elif pathname == "/depth":
        content = viewModules.depthview_layout
    elif pathname == "/treemap":
        content = viewModules.treemapview_layout
    #elif pathname == "/statistics":
    #    content = viewModules.statsview_layout
    else:
        # If the user tries to reach a different page, return a 404 message
        content = dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )
    return content
