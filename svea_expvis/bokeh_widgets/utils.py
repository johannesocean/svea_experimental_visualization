# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-23 15:10
@author: johannes
"""
import numpy as np
from pyproj import CRS, transform
from bokeh.models import ColumnDataSource


def decmin_to_decdeg(pos):
    pos = float(pos)
    if pos < 99:
        return pos

    output = np.floor(pos/100.) + (pos % 100)/60.
    output = "%.5f" % output
    return float(output)


def convert_projection(lats, lons):
    project_projection = CRS('EPSG:4326')
    google_projection = CRS('EPSG:3857')
    x, y = transform(project_projection, google_projection, lons, lats, always_xy=True)
    return x, y


def get_columndata_source(df, *args, lat_col=None, lon_col=None):

    if lat_col:
        xs, ys = convert_projection(df[lat_col].astype(float).values,
                                    df[lon_col].astype(float).values)
        df['LONGI'] = xs
        df['LATIT'] = ys

    if any(args):
        params = list(args)
        df['x'] = df[params[0]]
        df['y'] = df[params[1]]

    if lon_col and lat_col and (lon_col != 'LONGI' and lat_col != 'LATIT'):
        df = df.drop(columns=[lat_col, lon_col])

    return ColumnDataSource(df)
