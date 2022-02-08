#!/usr/bin/env python3
"""
Created on 2022-01-11 13:47

@author: johannes
"""
import pandas as pd
import numpy as np
from db_conn import DbHandler

DB_COLUMNS = [
    'timestamp', 'KEY', 'STATN', 'LATIT', 'LONGI', 'DEPH', 'CPHL', 'Q_CPHL'
]


def strip_mon_day(x):
    return x[:4] + x[10:]


if __name__ == '__main__':
    db_hand = DbHandler(table='btl')
    df = pd.read_feather('phyche_archive_2020.feather')

    df_filtered = df.loc[~df['CPHL'].isnull(), :]
    df_filtered['KEY'] = df_filtered['KEY'].apply(strip_mon_day)
    df_filtered['Q_CPHL'] = ''

    db_hand.post(df_filtered[DB_COLUMNS])
