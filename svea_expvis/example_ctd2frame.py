# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-05-03 17:59

@author: johannes
"""
import os
import pandas as pd
from ctdpy.core.utils import generate_filepaths
from ctdpy.core.session import Session as ctd_session
from svea_expvis.bokeh_widgets.utils import decmin_to_decdeg
from svea_expvis.filter import Filter


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


class CTD2Frame:
    """Example class."""

    def __init__(self, data_path=None):
        """Initialize."""
        files = generate_filepaths(data_path,
                                   pattern='ctd_profile_',
                                   endswith='.txt')

        filter_obj = Filter([os.path.basename(f) for f in files])
        filter_obj.add_filter(month_list=[9, 10])
        files = [f for f in files if os.path.basename(f) in filter_obj.valid_file_names]

        # ctd = ctd_session(filepaths=files, reader='smhi')

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
        """Description."""
        for qf, para in QFLAG_MAPPER.items():
            boolean = self.df[qf].isin(['S', 'B'])
            self.df.loc[boolean, para] = ''
        self.df = self.df.drop(columns=QFLAG_MAPPER.keys())

    def set_float_columns(self):
        """Description."""
        float_cols = ['LATIT', 'LONGI', 'DEPH', 'TEMP_BTL', 'TEMP_CTD', 'SALT_BTL', 'SALT_CTD',
                      'DOXY_BTL', 'DOXY_CTD',  'FLUO_CTD', 'CPHL']
        self.df[self.df == ''] = float('nan')
        self.df[float_cols] = self.df[float_cols].astype(float)

    def export_feather(self):
        """Description."""
        self.df.to_feather('phyche_archive.feather')
