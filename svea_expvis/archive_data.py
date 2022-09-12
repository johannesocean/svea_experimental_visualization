# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-28 09:42

@author: johannes
"""
import pandas as pd
import geopandas as gp
from shapely.geometry import Point
from svea_expvis.readers.txt import text_reader
from svea_expvis.bokeh_widgets.utils import decmin_to_decdeg
from pysolar.solar import *


def get_zen_angle(lat, lon, ts):
    """"""
    ts = ts.to_pydatetime()
    zendeg = get_altitude(lat, lon, ts)
    return round(zendeg, 1)


QFLAG_MAPPER = {
    'Q_TEMP_BTL': 'TEMP_BTL',
    'Q_TEMP_CTD': 'TEMP_CTD',
    'Q_SALT_BTL': 'SALT_BTL',
    'Q_SALT_CTD': 'SALT_CTD',
    'Q_DOXY_BTL': 'DOXY_BTL',
    'Q_DOXY_CTD': 'DOXY_CTD',
    'Q_H2S': 'H2S',
    'Q_PH': 'PH',
    'Q_PH_LAB': 'PH_LAB',
    'Q_ALKY': 'ALKY',
    'Q_FLUO_CTD': 'FLUO_CTD',
    'Q_CPHL': 'CPHL',
}

PARAMS = [
    'SDATE', 'STIME', 'SHIPC', 'SERNO', 'STATN', 'LATIT', 'LONGI', 'DEPH',
    'TEMP_BTL', 'Q_TEMP_BTL', 'TEMP_CTD', 'Q_TEMP_CTD',
    'SALT_BTL', 'Q_SALT_BTL', 'SALT_CTD', 'Q_SALT_CTD',
    'DOXY_BTL', 'Q_DOXY_BTL', 'DOXY_CTD', 'Q_DOXY_CTD',
    'H2S', 'Q_H2S', 'PH', 'Q_PH', 'PH_LAB', 'Q_PH_LAB',
    'ALKY', 'Q_ALKY',
    'FLUO_CTD', 'Q_FLUO_CTD',
    'CPHL', 'Q_CPHL',
]


def read_archive(fid):
    return text_reader(
        'pandas',
        fid,
        encoding='cp1252',
        sep='\t',
        header=0,
        dtype=str,
        keep_default_na=False,
    )



class PhyCheArchive:
    """Handler of physical and chemical data."""

    def __init__(self, archive_path=None, archive_files=None):
        """Initialize."""
        self.df = pd.DataFrame()
        if archive_path:
            df = read_archive(archive_path)
            self.df = self.df.append(df[PARAMS])
        elif archive_files:
            for fid in archive_files:
                df = read_archive(fid)
                self.df = self.df.append(df[PARAMS], ignore_index=True)

        self.df['KEY'] = self.df[['SDATE', 'SHIPC', 'SERNO']].apply(
            lambda x: '_'.join(x), axis=1
        )
        self.df['timestamp'] = self.df[['SDATE', 'STIME']].apply(
            lambda x: pd.Timestamp(' '.join(x)).tz_localize('utc'),
            axis=1
        )
        self.df = self.df.drop(columns=['SDATE', 'STIME', 'SHIPC', 'SERNO'])

        self.df['LONGI'] = self.df['LONGI'].apply(decmin_to_decdeg)
        self.df['LATIT'] = self.df['LATIT'].apply(decmin_to_decdeg)

        self.add_basin()
        self.exclude_bad_data()
        self.set_float_columns()
        self.set_sun_angle()
        self.export_feather()

    def exclude_bad_data(self):
        """Drop bad data from dataframe."""
        for qf, para in QFLAG_MAPPER.items():
            boolean = self.df[qf].isin(['S', 'B'])
            self.df.loc[boolean, para] = ''
        self.df = self.df.drop(columns=QFLAG_MAPPER.keys())

    def add_basin(self):
        """Add basin info."""
        self.df['SEA'] = ''
        gf = gp.read_file(
            r'C:\Temp\shapes\westsea_balticproper\simple_basins.shp'
        )
        unique_pos = self.df[['LONGI', 'LATIT']].apply('-'.join, axis=1)

        for pos in set(unique_pos):
            lo, la = pos.split('-')
            boolean = gf.contains(Point(float(lo), float(la)))
            if boolean.any():
                boolean_pos = unique_pos == pos
                self.df.loc[boolean_pos, 'SEA'] = gf.loc[boolean, 'SEA'].iloc[0]

    def set_sun_angle(self):
        """Add sun angle.

        Based on coordinates and time.
        """
        self.df['SUN_ANGLE'] = self.df[['LATIT', 'LONGI', 'timestamp']].apply(
            lambda x: get_zen_angle(*x), axis=1
        )

    def set_float_columns(self):
        """Set float type to the given columns."""
        float_cols = ['LATIT', 'LONGI', 'DEPH', 'TEMP_BTL', 'TEMP_CTD', 'SALT_BTL', 'SALT_CTD',
                      'DOXY_BTL', 'DOXY_CTD', 'H2S', 'PH', 'PH_LAB', 'ALKY',
                      'FLUO_CTD', 'CPHL']
        self.df[self.df == ''] = float('nan')
        self.df[float_cols] = self.df[float_cols].astype(float)

    def export_feather(self):
        """Save to feather file."""
        self.df.to_feather('phyche_archive_2018-2022.feather')


if __name__ == '__main__':
    fid_fmt = r'C:\Arbetsmapp\datasets\PhysicalChemical\{YEAR}\SHARK_PhysicalChemical_{YEAR}_BAS_SMHI\processed_data\data.txt'
    files = [
        fid_fmt.format_map({'YEAR': y}) for y in range(2018, 2023)
    ]
    pc_arch = PhyCheArchive(
        # archive_path=data_path,
        archive_files=files,
    )
