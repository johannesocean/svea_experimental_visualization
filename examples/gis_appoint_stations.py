#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-01-14 13:38

@author: johannes
"""
import numpy as np
import pandas as pd
import geopandas as gp
from shapely.geometry import Point

from db_conn import DbHandler


HARDCODED_STATIONS = {
    'SLÄGGÖ', 'HANÖBUKTEN', 'FLINTEN-7', 'SKÄLDERVIKEN', 'F33 GRUNDKALLEN'
}


def get_query(table, name, longi, latit):
    """Doc."""
    return f"""
    Update {table} set STATN = '"""+name+f"""' where LONGI = {longi} and LATIT = {latit}
    """


class StnRegShp:
    """Doc. """

    def __init__(self, coordinates_to_match=None):
        self.coordinates_to_match = coordinates_to_match

        stnreg = pd.read_csv(
            r'C:\Arbetsmapp\config\station.txt',
            sep='\t',
            encoding='cp1252',
        )
        self.stnreg = gp.GeoDataFrame(
            stnreg,
            geometry=stnreg[
                ['LONGITUDE_SWEREF99TM', 'LATITUDE_SWEREF99TM']
            ].apply(lambda x: Point(x), axis=1)
        )
        # stnreg.geometry = stnreg.buffer(1000)  # meters
        self.stnreg.geometry = self.stnreg.apply(
            lambda x: x.geometry.buffer(x.OUT_OF_BOUNDS_RADIUS),
            axis=1
        )

    def update_coordinate_list(self, coords, transform=False):
        """Doc."""
        self.coordinates_to_match = gp.GeoDataFrame(
            coords,
            geometry=coords.apply(lambda x: Point(x), axis=1)
        )
        if transform:
            self.coordinates_to_match.crs = 4326
            self.coordinates_to_match = self.coordinates_to_match.to_crs(
                epsg=3006
            )

    def get_name_for_pos(self, point):
        """Doc."""
        boolean = self.stnreg.contains(point)
        return self.stnreg.loc[boolean, 'STATION_NAME'].values


if __name__ == '__main__':
    stnreg = StnRegShp()
    table = 'ctd'

    db_hand = DbHandler(table=table)
    df = db_hand.get_unique_parameter_data(parameter='STATN, LONGI, LATIT')
    stnreg.update_coordinate_list(df[['LONGI', 'LATIT']], transform=True)

    for row in df.itertuples():
        p = stnreg.coordinates_to_match.geometry[row.Index]
        name_list = stnreg.get_name_for_pos(p)
        name = None
        if len(name_list) > 1:
            # print('2 no update', name_list, row.STATN)
            for n in name_list:
                if n in HARDCODED_STATIONS:
                    name = n
        elif len(name_list) == 1:
            name = name_list[0]
        else:
            pass
            # print('0 no update', name_list, row.STATN)
        if name:
            if row.STATN != name:
                query = get_query(table, name, row.LONGI, row.LATIT)
                db_hand.update_db(query)
