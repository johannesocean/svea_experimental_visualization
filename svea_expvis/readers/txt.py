# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-12-15 13:59

@author: johannes

"""
import pandas as pd
import numpy as np


class NumpyReaderBase:
    def __init__(self):
        super().__init__()

    @staticmethod
    def read(*args, **kwargs):
        return np.loadtxt(*args, **kwargs)


class PandasReaderBase:
    def __init__(self, *args, **kwargs):
        super().__init__()

    def get(self, item):
        if item in self.__dict__.keys():
            return self.__getattribute__(item)
        else:
            print('Warning! Can´t find attribute: %s' % item)
            return 'None'

    @staticmethod
    def read(*args, **kwargs):
        return pd.read_csv(*args, **kwargs).fillna('')


class NoneReaderBase:
    """
    Dummy base
    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def read(*args, **kwargs):
        print('Warning! No data was read due to unrecognizable reader type')


def text_reader(reader_type, *args, **kwargs):
    """
    Dynamic text reader.
    :param reader_type: str, decides what type of reader base to be used.
    :param args: iterable
    :param kwargs: dict
    :return:
    """
    if reader_type == 'pandas':
        base = PandasReaderBase
    elif reader_type == 'numpy':
        base = NumpyReaderBase
    else:
        base = NoneReaderBase

    class TextReader(base):
        """
        """
        def __init__(self):
            super().__init__()

    tr = TextReader()
    return tr.read(*args, **kwargs)
