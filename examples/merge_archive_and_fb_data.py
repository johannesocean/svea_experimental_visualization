#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-06-27 14:51

@author: johannes
"""
from svea_expvis.config import Config
import pandas as pd
import numpy as np
from shapely.geometry import Point
import math


def distance_between_stations(lat1, lon1, lat2, lon2):
    """http://www.johndcook.com/blog/python_longitude_latitude/"""
    if lat1 == lat2 and lon1 == lon2:
        return 0
    degrees_to_radians = math.pi / 180.0
    phi1 = (90.0 - lat1) * degrees_to_radians
    phi2 = (90.0 - lat2) * degrees_to_radians
    theta1 = lon1 * degrees_to_radians
    theta2 = lon2 * degrees_to_radians
    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
           math.cos(phi1) * math.cos(phi2))
    distance = math.acos(cos) * 6371. * 1000.  # 6371 ~ radius of the earth (km) * 1000 m
    return int(distance)


if __name__ == '__main__':
    cfig = Config(data_file_name='phyche_archive_2018-2022.feather')

    df = pd.read_feather(cfig.data_path)
    df_fb = pd.read_csv(
        r'C:\Utveckling\whisky_data\FB_data_19-22.txt',
        sep='\t'
    )
    df_fb['time'] = df_fb['time'].apply(
        lambda x: pd.Timestamp(x).tz_localize('utc'))

    # Select timestamps.
    boolean = df['CPHL'].notna() & df['FLUO_CTD'].notna()
    unique_series = df.loc[boolean, [
        'timestamp', 'LATIT', 'LONGI']].drop_duplicates(
        keep='first').reset_index(drop=True)

    df[['FLUO_FB', 'PHYC_FB']] = np.nan

    time_delta = pd.Timedelta(minutes=120)
    # time_delta = pd.Timedelta(hours=12)
    for row in unique_series.itertuples():
        # print(row.Index)
        t1 = row.timestamp - time_delta
        t2 = row.timestamp + time_delta
        boolean_time = (df_fb['time'] >= t1) & (df_fb['time'] <= t2)

        if boolean_time.any():
            distances = df_fb.loc[boolean_time, ['latitude', 'longitude']].apply(
                lambda x: distance_between_stations(*x, row.LATIT, row.LONGI), axis=1
            )
            idx = distances.index[distances <= 100]
            boolean = (df['timestamp'] == row.timestamp) & \
                      (df['LATIT'] == row.LATIT) & \
                      (df['LONGI'] == row.LONGI)
            df.loc[boolean, 'FLUO_FB'] = np.nanmean(df_fb['FLU2'].iloc[idx]).round(5)
            df.loc[boolean, 'PHYC_FB'] = np.nanmean(df_fb['PHYC'].iloc[idx]).round(5)
            # break

    df.to_feather('phyche_archive_ferrybox_2018-2022.feather')
    df.to_csv(
        'phyche_archive_ferrybox_2018-2022.txt',
        sep='\t',
        index=False,
        encoding='cp1252'
    )
