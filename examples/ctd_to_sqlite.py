#!/usr/bin/env python3
"""
Created on 2022-01-11 14:48

@author: johannes
"""
import pandas as pd
from db_conn import DbHandler

from ctdpy.core.session import Session
from ctdpy.core.calculator import Calculator
from ctdpy.core.utils import generate_filepaths, decmin_to_decdeg


DB_COLUMNS = [
    'timestamp', 'KEY', 'STATN', 'LATIT', 'LONGI', 'DEPH',
    'CHLFLUO_CTD', 'PHYC_CTD'
]


if __name__ == '__main__':
    db_hand = DbHandler(table='ctd')

    base_dir = r'C:\Temp\CTD_DV\qc_SMHI_2020\data'
    # base_dir = r'test_data'

    files = generate_filepaths(
        base_dir,
        pattern_list=['.cnv'],
        only_from_dir=False,
    )
    s = Session(
        filepaths=files,
        reader='smhi',
    )
    ctdsets = s.read()

    dep_calc = Calculator()
    for key, item in ctdsets[0].items():
        print(key)
        gogo = False

        if 'CHLFLUO_CTD' in item['data']:
            gogo = True
            if 'PHYC_CTD' not in item['data']:
                item['data']['PHYC_CTD'] = ''

        elif 'PHYC_CTD' in item['data']:
            gogo = True
            item['data']['CHLFLUO_CTD'] = ''

        if gogo:
            item['data']['DEPH'] = dep_calc.get_true_depth(
                attribute_dictionary={
                    'latitude': item['metadata']['LATIT'],
                    'pressure': item['data']['PRES_CTD'].astype(float),
                    'gravity': item['data']['PRES_CTD'].astype(float),
                    'density': item['data']['DENS_CTD'].astype(float),
                }
            )

            item['data']['LATIT'] = decmin_to_decdeg(item['metadata']['LATIT'].replace('N', '').replace(' ', ''), string_type=False)
            item['data']['LONGI'] = decmin_to_decdeg(item['metadata']['LONGI'].replace('E', '').replace(' ', ''), string_type=False)
            item['data']['STATN'] = item['metadata']['STATN']
            item['data']['timestamp'] = pd.Timestamp(' '.join((item['metadata'][k] for k in ('SDATE', 'STIME'))))
            item['data']['KEY'] = '_'.join((
                item['metadata']['SDATE'][:4],
                s.settings.smap.get(item['metadata']['SHIPC']),
                item['metadata']['SERNO'],
            ))
            dep_array = item['data']['DEPH'].astype(float)
            # print(item['data'].loc[dep_array < 55., DB_COLUMNS])

            db_hand.post(item['data'].loc[dep_array < 55., DB_COLUMNS])
