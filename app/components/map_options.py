from dash import html, dcc

from ..data.copernicus_data import get_copernicus_data, layer_options
from ..server import cache


MAP_STYLES = {
    "Open street map": "open-street-map",
    "Carto Positron": "carto-positron",
    "Carto Dark Matter": "carto-darkmatter",
    "Stamen Terrain": "stamen-terrain",
    "Stamen Toner": "stamen-toner",
    "Stamnen Watercolor": "stamen-watercolor"
}

MAP_TYPES = {
    "Default": "scatter",
    "Heatmap": "heatmap"
}

def map_option():
    return dcc.Dropdown(
        id="map-style",
        options=[{'label': k, 'value': v} for k, v in MAP_STYLES.items()],
        value="open-street-map",
        className="map-option"
    )


def map_overlay():
    overlay_layers = get_copernicus_data()
    opts = layer_options(overlay_layers)
    return dcc.Dropdown(
        id="map-overlay",
        options=[{'label': v, 'value': k} for k, v in opts.items()],
        value="",
        placeholder="Select an overlay... (WIP)",
        className="map-option"
    )


def map_type():
    return dcc.Dropdown(
        id="map-type",
        options=[{'label': k, 'value': v} for k, v in MAP_TYPES.items()],
        value="scatter",
        className="map-option"
    )
