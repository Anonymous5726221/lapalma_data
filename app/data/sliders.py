import logging
import math


logger = logging.getLogger(__name__)


def get_magnitude_slider_settings(df):
    logger.info("Calculating magnitude slide settings")

    stepsize = 0.5
    minrange = math.floor(df.mag.min())
    maxrange = math.ceil(df.mag.max())
    marks = {}

    for i in range(int((maxrange-minrange)/stepsize)+1):
        _mark = (i*stepsize) + minrange
        marks[_mark] = f"{_mark}"

    logger.debug(f"Magnitude marks are {marks}")

    values = [minrange, maxrange]
    return {
        "min": minrange,
        "max": maxrange,
        "step": stepsize,
        "marks": marks,
        "value": values,
        "allowCross": False
    }


def get_max_depth(df):

    multiple = 5
    n = df.depth.max()
    steps = n // multiple
    if n % multiple != 0:
        steps += 1

    return steps * multiple


def get_depth_slider_settings(df):
    logger.info("Calculating depth slide settings")

    stepsize = 5.0
    minrange = 0.0
    maxrange = get_max_depth(df)
    marks = {i: f"{i}" for i in range(0, maxrange+1, 5)}
    logger.debug(f"Depth marks are {marks}")
    values = [minrange, maxrange]

    return {
        "min": minrange,
        "max": maxrange,
        "step": stepsize,
        "marks": marks,
        "value": values,
        "allowCross": False
    }
