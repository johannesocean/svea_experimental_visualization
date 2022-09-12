#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-06-02 10:16

@author: johannes
"""
from svea_expvis.config import Config
import numpy as np
import pandas as pd
import gsw
import cmocean
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="white")
# sns.set(style="dark")
# sns.set_style("white", {"axes.facecolor": "grey"})


cfig = Config(
    data_file_name='phyche_archive_2018-2022.feather'
)

PARAMETERS = ['CPHL', 'FLUO_CTD', 'SUN_ANGLE', 'SEA']


fig_types = [
    {
        'booleans': {'dep5'},
        'label': 'dep<=5',
        'title': 'All stations',
        'fig_name': 'all_dep5.png'
    },
    {
        'booleans': {'angle_extreams'},
        'label': 'sun_angle>40 or <-40',
        'title': 'All stations',
        'fig_name': 'all_angle_extreams.png'
    },
    {
        'booleans': {'dep5', 'angle_extreams'},
        'label': 'dep<=5; sun_angle>40 or <-40',
        'title': 'All stations',
        'fig_name': 'all_dep5_angle_extreams.png'
    },
    {
        'booleans': {'dep5', 'west'},
        'label': 'dep<=5',
        'title': 'West sea stations',
        'fig_name': 'west_dep5.png'
    },
    {
        'booleans': {'angle_extreams', 'west'},
        'label': 'sun_angle>40 or <-40',
        'title': 'West sea stations',
        'fig_name': 'west_angle_extreams.png'
    },
    {
        'booleans': {'dep5', 'angle_extreams', 'west'},
        'label': 'dep<=5; sun_angle>40 or <-40',
        'title': 'West sea stations',
        'fig_name': 'west_dep5_angle_extreams.png'
    },
    {
        'booleans': {'dep5', 'baltic'},
        'label': 'dep<=5',
        'title': 'Baltic sea stations',
        'fig_name': 'baltic_dep5.png'
    },
    {
        'booleans': {'angle_extreams', 'baltic'},
        'label': 'sun_angle>40 or <-40',
        'title': 'Baltic sea stations',
        'fig_name': 'baltic_angle_extreams.png'
    },
    {
        'booleans': {'dep5', 'angle_extreams', 'baltic'},
        'label': 'dep<=5; sun_angle>40 or <-40',
        'title': 'Baltic sea stations',
        'fig_name': 'baltic_dep5_angle_extreams.png'
    },
]


if __name__ == '__main__':
    df = pd.read_feather(cfig.data_path)

    for item in fig_types:
        boolean = df['CPHL'].notna() & df['FLUO_CTD'].notna()
        if 'dep5' in item['booleans']:
            boolean = boolean & (df['DEPH'] <= 5.)
        if 'west' in item['booleans']:
            boolean = boolean & (df['SEA'] == 'WEST_SEA')
        if 'baltic' in item['booleans']:
            boolean = boolean & (df['SEA'] == 'BALTIC_PROPER')
        if 'angle_extreams' in item['booleans']:
            boolean = boolean & ((df['SUN_ANGLE'] > 40) | (df['SUN_ANGLE'] < -40))
        df_patch = df.loc[boolean, PARAMETERS].reset_index(drop=True)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        sc = ax.scatter(
            df_patch['CPHL'], df_patch['FLUO_CTD'],
            c=df_patch['SUN_ANGLE'],
            norm=None,
            vmin=-55, vmax=55,
            cmap=cmocean.cm.thermal,
            s=1, zorder=2,
            label=item['label']
        )
        plt.title(item['title'])
        min_of_max = min([df_patch['CPHL'].max(), df_patch['FLUO_CTD'].max()])
        ax.plot([0, min_of_max], [0, min_of_max], '--k', lw=.3, label='1:1')

        cbar = plt.colorbar(sc)
        cbar.set_label('Altitude of the sun (degrees)')

        ax.set_xlabel('Bottle chlorophyll a (µg/l)')
        ax.set_ylabel('CTD chlorophyll fluorescence (au)')
        ax.legend(loc='upper left')

        plt.savefig(item['fig_name'], dpi=300)
