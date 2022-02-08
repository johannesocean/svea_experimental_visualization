#!/usr/bin/env python3
"""
Created on 2022-01-11 16:12

@author: johannes
"""
import matplotlib.pyplot as plt
import seaborn as sns
# sns.set_theme()
sns.set(style="white")
from interpolate import interpolate_array
from db_conn import DbHandler

DB_COLUMNS_CTD = [
    'timestamp', 'KEY', 'STATN', 'LATIT', 'LONGI', 'DEPH',
    'CHLFLUO_CTD', 'PHYC_CTD'
]
DB_COLUMNS_BTL = [
    'timestamp', 'KEY', 'STATN', 'LATIT', 'LONGI', 'DEPH',
    'CPHL', 'Q_CPHL'
]


def get_nearest_depth_indices(in_array, search_array):
    """Doc."""
    return in_array.searchsorted(search_array)


if __name__ == '__main__':
    db_hand = DbHandler(table='btl', parameter='KEY')
    test_key = '2020_77SE_0357'

    keys_btl = db_hand.get_unique_parameter_data()

    for key in keys_btl['KEY']:
        print(key)
        key_btl_data = db_hand.get_data_for_key(key, table='btl')

        db_hand.update_attributes(table='ctd')
        key_ctd_data = db_hand.get_data_for_key(key)
        if key_ctd_data.empty:
            continue

        matching_idx = get_nearest_depth_indices(
            key_ctd_data['DEPH'], key_btl_data['DEPH']
        )

        ctd_selected = key_ctd_data['CHLFLUO_CTD'][matching_idx]
        bias = key_btl_data['CPHL'].values - ctd_selected.values

        interp_depth, interp_bias = interpolate_array(
            key_btl_data['DEPH'].values,
            bias, key_ctd_data['DEPH'].values
        )

        interp_depth_biasC, interp_biasC = interpolate_array(
            key_btl_data['DEPH'].values,
            key_btl_data['CPHL'].values,
            key_ctd_data['DEPH'].values
        )

        bias_corrected_A = key_ctd_data['CHLFLUO_CTD'].values + bias.mean()
        bias_corrected_B = key_ctd_data['CHLFLUO_CTD'].values + interp_bias
        # bias_corrected_C = key_ctd_data['CHLFLUO_CTD'].values * (interp_biasC / key_ctd_data['CHLFLUO_CTD'].values)
        bias_corrected_C = key_ctd_data['CHLFLUO_CTD'].values * (key_btl_data['CPHL'].values.mean() / key_ctd_data['CHLFLUO_CTD'].values.mean())
        rolling = key_ctd_data['CHLFLUO_CTD'].rolling(10, min_periods=3, center=True)
        # bias_corrected_D

        fig, ax = plt.subplots(figsize=(5, 7))
        ax.plot(key_btl_data['CPHL'], key_btl_data['DEPH'], 'ko', label='BTL-CPHL')
        ax.plot(key_ctd_data['CHLFLUO_CTD'], key_ctd_data['DEPH'], 'r-', label='CTD-FLUO')
        ax.plot(bias_corrected_A, key_ctd_data['DEPH'], 'g-', label='FLUO-BIAS-A')
        ax.plot(bias_corrected_B, key_ctd_data['DEPH'], 'b-', label='FLUO-BIAS-B')
        ax.plot(bias_corrected_C, key_ctd_data['DEPH'], 'c-', label='FLUO-BIAS-C')
        ax.invert_yaxis()
        ax.grid()
        # plt.xlim(0, 15)
        plt.ylabel('Depth (m)')
        plt.xlabel('Chl a / Chl fluo')
        plt.title(key)
        plt.legend()
        plt.savefig('bias_ctd_vs_btl/{}.png'.format(key))
        plt.close()
        # break