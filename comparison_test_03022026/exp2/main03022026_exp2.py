#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 10:44:30 2026

@author: epoirier
"""

'''
adjusting DO probe S/N 25082804
from comparison experiment
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import date, time, datetime

import seeedpy

############################################################################################################
# raw_data
ref_csv = 'WTW_ref_data.CSV'
instru_txt = 'SEEEDProbe_raw_data.csv'


# Read the csv/txt files of the ref and instru to compare and create a df for each
dfr = seeedpy.read_wtw_file_from_multi3630(ref_csv)
dfi = seeedpy.read_seeed_py_logging(instru_txt)


# Plot ref and instru variables of interest on the same graph
# before ploynomial correction
# DO (mg/L)
liste = seeedpy.plot_ref_instru(    
    
    # palier
    datetime(2026, 2, 3, 14,55,0),
    datetime(2026, 2, 3, 15,30,0),
    
    dfr,
    'Value',
    'WTW DO(mg/L)',
    dfi,
    'DO',
    'SeeedStudio probe DO(mg/L)',
    '2026-02-03, Comparison test WTW against SeeedStudio S/N 25082804',
    'Time(HL)',
    'DO(mg/L)')



#### Polyfit

# Exemple d'utilisation avec des données fictives
if __name__ == "__main__":
    # Génération de données simulées
    # np.random.seed(42)
    # dfr = pd.DataFrame({'reference': np.linspace(0, 10, 50)})
    # dfi = pd.DataFrame({'instrument': dfr['reference'] + np.random.normal(0, 0.5, size=50)})
    
    
    
    # Calibration
    coeffs, df_calibrated, r2 = seeedpy.calibrate_sensor(liste[0], liste[1], 'Value', 'DO', degree=2)
    
    # Affichage des résultats
    plt.scatter(df_calibrated['DO'], df_calibrated['Value'], label="Données brutes", color='red')
    plt.scatter(df_calibrated['DO'], df_calibrated['calibrated'], label="Données calibrées", color='blue')
    plt.xlabel("Sonde brute")
    plt.ylabel("Sonde de référence")
    plt.legend()
    plt.title(f"Calibration de la sonde avec un polynôme de degré 3 (R²={r2:.4f})")
    plt.show()
    
    print("Coefficients du polynôme d'ajustement:", coeffs)
    print(f"Coefficient de détermination R²: {r2:.4f}")

#plot de contrôle



# Plot ref and instru variables of interest on the same graph
# DO (mg/L)
seeedpy.plot_ref_instru(    
    
    # palier
    datetime(2026, 2, 3, 14,55,0),
    datetime(2026, 2, 3, 15,30,0),
    
    dfr,
    'Value',
    'WTW DO(mg/L)',
    df_calibrated,
    'calibrated',
    'SeeedStudio probe DO(mg/L)',
    '2026-02-03, post-calibration SeeedStudio S/N 25082804',
    'Time(HL)',
    'DO(mg/L)')


'''
# DO saturation (%)
plot_ref_instru(
    
    
    datetime(2025, 3, 4, 10,3,0),
    datetime(2025, 3, 4, 12,15,0),
    
    
    
    dfr,
    'Value',
    'WTW DO sat(%)',
    dfi,
    'DO_satur',
    'SeeedStudio probe DO saturation(%)',
    '2025-03-04, Comparison test WTW against SeeedStudio S/N 24100906',
    'Time(HL)',
    'DO saturation(%)')
'''

'''

# DO probe temp (°C)
plot_ref_instru(
      
    # total
    datetime(2025, 2, 27, 16,20,0),
    datetime(2025, 2, 27, 16,58,0),

    
    dfr,
    'Value2',
    'WTW Temp (°C)',
    dfi,
    'temperature',
    'SeeedStudio probe Temperature (°C)',
    '2025-01-14, Comparison test WTW against SeeedStudio S/N 24100906',
    'Time(HL)',
    'Temperature(°C)')

'''

