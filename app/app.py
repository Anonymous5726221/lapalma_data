import dash
from dash import html
from dash import dcc
from dash.html.Div import Div
import dash_bootstrap_components as dbc

# workaround to make app callable from other modules
app = None


################################
# Default layout used for view #
################################
# load components
from . import components
# load views
from . import views

BASELAYOUT = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [components.sidebar],
                    id="sidebar-layout",
                    className="col-md-2",
                ),
                html.Div(
                    [
                        html.Div(
                            [],
                            id="content"
                        ),
                    ],
                    className="col-md-10",
                )
            ],
            className="row"
        ),
        html.Div(id="hidden-div", style={"display":"none"})
    ],
    className="container-fluid",
    id="base-layout"
)

def init_app():
    global app

    # This is the only time 
    layout = html.Div([
        BASELAYOUT
    ])

    # TODO: Figure out a way to import local stylesheets, can't get it to work atm.
    # Html link doesn't work either...
    external_stylesheets = [
        dbc.themes.DARKLY,
        # html.Link(
        #     rel="stylesheet",
        #     href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.6.0/font/bootstrap-icons.css"
        # ),
    ]

    app = dash.Dash(external_stylesheets=external_stylesheets)

    # Callbacks generate an exception when the html structure isn't 'fixed'
    # Needs to be surpressed, because it's giving out false exceptions
    app.config.suppress_callback_exceptions=True

    app.layout = html.Div([dcc.Location(id="url"), layout])

    # load callbacks
    from . import callbacks

    app.run_server(debug=True)
