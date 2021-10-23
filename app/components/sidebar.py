from dash.html import Br
import dash_bootstrap_components as dbc
from dash import html, dcc

# load sidebar components
from .magnitudeslider import magnitude_slider
from .depthslider import depth_slider
from .datepicker import date_picker
from .tabs import tabs
from .buttongroup import button_group


def sidebar(df):
    sidebar_content = html.Div(
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
            html.P("Timeframe", style={"display": "none"}),  # TODO: Temp until we figure out how to make this work
            html.Div(tabs, style={"display": "none"}),  # tabs don't make sense when you can pick dates
            html.P("Magnitude"),
            html.Div([magnitude_slider(df)]),
            html.P("Depth"),
            html.Div([depth_slider(df)]),
            html.P("Date picker"),
            html.Div([date_picker()]),
            html.P("Move through data", style={"display": "none"}),
            # TODO: Temp until we figure out how to make this work
            html.Div([button_group], style={"display": "none"}),  # Same as above, but for buttons
        ],
        id="default sidebar",
        className="sidebar"
    )

    donation = html.Div(
        [
            dcc.Markdown('''
        #### Donation

        If you find this  useful please consider donating to one of my crypto account. Thank you :)

        [![Donate](https://img.shields.io/badge/Donate-BTC-green.svg?style=plastic&logo=bitcoin)](https://raw.githubusercontent.com/Anonymous5726221/lapalma_data/master/app/Donate/BTC_Bitcoin)
        [![Donate](https://img.shields.io/badge/Donate-BNB-green.svg?style=plastic&logo=binance)](https://raw.githubusercontent.com/Anonymous5726221/lapalma_data/master/app/Donate/BNB_BinanceSmartChain)
        [![Donate](https://img.shields.io/badge/Donate-FTM-green.svg?style=plastic&logo=data:image/svg%2bxml;base64,PHN2ZyBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGZpbGwtcnVsZT0iZXZlbm9kZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLW1pdGVybGltaXQ9IjIiIHZpZXdCb3g9IjAgMCA1NjAgNDAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxjaXJjbGUgY3g9IjI4MCIgY3k9IjIwMCIgZmlsbD0iIzEzYjVlYyIgcj0iMTUwIiBzdHJva2Utd2lkdGg9IjkuMzc1Ii8+PHBhdGggZD0ibTE3LjIgMTIuOSAzLjYtMi4xdjQuMnptMy42IDktNC44IDIuOC00LjgtMi44di00LjlsNC44IDIuOCA0LjgtMi44em0tOS42LTExLjEgMy42IDIuMS0zLjYgMi4xem01LjQgMy4xIDMuNiAyLjEtMy42IDIuMXptLTEuMiA0LjItMy42LTIuMSAzLjYtMi4xem00LjgtOC4zLTQuMiAyLjQtNC4yLTIuNCA0LjItMi41em0tMTAuMi0uNHYxMy4xbDYgMy40IDYtMy40di0xMy4xbC02LTMuNHoiIGZpbGw9IiNmZmYiIHRyYW5zZm9ybT0ibWF0cml4KDkuMzc1IDAgMCA5LjM3NSAxMzAgNTApIi8+PC9zdmc+)](https://raw.githubusercontent.com/Anonymous5726221/lapalma_data/master/app/Donate/FTM_Fantom)
        ''')
        ],
        className="donation"
    )

    return sidebar_content, donation
