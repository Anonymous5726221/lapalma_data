from dash.html import Br
import dash_bootstrap_components as dbc
from dash import html, dcc

# load sidebar components
from .magnitudeslider import magnitude_slider
from .depthslider import depth_slider
from .datepicker import date_picker
from .tabs import tabs
from .buttongroup import button_group


# the style arguments for the sidebar. fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "17%",
    "padding": "2rem 1rem",
    "background-color": "#332D2C",
}

sidebar = html.Div(
    [
        html.H2("La Palma", className="display-4"),
        html.Hr(),
        html.P(
            "Use links below to navigate through the views", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Magnitudes", href="/magnitudes", active="exact"),
                dbc.NavLink("Map", href="/map", active="exact"),
                dbc.NavLink("Energy", href="/energy", active="exact"),
                dbc.NavLink("Depth", href="/depth", active="exact"),
                dbc.NavLink("Treemap", href="/treemap", active="exact"),
                dbc.NavLink("Statistics", href="/statistics", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Hr(),
        html.H4("Filters"),
        html.P("Timeframe", style={"display":"none"}),  # TODO: Temp until we figure out how to make this work
        html.Div(tabs, style={"display":"none"}),       # tabs don't make sense when you can pick dates
        html.P("Magnitude"),
        html.Div([magnitude_slider]),
        html.P("Depth"),
        html.Div([depth_slider]),
        html.P("Date picker"),
        html.Div([date_picker]),
        html.P("Move through data", style={"display":"none"}),    # TODO: Temp until we figure out how to make this work
        html.Div([button_group], style={"display":"none"})        # Same as above, but for buttons
    ],
    style=SIDEBAR_STYLE,
    id="default sidebar"
)