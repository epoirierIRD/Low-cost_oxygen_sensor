#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 10:34:59 2026

@author: epoirier
"""

'''
List of functions for the processing of seeed DO probe data
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import date, time, datetime
import matplotlib.dates as mdates
#from fpdf import FPDF
import os
from io import StringIO
import re
from numpy.polynomial.polynomial import Polynomial
from sklearn.metrics import r2_score



# %%
def read_wtw_file_from_multi3630(ref_csv):
    '''
    parser to read the wtw data outputted on you USB stick
    from WTW Multi360 console

    Parameters
    ----------
    ref_csv : string 
        your raw WTW data file

    Returns
    -------
    df : pandas dataframe
        datetime as index + all columns from source csv with names

    '''

    # Read the data using pandas
    df = pd.read_csv(
    ref_csv, 
    sep=";", 
    encoding='ISO-8859-1'
    # na_values=["no_data"],  # Treat 'no_data' as NaN
    # header = 0,
    )
    # Convert the 'Date/Time' column to datetime format
    df['Date/Time'] = pd.to_datetime(df['Date/Time'], format='%d.%m.%Y %H:%M:%S')

    # Set the 'Date/Time' column as the index
    df.set_index('Date/Time', inplace=True)

    # Optional: Reformat the index to 'YYYY-MM-DD HH:MM:SS' if needed
    df.index = df.index.strftime('%Y-%m-%d %H:%M:%S')
    
    # give date time format to index again
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d %H:%M:%S')

    return df
# %%
def read_seeed_py_logging(input_file_path):
    '''
    Read the file with SEEED data logged from program modbus_minO2 with datetime

    Parameters
    ----------
    input_file_path : string
        SEEED DO probe raw data file logged with python program 
        modbus_min_O2_with_datetime.py

    Returns
    -------
    datframe with datetime as index + temp, DO concentration, DO_satur

    '''
   
    df = pd.read_csv(
        input_file_path,
        sep=";",
        header=None,
        names=[
            "datetime",
            "temperature", "temp_unit",
            "DO", "DO_unit",
            "DO_satur", "satur_unit"
        ]
    )
    
    # Convert datetime column
    df["datetime"] = pd.to_datetime(df["datetime"])
    
    # Convert the 'timestamp' column to datetime format
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
    
    # Assign timestamp column as Index
    df.set_index('datetime', inplace = True)
    
    # Keep only the columns you want
    df = (df[["temperature", "DO", "DO_satur"]])
    
    return(df)
# %%

def plot_ref_instru(start, stop, dfr, varr, labelr, dfi, vari, labeli, title, xlabel, ylabel):
    '''
    plot the ref and instru data without aligning the time indexes
    Plot one column data of each data frame dfr and dfi on the same graph
    
    Args:
        start (dt): datetime object start of period of interest
        stop (dt): datetime object stop of period of interest
        dfr (df): dataframe of ref data
        varr (str): the column name in the dfr to plot
        labelr (str): serie label of the ref
        dfi (df): dataframe of instru to examine
        vari (str): the column name of interest in the dfi
        labalei (str): serie label of the instrument variable 
        title(str): title of graph
        xlabel(str): label of x axis
        ylabel(str): label of y axis   
        
    '''
    # Cut the dataframes to keep only the period of interest
    dfr = dfr[(dfr.index >= start) & (dfr.index <= stop)]
    dfi = dfi[(dfi.index >= start) & (dfi.index <= stop)]
    
    # Plot both DataFrames using the datetime index
    plt.figure(figsize=(10, 6))


    # Plot DataFrame ref 
    plt.scatter(dfr.index, dfr[varr], label= labelr, color="blue", marker="o")
    
    # Plot DataFrame instru to evaluate
    plt.plot(dfi.index, dfi[vari], label= labeli, color="orange", marker="x")
    
    # Add labels, legend, and grid
    plt.title(title)
    plt.xlabel(xlabel)
    # Format the x-axis to show date and time. Ligne importante sinon les heures affichees sont fausses
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    #plt.ylabel(ylabel)
    plt.legend()
    #plt.grid()
    
    # Show plot
    plt.show()
    
    # Return Dfr
    return [dfr,dfi]

#%%

def plot_ref_instru_aligned(start, stop, dfr, varr, labelr, dfi, vari, labeli, title, xlabel, ylabel):
    '''
    Plot instru data versus ref data
    Args:
        start (dt): datetime object start of period of interest
        stop (dt): datetime object stop of period of interest
        dfr (df): dataframe of ref data
        varr (str): the column name in the dfr to plot
        labelr (str): serie label of the ref
        dfi (df): dataframe of instru to examine
        vari (str): the column name of interest in the dfi
        labalei (str): serie label of the instrument variable 
        title(str): title of graph
        xlabel(str): label of x axis
        ylabel(str): label of y axis   

    Returns
    -------
    None.

    '''
                            
    # Cut the dataframes to keep only the period of interest
    dfr = dfr[(dfr.index >= start) & (dfr.index <= stop)]
    dfi = dfi[(dfi.index >= start) & (dfi.index <= stop)]
    # merge on oxygen
    merged = dfr[[varr]].join(
    dfi[[vari]],
    how='inner'
    )
    plt.figure()
    plt.scatter(merged[varr], merged[vari])
    plt.xlabel(labelr)
    plt.ylabel(labeli)
    plt.title('SEEED DO Probe vs WTW ref data')
    plt.show()
    
    
    #plot a van de casteele like graph
    merged['diff'] = merged[vari]-merged[varr]
        
    plt.figure()
    plt.scatter(merged['diff'], merged[varr])
    plt.xlabel('Instrument minus Reference Oxygen')
    plt.ylabel('Reference Oxygen')
    plt.title('Oxygen Bias Plot')
    plt.axvline(0)  # zero-bias line
    plt.show()


# %%

def calibrate_sensor(dfr, dfi, ref_col, inst_col, degree=1):
    """
    fonction pour l'ajustement polynomial from chatgpt
    Calibre une sonde de moins bonne qualité en ajustant un polynôme
    pour correspondre aux données de référence.
    
    Paramètres:
    - dfr : DataFrame contenant les données de référence
    - dfi : DataFrame contenant les données de l'instrument à calibrer
    - ref_col : Nom de la colonne contenant les valeurs de référence
    - inst_col : Nom de la colonne contenant les valeurs à corriger
    - degree : int, degré du polynôme (3 ou 4 recommandé)
    
    Retourne:
    - coeffs : coefficients du polynôme d'ajustement
    - calibrated_values : valeurs ajustées selon le polynôme
    - r2 : coefficient de détermination R²
    """
    # Fusionner les DataFrames sur les index (ou une clé commune si nécessaire)
    df = pd.merge(dfr, dfi, left_index=True, right_index=True)
    
    # Extraire les valeurs
    reference = df[ref_col].values
    measured = df[inst_col].values
    
    # Ajustement du polynôme
    coeffs = np.polyfit(measured, reference, degree)
    poly = np.poly1d(coeffs)
    df['calibrated'] = poly(measured)
    
    # Calcul du R²
    r2 = r2_score(reference, df['calibrated'])
    
    return coeffs, df, r2


