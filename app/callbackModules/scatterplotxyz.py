import os
import logging

from skimage import io
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from ..data import database, calculations

# load app
from ..server import app

logger = logging.getLogger(__name__)


@app.callback(
    Output("scatter-3d-map", "figure"),
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('magnitude-slider', 'value'),
        Input("depth-slider", "value")
    ]
)
def scatter_3d_eq_coord_by_depth(start_date, end_date, magnitude_range, depth_range):
    df = database.get_unfiltered_df()
    date_mask, mag_mask, depth_mask = calculations.filter_data(df, start_date, end_date, magnitude_range, depth_range)

    df = df[date_mask & mag_mask & depth_mask]
    # get image file location
    root_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = root_dir.split('\\')[:-1]
    newPath = ""
    for directory in root_dir:
        newPath = os.path.join(newPath, directory)
    img_file = os.path.join(newPath, 'app', 'assets', 'map.png')

    # coordinates of the map, changing this will fuck up the scaling, need a new map if you want to change this
    lat_min = 28.4007
    lat_max = 28.7105

    lon_min =-17.9915
    lon_max =-17.6973

    # apart from the masks, filter all the datapoints outside of the map to prevent scaling issues or the map not covering the entire plot
    df = df[
        (df.lat <= lat_max) &
        (df.lat >= lat_min) &
        (df.lon <= lon_max) &
        (df.lon >= lon_min)
    ]

    # get image size
    img = io.imread(img_file)
    volume = img.T
    r, c = volume[0].shape

    #scale lat and lon to row and column size of image, in seperate cols so the real lat and lon is still available while hovering
    # Issue: Map is off coordinates by  only a tiny bit. Shifting entire plot slightly.
    # Do note: Only changes physical location on map, it doesn't change the actual coordinates.
    df['lat_scaled'] = calculations.scaling(df.lat-0.025, lat_min, lat_max, c)
    df['lon_scaled'] = calculations.scaling(df.lon+0.025, lon_min, lon_max, r)

    # To prevent exceptions, return empty figure if there are no values
    try:
        fig = px.scatter_3d(df, x='lat_scaled', y='lon_scaled', z=-df['depth'],
                            color='mag', size='mag',
                            hover_data={
                                'lat': True,
                                'lon': True,
                                'depth': True,
                                'mag': True,
                                'lat_scaled': False,    # used to plot, is not useful otherwise
                                'lon_scaled': False     # used to plot, is not useful otherwise
                            },
                            title="Earthquake 3d depth map")

        # add grayscale image to plot (impossible have an image with color :( )
        fig.add_trace(go.Surface(
            z=0 * np.ones((r, c)),
            surfacecolor=volume[0],
            colorscale='Gray',
            showscale=False,
            opacity=0.5,
            cmin=0, cmax=255,
            hoverinfo='skip'    # hoverinfo is turned off, but trace is still a plane. Can't get the data underneath it sadly
            ))

        # only show height, because lat and lon are no longer useful. Hoverdata displays real lat/lon, not scaled
        fig.update_layout(
            scene=dict(
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False),
                zaxis=dict(showticklabels=True),
            ))

        fig.update_layout(scene = dict(
                            xaxis_title='Latitude',
                            yaxis_title='Longitude',
                            zaxis_title='Depth',),
                            template="plotly_dark")
    except Exception as e:
        logger.error(f"Failed to load figure: {e}")
        fig = go.Figure()
        fig.layout.template="plotly_dark"

    # showing this figure is quite intensive and could take a couple of seconds before it's loaded.
    # not sure how it performs on the website...
    return fig