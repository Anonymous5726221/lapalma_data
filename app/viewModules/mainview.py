from dash import html, dcc

mainview_layout = html.Div(
    [
        html.H1("Use the sidebar to navigate through the different plots"),
        html.Hr(),
        html.Div(
            [
                html.Div(
                    [
                        html.P("🚧 This site is still under construction and some stuff may be broken:"),
                        html.Ul(
                            [
                                html.Li("There in an issue with the filters not reloading properly. You may need to update the date filter to include today's earthquakes in the charts."),
                                html.Li("The datatables on the statistics page are not updated automatically."),
                                html.Li("UI sizing might be a bit off.")
                            ]
                        ),
                        html.Hr(),
                        html.P(
                            [
                                "If you notice other issues, please report them ",
                                html.A("here.",
                                       href="https://github.com/Anonymous5726221/lapalma_data/issues")
                            ]
                        ),
                    ],
                    className="Disclaimer"
                )
            ],
            id="frontpage-content",
            className="frontpage-content",
        )
    ]
)