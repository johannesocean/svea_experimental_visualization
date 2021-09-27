#!/usr/bin/env python3
# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-09-24 11:10

@author: johannes
"""
import json


def load_json(file_path):
    """Load and return json data."""
    with open(file_path, 'r') as fd:
        data = json.load(fd)
    fd.close()
    return data
