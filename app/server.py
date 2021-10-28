from flask import Flask
from flask_caching import Cache

from dash import Dash, html
import dash_bootstrap_components as dbc


external_stylesheets = [
        dbc.themes.DARKLY,
        html.Link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.6.0/font/bootstrap-icons.css"
        ),
    ]

server = Flask('la-palma-data-viz')
app = Dash(external_stylesheets=external_stylesheets, server=server)
app.title = "la-palma-data-viz"

CACHE_CONFIG = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': "/tmp/cached_master_df"
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)

