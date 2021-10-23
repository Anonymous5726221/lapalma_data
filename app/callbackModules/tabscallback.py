from dash.dependencies import Input, Output

# load app
from ..server import app
@app.callback(
    Output("hidden-div", "children"),
    [Input("tabs", "active_tab")]
)
def set_datePicker(active_tab):
    if active_tab == "tab-today":
        pass
    elif active_tab == "tab-daily":
        pass
    elif active_tab == "tab-weekly":
        pass
    elif active_tab == "tab-monthly":
        pass
    elif active_tab == "tab-total":
        pass
    return None # You're forced to have an output..