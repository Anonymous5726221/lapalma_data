import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


############################################################################
# This serves as a controller that loads all the different views in /views #
############################################################################
from . import viewModules