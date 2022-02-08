# -*- coding: utf-8 -*-
"""
Created on 2019-12-05 14:25

@author: a002028

"""
import numpy as np
from scipy import interpolate


def interpolate_array(x, y, x_long, smooth_rate=100):
    """Doc."""
    interp_obj = interpolate.PchipInterpolator(x, y)
    # new_x = np.linspace(x[0], x[-1], smooth_rate)
    new_y = interp_obj(x_long)
    return x_long, new_y
