# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-23 15:10

@author: johannes
"""
import numpy as np
import pandas as pd
import geopandas as gp
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points
from datetime import datetime as dt
from pyproj import CRS, transform
from decimal import Decimal, ROUND_HALF_UP
from bokeh.models import ColumnDataSource


def round_value(value, nr_decimals=2):
    """Calculate rounded value."""
    return str(Decimal(str(value)).quantize(Decimal('%%1.%sf' % nr_decimals % 1), rounding=ROUND_HALF_UP))


def decmin_to_decdeg(pos, string_type=True, decimals=4):
    """Convert position from decimal degrees into degrees and decimal minutes."""
    pos = float(pos)

    output = np.floor(pos / 100.) + (pos % 100) / 60.
    output = round_value(output, nr_decimals=decimals)
    if string_type:
        return output
    else:
        return float(output)


def convert_projection(lats, lons):
    """Convert coordinates to a different system."""
    project_projection = CRS('EPSG:4326')
    google_projection = CRS('EPSG:3857')
    x, y = transform(project_projection, google_projection, lons, lats, always_xy=True)
    return x, y


def get_columndata_source(df, *args, lat_col=None, lon_col=None):
    """Return a bokeh ColumnDataSource object."""
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


def get_columndata_source_json(indata, xy_params=False):
    """

    indata-structure:
    {
        timestamp: {
            lat: value,
            lon: value,
            data: {
                o2: array,
                dens: array,
                pressure: array
            }
        }
    }
    """
    new_data = {
        'timestring': [],
        'timestamp': [],
        'PRES_CTD': [],
        'DOXY_CTD': [],
        'DENS_CTD': [],
    }
    for key, item in indata.items():
        new_data['DOXY_CTD'].extend(item['data']['o2'])
        new_data['DENS_CTD'].extend(item['data']['dens'])
        new_data['PRES_CTD'].extend(item['data']['pressure'])
        new_data['timestring'].extend([key] * len(item['data']['o2']))
        # new_data['timestamp'].extend([dt.strptime(key, "%Y%m%d%H%M%S")] * len(item['data']['o2']))
        new_data['timestamp'].extend([pd.Timestamp(key)] * len(item['data']['o2']))

    if xy_params:
        new_data['x'] = new_data['DOXY_CTD']
        new_data['y'] = new_data['PRES_CTD']

    return ColumnDataSource(new_data)


def get_position_columndata_source_json(indata):
    """

    indata-structure:
    {
        timestamp: {
            lat: value,
            lon: value,
            data: {
                o2: array,
                dens: array,
                pressure: array
            }
        }
    }
    """
    new_data = {
        'timestring': [],
        'lat': [],
        'lon': []
    }
    for key, item in indata.items():
        new_data['timestring'].append(key)
        new_data['lat'].append(item['lat'])
        new_data['lon'].append(item['lon'])

    xs, ys = convert_projection(new_data['lat'], new_data['lon'])
    new_data['lon'] = xs
    new_data['lat'] = ys

    return ColumnDataSource(new_data)


def get_matching_columndata_source(data_ctd=None, data_mvp=None, match_timestrings=None):
    """Pick out matching values between the data sources."""
    new_data = {
        'timestring': [],
        'timestamp': [],
        'PRES_CTD': [],
        'DOXY_CTD': [],
        'DENS_CTD': [],
        'DOXY_MVP': [],
        'DENS_MVP': [],
    }

    df_ctd = pd.DataFrame(data_ctd.data)
    df_mvp = pd.DataFrame(data_mvp.data)

    for ctd_time, mvp_time in match_timestrings.items():
        mvp_boolean = df_mvp['timestring'] == mvp_time
        ctd_boolean = df_ctd['timestring'] == ctd_time

        ctd_boolean = ctd_boolean & (df_ctd['PRES_CTD'].isin(df_mvp.loc[mvp_boolean, 'PRES_CTD']))
        for row in df_ctd.loc[ctd_boolean, :].itertuples():
            depth_boolean = mvp_boolean & (df_mvp['PRES_CTD'] == row.PRES_CTD)
            if depth_boolean.sum() == 1:
                new_data['timestring'].append(row.timestring)
                new_data['timestamp'].append(row.timestamp)
                new_data['PRES_CTD'].append(row.PRES_CTD)
                new_data['DOXY_CTD'].append(row.DOXY_CTD)
                new_data['DENS_CTD'].append(row.DENS_CTD)
                new_data['DOXY_MVP'].append(df_mvp.loc[depth_boolean, 'DOXY_CTD'].values[0])
                new_data['DENS_MVP'].append(df_mvp.loc[depth_boolean, 'DENS_CTD'].values[0])

    return ColumnDataSource(new_data)


def get_matching_positions(data_ctd=None, data_mvp=None):
    gf_ctd = gp.GeoDataFrame(data_ctd.data)
    gf_ctd.geometry = gf_ctd[['lat', 'lon']].apply(lambda x: Point(x), axis=1)

    gf_mvp = gp.GeoDataFrame(data_mvp.data)
    gf_mvp.geometry = gf_mvp[['lat', 'lon']].apply(lambda x: Point(x), axis=1)
    mvp_points = MultiPoint(gf_mvp['geometry'])

    matching = {}
    for row in gf_ctd.itertuples():
        mvp_index = np.where(gf_mvp.geometry == nearest_points(row.geometry, mvp_points)[1])[0][0]
        if row.geometry.distance(mvp_points[mvp_index]) < 10000:
            matching[row.timestring] = gf_mvp['timestring'][mvp_index]

    # returning dict. Matching CTD-timestring to MVP-timestring {"CTD-timestring": "MVP-timestring"}
    return matching
