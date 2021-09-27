# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-23 15:12

@author: johannes
"""
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, Vendors
tile_provider = get_provider('CARTODBPOSITRON')


def get_map(title='', x_range=None, y_range=None, tooltips=None):
    x_range = x_range or (500000, 3000000)
    y_range = y_range or (7000000, 10000000)
    """Return a bokeh figure."""
    fig = figure(
        x_range=x_range, y_range=y_range,
        x_axis_type="mercator", y_axis_type="mercator",
        plot_height=500, plot_width=800,
        tools="pan,lasso_select,wheel_zoom,reset,save", 
        active_drag="lasso_select",
        active_scroll="wheel_zoom",
        tooltips=tooltips,
        title=title
    )
    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None
    fig.add_tile(tile_provider)

    return fig
