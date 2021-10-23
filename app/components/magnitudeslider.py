from dash import html, dcc

from ..data import sliders


def magnitude_slider(df):
    return html.Div(
        [
            dcc.RangeSlider(
                id="magnitude-slider",
                **sliders.get_magnitude_slider_settings(df)
            ),
        ],
    )
