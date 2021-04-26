# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-23 15:12
@author: johannes
"""
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, Vendors
tile_provider = get_provider('CARTODBPOSITRON')


def get_map():
    fig = figure(
        x_range=(1000000, 3000000), y_range=(7500000, 8500000),
        x_axis_type="mercator", y_axis_type="mercator",
        plot_height=500, plot_width=800,
        tools="pan,reset,wheel_zoom,lasso_select,save", 
        title='X-parameter'
    )

    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None
    fig.add_tile(tile_provider)

    return fig
