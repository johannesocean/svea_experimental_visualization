# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-23 14:44

@author: johannes
"""
import os
from pathlib import Path


class Config:
    """Settings class."""

    def __init__(self, data_file_name=None):
        """Initialize."""
        self.config_directory = Path(os.path.dirname(os.path.realpath(__file__)))
        self.base_directory = Path(self.config_directory).parents[0]
        self.data_folder = Path.joinpath(self.base_directory, 'test_data')
        self.export_folder = Path.joinpath(self.base_directory, 'exports')
        self.data_file_name = data_file_name

    def get_data_path(self, path=None):
        """Return path to data."""
        if self.data_file_name:
            return Path.joinpath(self.data_folder, self.data_file_name)
        else:
            return Path.joinpath(self.data_folder, path)

    def get_export_path(self):
        """Return path for data export."""
        if not os.path.exists(self.export_folder):
            os.mkdir(self.export_folder)
        return self.export_folder

    @property
    def data_path(self):
        """Return path to data."""
        if self.data_file_name:
            return self.get_data_path()
        else:
            return None

    @property
    def export_path(self):
        """Return path for data export."""
        return self.get_export_path()
