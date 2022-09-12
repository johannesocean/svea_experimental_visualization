#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-06-02 10:16

@author: johannes
"""
from svea_expvis.config import Config
import numpy as np
from scipy import stats
import pandas as pd
import gsw
import cmocean
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="white")
# sns.set(style="dark")
# sns.set_style("white", {"axes.facecolor": "grey"})


def r2(x, y):
    return stats.pearsonr(x, y)[0] ** 2


def linreg_eq_data(x, y):
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    y_max = x.max() * slope + intercept
    y_min = x.min() * slope + intercept
    eq = 'y = {}x {} {}'.format(
        round(slope, 3),
        '+' if intercept > 0 else '-',
        abs(round(intercept, 3))
    )
    values = (slope, intercept, r_value, p_value, std_err)
    return ([x.min(), x.max()], [y_min, y_max]), eq, values


cfig = Config(
    data_file_name='phyche_archive_2018-2022.feather'
)

PARAMETERS = ['CPHL', 'FLUO_CTD', 'DEPH', 'SEA']

fig_types = [
    {
        'booleans': {''},
        'label': 'all',
        'title': 'All stations',
        'fig_name': 'all.png'
    },
    {
        'booleans': {'winter'},
        'label': 'winter',
        'title': 'All stations - winter',
        'fig_name': 'all_winter.png'
    },
    {
        'booleans': {'spring'},
        'label': 'spring',
        'title': 'All stations - spring',
        'fig_name': 'all_spring.png'
    },
    {
        'booleans': {'summer'},
        'label': 'summer',
        'title': 'All stations - summer',
        'fig_name': 'all_summer.png'
    },
    {
        'booleans': {'autumn'},
        'label': 'autumn',
        'title': 'All stations - autumn',
        'fig_name': 'all_autumn.png'
    },
    {
        'booleans': {'west'},
        'label': 'all',
        'title': 'West sea stations',
        'fig_name': 'west.png'
    },
    {
        'booleans': {'west', 'winter'},
        'label': 'winter',
        'title': 'West sea stations - winter',
        'fig_name': 'west_winter.png'
    },
    {
        'booleans': {'west', 'spring'},
        'label': 'spring',
        'title': 'West sea stations - spring',
        'fig_name': 'west_spring.png'
    },
    {
        'booleans': {'west', 'summer'},
        'label': 'summer',
        'title': 'West sea stations - summer',
        'fig_name': 'west_summer.png'
    },
    {
        'booleans': {'west', 'autumn'},
        'label': 'autumn',
        'title': 'West sea stations - autumn',
        'fig_name': 'west_autumn.png'
    },
    {
        'booleans': {'baltic'},
        'label': 'all',
        'title': 'Baltic sea stations',
        'fig_name': 'baltic.png'
    },
    {
        'booleans': {'baltic', 'winter'},
        'label': 'winter',
        'title': 'Baltic sea stations - winter',
        'fig_name': 'baltic_winter.png'
    },
    {
        'booleans': {'baltic', 'spring'},
        'label': 'spring',
        'title': 'Baltic sea stations - spring',
        'fig_name': 'baltic_spring.png'
    },
    {
        'booleans': {'baltic', 'summer'},
        'label': 'summer',
        'title': 'Baltic sea stations - summer',
        'fig_name': 'baltic_summer.png'
    },
    {
        'booleans': {'baltic', 'autumn'},
        'label': 'autumn',
        'title': 'Baltic sea stations - autumn',
        'fig_name': 'baltic_autumn.png'
    },
]


if __name__ == '__main__':

    stats_dict = {k: [] for k in (
        'fig_name', 'slope', 'intercept', 'R_value', 'p_value', 'std_err'
    )}

    df = pd.read_feather(cfig.data_path)

    for log_bool in (True, False):
        for dep_itv in ('', '0-5', '0-10', '20-50'):
            for sun_angle in ('', '>30', '<-30'):
                for item in fig_types:
                    boolean = df['CPHL'].notna() & df['FLUO_CTD'].notna()
                    if 'west' in item['booleans']:
                        boolean = boolean & (df['SEA'] == 'WEST_SEA')
                    if 'baltic' in item['booleans']:
                        boolean = boolean & (df['SEA'] == 'BALTIC_PROPER')
                    if 'winter' in item['booleans']:
                        boolean = boolean & df['timestamp'].dt.month.isin([12, 1, 2])
                    if 'spring' in item['booleans']:
                        boolean = boolean & df['timestamp'].dt.month.isin([3, 4, 5])
                    if 'summer' in item['booleans']:
                        boolean = boolean & df['timestamp'].dt.month.isin([6, 7, 8])
                    if 'autumn' in item['booleans']:
                        boolean = boolean & df['timestamp'].dt.month.isin([9, 10, 11])
                    if sun_angle == '>30':
                        boolean = boolean & (df['SUN_ANGLE'] > 30)
                    if sun_angle == '<-30':
                        boolean = boolean & (df['SUN_ANGLE'] < -30)
                    if dep_itv == '0-5':
                        boolean = boolean & (df['DEPH'] <= 5)
                    if dep_itv == '0-10':
                        boolean = boolean & (df['DEPH'] <= 10)
                    if dep_itv == '20-50':
                        boolean = boolean & (df['DEPH'] >= 20)
                    df_patch = df.loc[boolean, PARAMETERS].reset_index(drop=True)
                    if not df_patch.size:
                        continue
                    if log_bool:
                        df_patch['CPHL'] = np.log10(df_patch['CPHL'])
                        df_patch['FLUO_CTD'] = np.log10(df_patch['FLUO_CTD'])

                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    r, p = stats.pearsonr(df_patch['CPHL'], df_patch['FLUO_CTD'])
                    p = '< 0.05' if p < 0.05 else str(p)

                    linregs, eq, stat_values = linreg_eq_data(
                        df_patch['CPHL'], df_patch['FLUO_CTD'])
                    stats_text = 'R={:.2f}, p={}\n{}'.format(r, p, eq)

                    ax.plot(*linregs, '-r', lw=.7, label=stats_text, zorder=3)
                    data_label = item['label']
                    if sun_angle:
                        data_label += f'; sun_angle: {sun_angle}'
                    if dep_itv:
                        data_label += f'; depth_itv: {dep_itv}'

                    sc = ax.scatter(
                        df_patch['CPHL'], df_patch['FLUO_CTD'],
                        c=df_patch['DEPH'],
                        norm=None,
                        vmin=0, vmax=50,
                        cmap=cmocean.cm.thermal,
                        s=1, zorder=2,
                        label=data_label
                    )
                    plt.title(item['title'])
                    max_of_max = max([df_patch['CPHL'].max(), df_patch['FLUO_CTD'].max()])
                    min_of_min = min([df_patch['CPHL'].min(), df_patch['FLUO_CTD'].min()])
                    ax.plot([min_of_min, max_of_max], [min_of_min, max_of_max], '--k', lw=.3, label='1:1')

                    axis_max = max_of_max * 1.05
                    axis_min = min_of_min * .95 if min_of_min > 0 else min_of_min * 1.05
                    ax.set_xlim([axis_min, axis_max])
                    ax.set_ylim([axis_min, axis_max])

                    cbar = plt.colorbar(sc)
                    cbar.set_label('Depth (m)')

                    ax.set_xlabel('Bottle chlorophyll a (µg/l)')
                    ax.set_ylabel('CTD chlorophyll fluorescence (au)')
                    ax.legend(loc='upper left')
                    degree = 'hi' if sun_angle == '>30' else 'lo'
                    fig_name = item['fig_name']
                    if sun_angle:
                        fig_name = fig_name.replace('.png',
                                                    f'_sun_angle_{degree}.png')
                    if dep_itv:
                        fig_name = fig_name.replace('.png',
                                                    f'_dep_itv_{dep_itv}.png')
                    if log_bool:
                        fig_name = fig_name.replace('.png', '_logged.png')

                    stats_dict['fig_name'].append(fig_name)
                    for key, value in zip(('slope', 'intercept', 'R_value', 'p_value', 'std_err'), stat_values):
                        stats_dict[key].append(round(value, 4))
                    plt.savefig(fig_name, dpi=300)
                    plt.close(fig)

    pd.DataFrame(stats_dict).to_excel(
        'stats_table.xlsx',
        sheet_name='statistics',
        header=True,
        index=False,
    )


# df = pd.read_excel(
#     r'C:\Utveckling\svea_experimental_visualization\examples\stats_table.xlsx',
#     sheet_name='statistics'
# )
#
# original_header = df.columns.to_list()
#
# extra_columns = {
#     'area': ['baltic', 'west'],
#     'season': ['winter', 'spring', 'summer', 'winter'],
#     'sun_angle': ['angle_lo', 'angle_hi'],
#     'depth_interval': ['_0-5', '0-10', '20-50'],
#     'logged': ['logged']
# }
# df[list(extra_columns)] = 'all'
#
# for col, item in extra_columns.items():
#     for value in item:
#         boolean = df['fig_name'].str.contains(value)
#         if value == '_0-5':
#             value = value.replace('_', '')
#
#         if value == 'logged':
#             df.loc[boolean, col] = 'yes'
#             df.loc[~boolean, col] = 'no'
#         else:
#             df.loc[boolean, col] = value
#
# df[list(extra_columns) + original_header].to_excel(
#     'stats_table.xlsx',
#     sheet_name='statistics',
#     header=True,
#     index=False,
# )