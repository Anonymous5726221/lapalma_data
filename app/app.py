import logging

from dash import html, dcc, Dash
import plotly.io as pio

from .server import app, server
from . import views
from . import callbacks
from . import components
from .data.database import get_unfiltered_df
from .styles.lpmtg_style import lpmtg_template

logger = logging.getLogger(__name__)

pio.templates.default = lpmtg_template

def generate_layout():
    logger.info("Generating layout...")

    df = get_unfiltered_df()

    base_layout = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [*components.sidebar(df)],
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
            html.Div(id="hidden-div", style={"display": "none"})
        ],
        className="container-fluid",
        id="base-layout"
    )

    return html.Div(
        [
            dcc.Location(id="url"),
            html.Div(
                [
                    base_layout
                ]
            )
        ]
    )


app.config.suppress_callback_exceptions=True
app.layout = generate_layout

