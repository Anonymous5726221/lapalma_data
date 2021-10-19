import pandas as pd
import numpy as np
from datetime import datetime as dt
from datetime import timedelta

def filter_data(df, start_date=None, end_date=None, magnitude_range=None, depth_range=None):
    """Apply selected filter over dataframe

    Args:
        df (pd dataframe): pandas dataframe containing La Palma dataset
        start_date (datetime, optional): selected startdate. Defaults to None.
        end_date (datetime, optional): selected enddate. Defaults to None.
        magnitude_range (list[float], optional): selected magnitude range. Defaults to None.
        depth_range (list[float], optional): selected depth range. Defaults to None.

    Returns:
        pd dataframe: filtered dataset
    """
    #TODO: Uncomment once datepicker is available
    #date_mask = (df['date'] >= dt.fromisoformat(start_date).date()) & (df['date'] <= dt.fromisoformat(end_date).date())
    mag_mask = (df['mag'] >= magnitude_range[0]) & (df['mag'] <= magnitude_range[1])
    depth_mask = (df['depth'] >= depth_range[0]) & (df['depth'] <= depth_range[1])
    
    #return date_mask, mag_mask, depth_mask
    return mag_mask, depth_mask

def get_statistics(df, statistics_level):
    to_drop = ["depth", "mag"]

    if statistics_level == "all":
        df["all"] = 1
        to_drop.append("all")

    agg_df = df.groupby(statistics_level).size().reset_index(name="earthquakes")

    # Need to initialize those 2 columns for the first merge to work.
    agg_df[["depth", "mag"]] = np.NaN

    agg_df = pd.merge(agg_df, df.groupby(statistics_level)["energy"].sum().round(decimals=4).reset_index(name='energy'), how="left", on=[statistics_level])
    agg_df = pd.merge(agg_df, df.groupby(statistics_level)[['depth', 'mag']].min().reset_index(), how="left", on=[statistics_level], suffixes=("", "_min"))
    agg_df = pd.merge(agg_df, df.groupby(statistics_level)[['depth', 'mag']].max().reset_index(), how="left", on=[statistics_level], suffixes=("", "_max"))
    agg_df = pd.merge(agg_df, df.groupby(statistics_level)[['depth', 'mag']].mean().reset_index(), how="left", on=[statistics_level], suffixes=("", "_mean"))

    agg_df = agg_df.drop(to_drop, axis=1)

    if statistics_level == "date":
        agg_df['week'] = pd.to_datetime(agg_df['date']).dt.isocalendar().week

    return agg_df
    
def get_color_map():
    c_map = {
        pd.Interval(left=0, right=2): "rgb(255, 142, 37)",
        pd.Interval(left=2, right=3): "rgb(248, 67, 45)",
        pd.Interval(left=3, right=4): "rgb(217, 13, 57)",
        pd.Interval(left=4, right=5): "rgb(151, 2, 61)",
        pd.Interval(left=5, right=float("inf")): "rgb(49, 49, 49)",
    }
    return c_map

def get_n_bins(df, groupby):
    """get the number of bins using groupby

    Args:
        df (pd dataframe): dataframe with La Palma dataset
        groupby (list): List of every column the dataframe has to use

    Returns:
        int: Number of bins
    """
    n_bins = len(df.groupby(groupby))
    return n_bins

# Probably could've done this in-line, but it would've been too difficult to read
def scaling(data, minscaling, maxscaling, maxpxcount):
    """scales lat and lon to pixel count row/col
        Args:
            data (list[float]): list with data to be scaled
            minscaling (float): min range of the data
            maxscaling (float): max range of the data
            maxpxcount (int): pixel count for row/col

        Returns:
            list[float]: input data scaled to lie between 0 and pixelcount
    """
    scaled = np.interp(data, (minscaling, maxscaling), (0, maxpxcount))
    return scaled