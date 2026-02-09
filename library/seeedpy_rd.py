#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Library to manipulate and communicate with SeeedStudio DO optical sensor
# and lof the data to csv
# Needs either a USB-RS485 converter or a microcontroller programmed as passthrough
# J Flye-Sainte-Marie, E. Poirier
# 02/2026

import serial
import minimalmodbus
import numpy as np
import csv
import os
from time import sleep

#%% 
# function to create a client. To be done for each probe.
def create_client(port, slave_address):
    client = minimalmodbus.Instrument(port, slave_address, debug=False)

    client.serial.baudrate = 9600
    client.serial.bytesize = 8
    client.serial.parity = serial.PARITY_NONE
    client.serial.stopbits = 1
    client.serial.timeout = 0.1

    client.address = slave_address
    client.mode = minimalmodbus.MODE_RTU # RTU or ASCII mode
    client.clear_buffers_before_each_transaction = True

    return client

#%%
# Function to access diffrent registers on the probes

def read_sensor(client):
    """
    Read temperature, DO, and oxygen saturation values for client.
    Returns a list with:
    - temperature x 10
    - DO x 100
    - Sat x 10
    """
    return client.read_registers(256,3)


def read_raw_values(client):
	"""
	
	"""
	return client.read_registers(0, 4)
	
    
def format_oxy_sens_values(to_format) :
	"""
	Formats converted seeedstudio DO sensor values for display
	
	"""
	return "Temp:" + str(to_format[0])+ "°C, DO: " + str(to_format[1]) + "mg/L, Sat: " + str(to_format[2]) + '%'
	
def format_to_write(to_format):
	"""
	Formats converted seeedstudio DO sensor values for saving in file
		
	"""
	return str(to_format[0]) + ";°C;" + str(to_format[1]) + ";mg/L;" + str(to_format[2]) + ';%;'

	
def calibrate_100(client) :
	"""
	Calibration of the 100% saturation in air-saturated water,
	returns calibration slope 	
	"""
	client.write_register(4099, 0, number_of_decimals=0, functioncode=6)
	return client.read_registers(4099, 1)[0]/100

def calibrate_0(client) :
	"""
	Calibration of the 0% in anaerobic water (you can use sodium sulfilte in water),
	returns  the 0 offset
	Note that after zero calobration the sensor will always return a 0.04mg/L value of DO (and 0.4% saturation)
	
	"""
	client.write_register(4097, 0, number_of_decimals=0, functioncode=6)
	return client.read_registers(4097, 1)[0]

def calibrate_temp(client, temp_cal) : 
	"""
	Temperature calibration
	
	Parameter :
	Temperature of the calibration solution
	
	Returns the calibration offset
	
	When calibrating in solution, the written data is the actual temperature value × 10;
	the read data is the temperature calibration offset × 10.
	"""
	client.write_register(4096, temp_cal*10, number_of_decimals=0, functioncode=6)
	sleep(1)
	return client.read_registers(4096, 1)[0]/10


def set_sensor_add(client, address) :
	"""
	Set sensor Modbus adress
	
	Parameter:
	Modbus adress from 1 to 127, default is 55
	 
	"""
	if 1 <= address <= 127:
		print(f"Adress {address} is valid.")
		client.write_register(8192, address, number_of_decimals=0, functioncode=6)
	else :
		print(f"Adresse {address} is invalid.")
	

def reset_sensor(client):
	"""
	Reset sensor 
	
	The calibration value is restored to the default value.
	Note: After the sensor is reset, it needs to be calibrated again before it can be used
	 
	"""
	client.write_register(8224, 0, number_of_decimals=0, functioncode=6)


def set_baudrate(client, baudrate):
	"""
	Set sensor communication baudrate
	
	The default value is 9600. Write 0 to 4800; Write 1 to 9600; Write 2 to 19200
	
	Note that the modification will only take effect after restaring the sensor
	
	Warning : if you use a microcontroller to get data form the sensor take care to 
	set adequate microcontroller baudrate communication with sensor 

	"""
	if baudrate == 4800 : 
		client.write_register(8195, 0, number_of_decimals=0, functioncode=6)
		print('done')
	elif baudrate == 9600:
	  	client.write_register(8195, 1, number_of_decimals=0, functioncode=6)
	elif baudrate == 19200 :
	  	client.write_register(8195, 2, number_of_decimals=0, functioncode=6)
	else :
		print(f"Baudrate {baudrate} is invalid.")
	sleep(1)
	print(client.read_registers(8195, 1))


# %%
# functions to write and correct
def correct_oxy_sens_values(oxy_sens_values, coeffs):
    """
    Converts raw values read from the SeeedStudio DO sensor
    - temperature (divided by 10),
    - dissolved oxygen (DO, divided by 100),
    - oxygen saturation (SatO2, divided by 10).
    - applies polynomial correction with coeffs provided
    """
    Temp = oxy_sens_values[0] / 10  # Convert temp
    DO = oxy_sens_values[1] / 100   # Convert DO
    SatO2 = oxy_sens_values[2] / 10  # Convert oxygen saturation
    
    # Apply polynomial correction
    DO_corr = float(round(np.polyval(coeffs, DO), 2)) # for 2 decimals python float
    
    return [Temp, DO, DO_corr, SatO2]


def log_to_csv(csv_file, timestamp, client_addr, values):
    """
    values = [Temp, DO, DO_corr, SatO2]
    """
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode="a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "client_address",
                "temperature_C",
                "do_raw_mgL",
                "do_corrected_mgL",
                "saturation_percent"
            ])

        writer.writerow([
            timestamp,
            client_addr,
            *values
        ])

# %% TEST THE FUNCTIONS

#set_baudrate(9600)
	
#reset_sensor()

# set_sensor_add(4)

#toto = calibrate_temp(22)
#print("calibration slope is " + str(toto))


#toto = calibrate_100()
#print("calibration slope is " + str(toto))


#toto = calibrate_0()
#print("zero offset is " + str(toto))

#sleep(1)
