from dash import html, dcc

# TODO: Link to actual db or df
from ..data import datepicker

start_date, end_date, display_fmt = datepicker.get_date_picker_settings()

date_picker = html.Div(
    [
        dcc.DatePickerRange(
            id='date-picker',
            start_date=start_date,
            end_date=end_date,
            display_format=display_fmt
        ),
    ],
)
