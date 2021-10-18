import pandas as pd

# After init they can only be changed through callbacks, be mindful of that
def get_magnitude_slider_settings():
    stepsize = 0.5
    minrange = 1.5
    maxrange = 5.0
    marks = {}
    for i in range(int((maxrange-minrange)/stepsize)+1):
        _mark = (i*stepsize) + minrange
        marks[_mark] = f"{_mark}"
    values = [minrange, maxrange]
    return minrange, maxrange, marks, values, stepsize

def get_depth_slider_settings():
    stepsize = 5.0
    minrange = 0.0
    maxrange = 50.0
    marks = {}
    for i in range(int((maxrange-minrange)/stepsize)+1):
        _mark = (i*stepsize) + minrange
        marks[_mark] = f"{_mark}"
    values = [minrange, maxrange]
    return minrange, maxrange, marks, values, stepsize
