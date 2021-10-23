from dash import html, dcc

from ..data import sliders


def depth_slider(df):
    return html.Div(
        [
            dcc.RangeSlider(
                id="depth-slider",
                **sliders.get_depth_slider_settings(df)
            ),
        ],
    )
