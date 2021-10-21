import dash_bootstrap_components as dbc
from dash import html


button_gotobegin = dbc.Button("<<<", className="btn btn-secondary", id="go-to-begin")
button_stepbackward = dbc.Button("<", className="btn btn-secondary", id="go-backwards")
button_dummy = dbc.Button("", className="btn btn-secondary active", disabled=True) # Empty button that doesn't do anything, just filler
button_stepforward = dbc.Button(">", className="btn btn-secondary", id="go-forwards")
button_gotoend = dbc.Button(">>>", className="btn btn-secondary", id="go-to-end")


button_group = dbc.ButtonGroup(
    [
        button_gotobegin,
        button_stepbackward,
        button_dummy,
        button_stepforward,
        button_gotoend
    ],
    size="lg"
)