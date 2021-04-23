# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-23 15:10
@author: johannes
"""
from pyproj import CRS, transform
from bokeh.models import ColumnDataSource


def convert_projection(lats, lons):
    project_projection = CRS('EPSG:4326')
    google_projection = CRS('EPSG:3857')
    x, y = transform(project_projection, google_projection, lons, lats, always_xy=True)
    return x, y


def get_columndata_source(df):

    xs, ys = convert_projection(df['latitude'].astype(float).values,
                                df['longitude'].astype(float).values)
    df['LONGI'] = xs
    df['LATIT'] = ys
    df['x'] = 0
    df['y'] = 0
    df = df.drop(columns=['latitude', 'longitude'])

    return ColumnDataSource(df)
