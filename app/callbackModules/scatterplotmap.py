import logging

from dash.dependencies import Input, Output
import plotly.graph_objects as go

from ..data import database, calculations, copernicus_data

# load app
from ..server import app

logger = logging.getLogger(__name__)


@app.callback(
    Output("map-viz", "figure"),
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value"),
        Input("map-style", "value"),
        Input("map-overlay", "value"),
        Input("map-type", "value"),
    ]
)
def map_eq(start_date, end_date, magnitude_range, depth_range, map_style, map_overlay, map_type):
    df = database.get_unfiltered_df()
    date_mask, mag_mask, depth_mask = calculations.filter_data(df, start_date, end_date, magnitude_range, depth_range)

    df = df[date_mask & mag_mask & depth_mask]

    ovr = {}
    if map_overlay:
        type_raw = map_overlay.split("_")[-1]
        if type_raw == "Point":
            type = "circle"
        if type_raw == "Area":
            type = "fill"
        if type_raw == "Line":
            type = "line"
        overlay = copernicus_data.overlay(map_overlay)
        ovr = {
            "below": 'traces',
            'type': type,
            'circle': {"radius": 10},
            'color': "red",
            "opacity": 0.75,
            "source": overlay
        }

    # To prevent exceptions, return empty figure if there are no values
    try:
        if map_type == "scatter":
            fig = go.Figure(go.Scattermapbox(
                lat=df.lat,
                lon=df.lon,
                mode="markers",
                marker={
                    "size": df["mag"] * 2 ** 2,
                    "color": df.mag,
                    "showscale": True,
                },
            ))
        elif map_type == "heatmap":
            fig = go.Figure(go.Densitymapbox(
                lat=df.lat,
                lon=df.lon,
                z=df.mag,
                radius=df["mag"] ** 2,
            ))
        else:
            raise Exception("map type unknown")

        fig.update_layout(
            mapbox_style=map_style,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            uirevision=f"{start_date}{end_date}",
            showlegend=False,
            mapbox_center_lon=-17.8470,
            mapbox_center_lat=28.6716,
            mapbox_zoom=8,
            mapbox_layers=[ovr]
        )

    except Exception as e:
        logger.error(f"Failed to load figure: {e}")
        fig = go.Figure()

    return fig