import dash_core_components as dcc
from dash import html
from ..callbackModules import statistictables   # TODO: This shouldn't be here. Structure should remain consistent and this is an outlier.
                                                # Table should output to id='' of a div instead

statsview_layout = html.Div(children=[
    html.Div("statistics"),
    html.Div(
                [
                    html.Div(
                        [
                            html.Label("Weekly stats."),
                            statistictables.stat_table_week(),
                        ],
                        className="DataTable"
                    ),
                    html.Div(
                        [
                            html.Label("Total stats."),
                            statistictables.stat_table_total(),
                        ],
                        className="DataTable"
                    ),
                    html.Div(
                        [
                            html.Label("List of all earthquakes that happened today"),
                            statistictables.today_eqs(),
                        ],
                        className="DataTable"
                    ),
                    html.Div(
                        [
                            html.Label("Daily stats."),
                            statistictables.stat_table_day(),
                        ],
                        className="DataTable"
                    ),
                ],
                className="DataTables"
            )
])