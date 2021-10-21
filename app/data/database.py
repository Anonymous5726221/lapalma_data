
from . import calculations
from flask_caching import Cache
import pandas as pd
from urllib.parse import urlparse
import psycopg2
import logging
import os

from .db_helper import tools

from ..app import app

DB_URL = urlparse(os.environ.get("DATABASE_URL"))
DB_HOST = DB_URL.hostname
DB_PORT = DB_URL.port
DB_NAME = DB_URL.path[1:]
DB_USER = DB_URL.username
DB_PASS = DB_URL.password

CACHE_CONFIG = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': "/tmp/cached_master_df"
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)


def process_data(d):
    master_df = pd.DataFrame(d)

    ## Tranform data

    # Remove timezone info to remove numpy deprecation warning
    master_df["time"] = master_df["time"].apply(lambda x: x.replace(tzinfo=None))
    master_df["lastupdate"] = master_df["lastupdate"].apply(lambda x: x.replace(tzinfo=None))

    master_df["lastupdate"] = pd.to_datetime(master_df["lastupdate"])
    master_df["time"] = pd.to_datetime(master_df["time"])
    master_df["date"] = master_df["time"].dt.date

    master_df["depth"] = master_df.depth.astype(int)

    # Enrich data

    # Add week number
    master_df['week'] = master_df['time'].dt.isocalendar().week

    # Create magnitude bins
    m_bins = [
        pd.Interval(left=0, right=2),
        pd.Interval(left=2, right=3),
        pd.Interval(left=3, right=4),
        pd.Interval(left=4, right=5),
        pd.Interval(left=5, right=float("inf"))
    ]

    # m_bins_small = [
    #     pd.Interval(left=-float("inf"), right=3),
    #     pd.Interval(left=3, right=float("inf")),
    # ]

    magnitude_ranges = []
    for index, row in master_df.iterrows():
        for r in m_bins:
            if row["mag"] in r:
                magnitude_ranges.append(r)

    master_df['mag_range'] = magnitude_ranges

    # Auto create bins
    # master_df['mag_range'] = pd.cut(master_df['mag'], bins = 5)

    # Add mean magnitude and depth per day
    master_df = pd.merge(master_df, master_df.groupby("date").mean().round(decimals=1)[["mag", "depth"]], on="date", suffixes=("", "_mean"), how="right")
    master_df = pd.merge(master_df, master_df.groupby("date").size().reset_index(name='daily_eq'), how="left", on=["date"])

    # Add Energy equivalent in Joule
    master_df["energy"] = master_df.mag.apply(lambda x: 10 ** (1.5 * x + 4.8))
    master_df = pd.merge(master_df, master_df.groupby("date")["energy"].sum().reset_index(name='daily_energy'), how="left", on=["date"])

    master_df = master_df.sort_values("time", ignore_index=True)
    master_df["cumEnergy"] = master_df.energy.cumsum()

    return master_df


def _get_master_df():

    logging.info(f"master_df requested")
    try:
        conn = psycopg2.connect(f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASS}")
    except Exception as e:
        logging.error(f"Something f'd up with psycopg: {e}")
        exit(1)

    db_data = tools.get_all_from_db(conn)
    master_df = process_data(db_data)

    return master_df

@cache.memoize(timeout=60)# TODO: Not sure if this is a good idea how I've implemented this. 
def get_unfiltered_df():
    """Get unfiltered dataframe

    Returns:
        pd dataframe: unfiltered dataset
    """
    df = _get_master_df()
    return df

def get_master_df(start_date=None, end_date=None, magnitude_range=None, depth_range=None):
    """get filtered dataframe

    Args:
        df (pd dataframe): pandas dataframe containing La Palma dataset
        start_date (datetime, optional): selected startdate. Defaults to None.
        end_date (datetime, optional): selected enddate. Defaults to None.
        magnitude_range (list[float], optional): selected magnitude range. Defaults to None.
        depth_range (list[float], optional): selected depth range. Defaults to None.

    Returns:
        pd dataframe: filtered dataset
    """
    df = get_unfiltered_df()
    df = calculations.filter_data(df, start_date=None, end_date=None, magnitude_range=None, depth_range=None)
    return df

def get_stats_df(statistics_level="date"):
    """get dataframe with extra statistical columns

    Args:
        statistics_level (str, optional): the level of detail for the table: (date, week, total). Defaults to "date".

    Returns:
        pd dataframe: dataframe with statistical columns
    """
    df = get_unfiltered_df()
    df = calculations.get_statistics(df, statistics_level)
    return df