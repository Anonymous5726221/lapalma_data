from dash import html, dcc
from ..callbackModules import statistictables   # TODO: This shouldn't be here. Structure should remain consistent and this is an outlier.
                                                # Table should output to id='' of a div instead

def statsview_layout():
    return html.Div(children=[
        html.Div(
                [
                    html.Hr(),
                    html.Div(
                        [
                            html.H5("List of all earthquakes that happened today"),
                            statistictables.today_eqs(),
                        ],
                        className="DataTable"
                    ),
                    html.Hr(),
                    html.Div(
                        [
                            html.H5("Daily stats."),
                            statistictables.stat_table_day(),
                        ],
                        className="DataTable"
                    ),
                    html.Hr(),
                    html.Div(
                        [
                            html.H5("Weekly stats."),
                            statistictables.stat_table_week(),
                        ],
                        className="DataTable"
                    ),
                    html.Hr(),
                    html.Div(
                        [
                            html.H5("Total stats."),
                            statistictables.stat_table_total(),
                        ],
                        className="DataTable"
                    ),
                ],
                className="DataTables"
            )
        ]
    )
