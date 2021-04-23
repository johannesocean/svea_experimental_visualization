# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-23 14:44
@author: johannes
"""
import os
from pathlib import Path


class Config:
    def __init__(self, data_file_name=None):
        self.config_directory = Path(os.path.dirname(os.path.realpath(__file__)))
        self.base_directory = Path(self.config_directory).parents[0]
        self.data_folder = Path.joinpath(self.base_directory, 'test_data')
        self.data_file_name = data_file_name

    def get_data_path(self, path=None):
        if self.data_file_name:
            return Path.joinpath(self.data_folder, self.data_file_name)
        else:
            return Path.joinpath(self.data_folder, path)
    
    @property
    def data_path(self):
        if self.data_file_name:
            return self.get_data_path()
        else:
            return None
