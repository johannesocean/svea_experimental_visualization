# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-28 09:42

@author: johannes
"""
import pandas as pd
from svea_expvis.readers.txt import text_reader
from svea_expvis.bokeh_widgets.utils import decmin_to_decdeg


QFLAG_MAPPER = {
    'Q_TEMP_BTL': 'TEMP_BTL',
    'Q_TEMP_CTD': 'TEMP_CTD',
    'Q_SALT_BTL': 'SALT_BTL',
    'Q_SALT_CTD': 'SALT_CTD',
    'Q_DOXY_BTL': 'DOXY_BTL',
    'Q_DOXY_CTD': 'DOXY_CTD',
    'Q_FLUO_CTD': 'FLUO_CTD',
    'Q_CPHL': 'CPHL',
}


class PhyCheArchive:
    """Handler of physical and chemical data."""

    def __init__(self, archive_path=None):
        """Initialize."""
        archive_path = archive_path or r'C:\PhysicalChemical\2019\
        SHARK_PhysicalChemical_2019_BAS_SMHI\processed_data\data.txt'
        df = text_reader(
            'pandas',
            archive_path,
            encoding='cp1252',
            sep='\t',
            header=0,
            dtype=str,
            keep_default_na=False,
        )

        params = [
            'SDATE', 'STIME', 'SHIPC', 'SERNO', 'STATN', 'LATIT', 'LONGI', 'DEPH',
            'TEMP_BTL', 'Q_TEMP_BTL', 'TEMP_CTD', 'Q_TEMP_CTD',
            'SALT_BTL', 'Q_SALT_BTL', 'SALT_CTD', 'Q_SALT_CTD',
            'DOXY_BTL', 'Q_DOXY_BTL', 'DOXY_CTD', 'Q_DOXY_CTD',
            'FLUO_CTD', 'Q_FLUO_CTD',
            'CPHL', 'Q_CPHL',
        ]

        self.df = df[params]
        self.df['KEY'] = self.df[['SDATE', 'SHIPC', 'SERNO']].apply(lambda x: '_'.join(x), axis=1)
        self.df['timestamp'] = self.df[['SDATE', 'STIME']].apply(
            lambda x: pd.Timestamp(' '.join(x)),
            axis=1
        )
        self.df = self.df.drop(columns=['SDATE', 'STIME', 'SHIPC', 'SERNO'])

        self.df['LONGI'] = self.df['LONGI'].apply(decmin_to_decdeg)
        self.df['LATIT'] = self.df['LATIT'].apply(decmin_to_decdeg)

        self.exclude_bad_data()
        self.set_float_columns()
        self.export_feather()

    def exclude_bad_data(self):
        """Drop bad data from dataframe."""
        for qf, para in QFLAG_MAPPER.items():
            boolean = self.df[qf].isin(['S', 'B'])
            self.df.loc[boolean, para] = ''
        self.df = self.df.drop(columns=QFLAG_MAPPER.keys())

    def set_float_columns(self):
        """Set float type to the given columns."""
        float_cols = ['LATIT', 'LONGI', 'DEPH', 'TEMP_BTL', 'TEMP_CTD', 'SALT_BTL', 'SALT_CTD',
                      'DOXY_BTL', 'DOXY_CTD',  'FLUO_CTD', 'CPHL']
        self.df[self.df == ''] = float('nan')
        self.df[float_cols] = self.df[float_cols].astype(float)

    def export_feather(self):
        """Save to feather file."""
        self.df.to_feather('phyche_archive_2019.feather')
