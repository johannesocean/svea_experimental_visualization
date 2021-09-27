# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-12-15 13:59

@author: johannes
"""
import pandas as pd
import numpy as np


class NumpyReaderBase:
    """Numpy Base Reader."""

    def __init__(self):
        """Initialize."""
        super().__init__()

    @staticmethod
    def read(*args, **kwargs):
        """Return data from numpy.loadtxt()."""
        return np.loadtxt(*args, **kwargs)


class PandasReaderBase:
    """Pandas Base Reader."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__()

    def get(self, item):
        """Return value for "item"."""
        if item in self.__dict__.keys():
            return self.__getattribute__(item)
        else:
            print('Warning! Can´t find attribute: %s' % item)
            return 'None'

    @staticmethod
    def read(*args, **kwargs):
        """Return data from pd.read_csv()."""
        return pd.read_csv(*args, **kwargs).fillna('')


class NoneReaderBase:
    """Dummy base."""

    def __init__(self):
        """Initialize."""
        super().__init__()

    @staticmethod
    def read(*args, **kwargs):
        """Read."""
        print('Warning! No data was read due to unrecognizable reader type')


def text_reader(reader_type, *args, **kwargs):
    """Dynamic text reader.

    Args:
        reader_type (str): decides what type of reader base to be used.
        *args: args to pass on to reader.
        **kwargs: kwargs to pass on to reader.
    """
    if reader_type == 'pandas':
        base = PandasReaderBase
    elif reader_type == 'numpy':
        base = NumpyReaderBase
    else:
        base = NoneReaderBase

    class TextReader(base):
        """Reader who inherits from the selected reader_type (base)."""

        def __init__(self):
            """Initialize."""
            super().__init__()

    tr = TextReader()
    return tr.read(*args, **kwargs)
