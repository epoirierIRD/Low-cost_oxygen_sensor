#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 16:09:02 2025

@author: epoirier1
"""

import numpy as np

# To be used on saturation values only for the moment.

# function to convert raw saturation from SEEED DO probe 24100906 at high sat
# into a correct saturation that fits to WTW ref data
# calculated from 04/03/2025 exp1 laboratory test
# valid on range [13-100%] or [2.7-9.3mg/L]
# coeff are high order first. Last value is the ordinate at the origin

def polySeeed_h (raw_sat):
    
    coeff = np.array([ 1.51007946e-04, -1.61182452e-02,  1.22747443e+00, -1.20492099e+01])
    p = np.poly1d(coeff)
    corr_sat = p (raw_sat)
    return corr_sat

# function to convert raw saturation from SEEED DO probe 24100906 at low sat
# into a correct saturation that fits to WTW ref data
# calculated from 04/03/2025 exp2 laboratory test
# valid on range [0-13%] or [0-2.7mg/L]

def polySeeed_l (raw_sat):
    
    coeff = np.array([0.31717437, 0.90944749])
    p = np.poly1d(coeff)
    corr_sat = p (raw_sat)
    return corr_sat

