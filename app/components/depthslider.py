import dash_bootstrap_components as dbc
from dash import html, dcc

# TODO: Link to actual db or df
from ..data import sliders
_minrange, _maxrange, _marks, _values, _stepsize = sliders.get_depth_slider_settings()

depth_slider = html.Div(
    [
        dcc.RangeSlider(
            id="depth-slider",
            min= _minrange,
            max= _maxrange,
            step= _stepsize,
            marks= _marks,
            value= _values,
            allowCross= False,
        ),
    ],
)