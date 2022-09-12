#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-01-13 16:32

@author: johannes
"""
import sys
sys.path.append('..')

import pandas as pd

from svea_expvis.config import Config
from svea_expvis.bokeh_widgets.map import get_map
from svea_expvis.bokeh_widgets.callbacks import (
    lasso_corr_callback,
    select_callback,
    month_selection_callback,
    range_selection_callback,
    sun_angle_selection_callback,
    range_slider_update_callback,
    check_box_group_axis_scale,
    check_box_group_log,
    linreg_callback,
    station_selection,
)
from svea_expvis.bokeh_widgets.utils import get_columndata_source

from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, PreText, Select, Circle, RangeSlider, Legend, LegendItem
from bokeh.layouts import column, row


output_file("chl_fluo_2018-2022.html")

DEFAULT_PARAMETERS = [
    'TEMP_BTL', 'TEMP_CTD', 'SALT_BTL', 'SALT_CTD',  'DOXY_BTL', 'DOXY_CTD',
    'H2S', 'PH', 'PH_LAB', 'ALKY', 'FLUO_CTD', 'CPHL'
]
STATION_OPTIONS = [
    'Å13', 'Å15', 'Å17', 'SLÄGGÖ', 'P2', 'FLADEN', 'N14 FALKENBERG', 'ANHOLT E',
    'W LANDSKRONA', 'BY1', 'BY2 ARKONA', 'BY4 CHRISTIANSÖ',
    'BY5 BORNHOLMSDJ', 'HANÖBUKTEN', 'REF M1V1', 'BCS III-10', 'BY10',
    'BY15 GOTLANDSDJ', 'BY20 FÅRÖDJUPET', 'BY29/LL19',
    'BY31 LANDSORTSDJ', 'BY32 NORRKÖPING', 'BY38 KARLSÖDJ',
]


cfig = Config(
    data_file_name='phyche_archive_2018-2022.feather'
    # data_file_name='phyche_archive_2020.feather'
)

df = pd.read_feather(cfig.data_path)
df['MONTH'] = df['timestamp'].dt.month

# df = df.loc[df['timestamp'].dt.hour.isin(list(range(9, 17))), :]

position_master_source = get_columndata_source(
    df.loc[:, ['STATN', 'LATIT', 'LONGI', 'KEY', 'MONTH']].drop_duplicates().reset_index(drop=True),
    lat_col='LATIT', lon_col='LONGI',
)
position_source = get_columndata_source(
    df.loc[:, ['STATN', 'LATIT', 'LONGI', 'KEY', 'MONTH']].drop_duplicates().reset_index(drop=True),
    lat_col='LATIT', lon_col='LONGI',
)

data_source = get_columndata_source(df.loc[:, ['KEY', 'DEPH', 'SUN_ANGLE'] + DEFAULT_PARAMETERS], 'FLUO_CTD', 'CPHL')

callback_month = month_selection_callback(position_source=position_source, position_master_source=position_master_source)
month_selector = Select(
    title="Select month",
    value='All',
    options=['All'] + pd.date_range(start='2020-01', freq='M', periods=12).month_name().to_list(),
)
month_selector.js_on_change('value', callback_month)
callback_month.args["month"] = month_selector

fig_map = get_map()

map_renderer = fig_map.circle(
    x="LONGI",
    y="LATIT",
    size=10, alpha=0.5, source=position_source,
)

nonselected_circle = Circle(fill_alpha=0.3, line_color='grey')
map_renderer.nonselection_glyph = nonselected_circle

TOOLTIPS = [
    ("Serie", "@key"),
    ("Depth", "@dep")]
corr = figure(
    width=400, height=400,
    title='Correlation of selected X- and Y values',
    tools='pan,wheel_zoom,box_select,reset,save',
    active_scroll="wheel_zoom",
    tooltips=TOOLTIPS
)
corr.xaxis.axis_label = 'FLUO_CTD'
corr.yaxis.axis_label = 'CPHL'
corr_source = ColumnDataSource(data=dict(x=[], y=[], dep=[], key=[], sun=[]))
corr_renderer = corr.circle(
    x="x",
    y="y",
    size=3, color='red', alpha=0.5, source=corr_source,
)
nonselected_corr_circle = Circle(fill_alpha=0.2, line_color=None)
corr_renderer.nonselection_glyph = nonselected_corr_circle

linreg_source = ColumnDataSource(data=dict(x=[], y=[]))

line_p = corr.line('x', 'y', color="black", alpha=0.7, source=linreg_source)
line_p_legend = LegendItem(label='stats', renderers=[line_p])
# corr.legend.location = "top_left"
corr.add_layout(Legend(items=[line_p_legend], location="top_left"))
linreg_cb = linreg_callback(source=linreg_source, legend_obj=line_p_legend)
corr_source.js_on_change('data', linreg_cb)

x_prof = figure(
    width=400, height=400,
    title='Selected X-profiles',
    tools='pan,wheel_zoom,box_select,reset,save',
    active_scroll="wheel_zoom",
    tooltips=[("Serie", "@key"), ("Value", "@x")]
)
x_prof.xaxis.axis_label = 'FLUO_CTD'
x_prof.yaxis.axis_label = 'Depth (m)'
x_prof.y_range.flipped = True
x_prof.circle(
    x="x",
    y="dep",
    size=3, alpha=0.5, source=corr_source,
)

y_prof = figure(
    width=400, height=400,
    title='Selected Y-profiles',
    tools='pan,wheel_zoom,box_select,reset,save',
    active_scroll="wheel_zoom",
    tooltips=[("Serie", "@key"), ("Value", "@x")]
)
y_prof.xaxis.axis_label = 'CPHL'
y_prof.yaxis.axis_label = 'Depth (m)'
y_prof.y_range.flipped = True
y_prof.circle(
    x="y",
    y="dep",
    size=3, alpha=0.5, source=corr_source,
)

x_sel = Select(value='FLUO_CTD', options=DEFAULT_PARAMETERS, title='X-parameter')
y_sel = Select(value='CPHL', options=DEFAULT_PARAMETERS, title='Y-parameter')

x_sel.js_on_change("value", select_callback(data_source=data_source, axis_objs=[corr.xaxis[0], x_prof.xaxis[0]], axis='x'))
y_sel.js_on_change("value", select_callback(data_source=data_source, axis_objs=[corr.yaxis[0], y_prof.xaxis[0]], axis='y'))  # (y_prof.xaxis[0] is correct, y and x: yes, I know :), you sure?!?! YES! :D)

depth_slider = RangeSlider(start=0, end=100, value=(0, 100),
                           step=0.5, title="Select depth range",
                           width=300)
depth_slider.js_on_change('value', range_selection_callback(data_source=corr_source))

sun_angle_slider = RangeSlider(start=-60, end=60, value=(-60, 60),
                               step=1, title="Select sun angle range",
                               width=300)
sun_angle_slider.js_on_change('value', sun_angle_selection_callback(data_source=corr_source))

checkbox = check_box_group_axis_scale(corr_fig=corr, source=corr_source)
checkbox_log = check_box_group_log()

selection_lasso_change = lasso_corr_callback(
     x_selector=x_sel,
     y_selector=y_sel,
     data_source=data_source,
     position_source=position_source,
     corr_source=corr_source,
     corr_plot=corr,
     logbox=checkbox_log,
)

position_source.selected.js_on_change(
    'indices',
    selection_lasso_change,
    range_slider_update_callback(slider=depth_slider, data_source=corr_source),
)

station_choice = station_selection(
    source=position_source,
    options=STATION_OPTIONS
)

show(
    row(
        column(
            fig_map,
            row(
                x_sel,
                month_selector
            ),
            row(
                y_sel,
                depth_slider
            ),
            row(
                station_choice,
                column(
                    sun_angle_slider,
                    checkbox,
                    checkbox_log,
                )
            ),
        ),
        column(
            row(
                x_prof,
                y_prof
            ),
            corr
        )
    ),
)
