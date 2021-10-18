import dash_bootstrap_components as dbc
from dash import html


tab_today = dbc.Card(
    [
        html.P("Filter set to 'today'",className="card-text"),
    ],
)
tab_daily = dbc.Card(
    [
        html.P("Filter set to 'daily'",className="card-text"),
    ]
)
tab_weekly = dbc.Card(
    [
        html.P("Filter set to 'weekly'",className="card-text"),
    ]
)
tab_monthly = dbc.Card(
    [
        html.P("Filter set to 'monthly'",className="card-text"),
    ]
)
tab_total = dbc.Card(
    [
        html.P("Filter set to 'total'",className="card-text"),
    ]
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab_today, label="today", tab_id='tab-today'),
        dbc.Tab(tab_daily, label="daily", tab_id='tab-daily'),
        dbc.Tab(tab_weekly, label="weekly", tab_id='tab-weekly'),
        dbc.Tab(tab_monthly, label="monthly", tab_id='tab-monthly'),
        dbc.Tab(tab_total, label="total", tab_id='tab-total'),
    ],
    id='tabs',
    active_tab="tab-today",
    className="nav-fill"
)