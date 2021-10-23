import logging
from dash import html, dcc

from ..data import datepicker


logger = logging.getLogger(__name__)


def date_picker():
    return html.Div(
        [
            dcc.DatePickerRange(
                id='date-picker',
                **datepicker.get_date_picker_settings()
            ),
        ],
    )
