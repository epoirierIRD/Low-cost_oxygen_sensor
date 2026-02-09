#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 14:46:18 2025

@author: epoirier
"""
import time
from time import sleep
from datetime import datetime
import seeedpy_rd

'''This program is to read seevral DO probe sensors
with theri addresses list
apply polynomila correction to DO concentration and log in a chosen csv
file at a chosen interval
the data:
    datetime, addresss, Temp, DO_raw, DO_corr, Sat for each sensor
    fo the list
'''


#%%
# Main
# Modbus addresses of probes to log
addresses = [3, 4]
clients = {}
port = '/dev/ttyUSB0' #usb port to read
csv_file = "SEEED_DOProbe_raw.csv" #choose your file name
LOG_INTERVAL = 1 # seconds

# polynomial coeffs correction for DO concentration
# each client/slave address has its own polynomial coefficients
coeffs_per_address = {
    1: [1,0],  # coeffs [1,0] = no polynomial correction
    2: [1,0],
    3: [1,0], #sensor 25082803
    4: [0.04579253, 0.53543994, 0.21359762], #sensor 25082804
    5: [1,0]
}

# Creating the clients
for addr in addresses:
    clients[addr] = seeedpy_rd.create_client(port, addr)

sleep(1)

# automatic logging in csv file  
while True:
        
    for addr, client in clients.items():
        try:
            # read raw sensor values
            sens_values =  seeedpy_rd.read_sensor(client)
            
            # get the polynomila coeffs
            coeffs = coeffs_per_address[addr]
            
            # correct raw values
            corrected_values =  seeedpy_rd.correct_oxy_sens_values(sens_values, coeffs)
            
            #timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # log to csv
            seeedpy_rd.log_to_csv(csv_file, timestamp, addr, corrected_values)
            
            print(f"Client {addr} logged: {corrected_values}")
    
        except Exception as e:
            print(f"Client {addr} read error: {e}")
            
    time.sleep(LOG_INTERVAL)
    








