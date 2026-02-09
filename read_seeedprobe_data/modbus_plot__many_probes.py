#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 10:57:48 2026

@author: epoirier
"""

import seeedpy_plt

seeedpy_plt.plot_DO_probes(
    'SEEED_DOProbe_raw.csv',
    sensors=[3, 4],
    value_col='do_corrected_mgL')
    