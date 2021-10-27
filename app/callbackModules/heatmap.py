import logging

from dash.dependencies import Input, Output
import plotly.graph_objects as go

from ..data import database, calculations

# load app
from ..server import app

logger = logging.getLogger(__name__)


@app.callback(
    Output("heat-map-2d", "figure"),
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def heatmap_eq(start_date, end_date, magnitude_range, depth_range):
    df = database.get_unfiltered_df()
    date_mask, mag_mask, depth_mask = calculations.filter_data(df, start_date, end_date, magnitude_range, depth_range)

    df = df[date_mask & mag_mask & depth_mask]

    # To prevent exceptions, return empty figure if there are no values
    try:

        fig = go.Figure(go.Densitymapbox(
            lat=df.lat,
            lon=df.lon,
            z=df.mag,
            radius=df["mag"] ** 2,
        ))
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_center_lon=-17.8470,
            mapbox_center_lat=28.6716,
            mapbox_zoom=8
        )
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            uirevision=f"{start_date}{end_date}",
        )

    except Exception as e:
        logger.error(f"Failed to load figure: {e}")
        fig = go.Figure()

    return fig
