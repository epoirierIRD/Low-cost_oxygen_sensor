#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:44:31 2025

@author: epoirier1
"""


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

# Fonctions called in the main

#parser to read the minidot data coming from epoirierIRD rep github

def readminidot(path, start1, end1):
     
    # args
    # path: path of your file
    # start1 = datetime(2023,5,23,9,30,00); start of period of interest
    # end1 = datetime(2023,5,23,11,25,00); end of period of interest
    
    #output
    # a data frame with the data of the selected period
    
    # ************************************************************************************
    # This code is to read a raw data file recorded by a PME MiniDOT logger
    # It is not made to read a concatenated file 
    # download the file raw_minidot_data.txt from this repo and save it on your machine
    # then put the right path to it in the line path =
    
    # path to the raw data file on your machine
    
    # df is a dataframe created with all the columns from raw_minidot_data.txt
    # careful for row value in header=row. The row counts starts at row 0
    df = pd.read_csv(path, header=2, delimiter=',', index_col=0)
    
    # convert the index times from unix seconds to date time objects with the format AAAA-MM-DD HH:MM:SS
    df.index = pd.to_datetime(df.index, unit='s')
    
    # plot the column number you want to see (watch out, number of first column is 0)
    # [0] column 0 is the battery voltage in Volts
    # [1] column 1 is the dissolved oxygen in mg/l
    # [2] column 2 is the temperature in °C
    df.plot(y=df.columns[2], style='.-', markevery=5)
    
    # show the first lines of the df dataframe
    print(df.head())
    # show the last lines of the df dataframe
    print(df.tail())
    # show the basic statistics of all columns of the dataframe
    print(df.describe())
    
    # ****************************************************************************
    
    # This code is to select a period of the data between tow chosen times
    # It is helpful if you want to "zoom in" on some data of interest
    
    
    # this shorten the df dataframe into a smaller one called dfs
    # containig the data of interest
    dfs = df[start1 : end1]
    # plot your data of interest
    dfs.plot(y=dfs.columns[2], style='.-', markevery=5)
    plt.show()
    
    return dfs


# parser to read the wtw data

def read_wtw_file_from_multi3630(ref_csv):

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

# parser to read the DO probe data from the monitor that were time stamped

def read_raw_seeed_logging(input_file_path):    
    
    """
    Reads a log file coming from arduino serial monitor logged in file via python script, 
    extracts relevant data, and converts it to a CSV file.

    Args:
        input_file_path (str): Path to the input text file containing log data.
    """

    # Define the regular expression for valid data lines
    valid_line_pattern = re.compile(r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), Temp rature: (?P<temperature>[\d.]+) C, DO: (?P<DO>[\d.]+)mg/L, DO Satur : (?P<DO_satur>[\d.]+)%')

    # List to hold parsed data
    data = []

    # Open and read the file
    with open(input_file_path, 'r') as file:
        for line in file:
            # Check if the line matches the valid format
            match = valid_line_pattern.match(line.strip())
            if match:
                # If valid, extract the data and append it to the list
                data.append(match.groupdict())

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data)
    
    # convert columns values from objects to float  
    df = df.astype({'temperature':'float','DO':'float', 'DO_satur':'float'})
    
    # Convert the 'timestamp' column to datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
    
    # Assign timestamp column as Index
    df.set_index('timestamp', inplace = True)
    
    return df

# plot the ref and instru data without aligning the time indexes
def plot_ref_instru(start, stop, dfr, varr, labelr, dfi, vari, labeli, title, xlabel, ylabel):
    '''
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

############################################################################################################

# Main
# exp1
# ref_csv = '/home/epoirier/Documents/Projets/SEEEDstudio_DOProbe/Low-cost_oxygen_sensor/comparison_test_27022025/Exp1/wtw_ref_data.CSV'
# instru_txt = '/home/epoirier/Documents/Projets/SEEEDstudio_DOProbe/Low-cost_oxygen_sensor/comparison_test_27022025/Exp1/SEEEDProbe_raw_data.txt'
# exp2
ref_csv = '/home/epoirier1/Documents/PROJETS/2024/oxygen_probe_seeedstudio/github_project/Low-cost_oxygen_sensor/comparison_test_11032025/wtw_ref_data.CSV'
instru_txt = '/home/epoirier1/Documents/PROJETS/2024/oxygen_probe_seeedstudio/github_project/Low-cost_oxygen_sensor/comparison_test_11032025/seeedprobe_data_exp1.txt'


# Read the csv/txt files of the ref and instru to compare and create a df for each
dfr = read_wtw_file_from_multi3630(ref_csv)
dfi = read_raw_seeed_logging(instru_txt)


# Plot ref and instru variables of interest on the same graph
# DO (mg/L)
plot_ref_instru(    
    
    # 
    datetime(2025, 3, 11, 10,56,0),
    datetime(2025, 3, 11, 11,10,0),
    
    dfr,
    'Value',
    'WTW DO(mg/L)',
    dfi,
    'DO',
    'SeeedStudio probe DO(mg/L)',
    '2025-01-14, Comparison test WTW against SeeedStudio S/N 24100906',
    'Time(HL)',
    'DO(mg/L)')


'''

# DO saturation (%)
plot_ref_instru(
    
    
    datetime(2025, 3, 11, 10,30,0),
    datetime(2025, 3, 11, 11,30,0),
    
    
    
    dfr,
    'Value',
    'WTW DO sat(%)',
    dfi,
    'DO_satur',
    'SeeedStudio probe DO saturation(%)',
    '2025-01-21, Comparison test WTW against SeeedStudio S/N 24100906',
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

