#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 14:46:18 2025

@author: epoirier
"""

# Program to manipulate and communicate with SeeedStudio DO optical sensor
# Needs either a USB-RS485 converter or a microcontroller programmed as passthrough
# J Flye-Sainte-Marie
# 03/2025


#!/usr/bin/env python3

import serial
import minimalmodbus
from time import sleep
from datetime import datetime

client1 = minimalmodbus.Instrument('/dev/ttyUSB0', 1, debug=False)  # port name, slave address (in decimal)
client1.serial.baudrate = 9600  # baudrate
client1.serial.bytesize = 8
client1.serial.parity = serial.PARITY_NONE
client1.serial.stopbits = 1
client1.serial.timeout = 0.1  # seconds
client1.address = 55  # this is the slave address number
client1.mode = minimalmodbus.MODE_RTU  # RTU or ASCII mode
client1.clear_buffers_before_each_transaction = True

sleep(1)

def read_sensor():
    """
    Read temperature, DO, and oxygen saturation values.
    Returns a list with:
    - temperature x 10
    - DO x 100
    - Sat x 10
    """
    return client1.read_registers(256, 3)

def correct_oxy_sens_values(oxy_sens_values):
    """
    Converts raw values read from the SeeedStudio DO sensor
    - temperature (divided by 10),
    - dissolved oxygen (DO, divided by 100),
    - oxygen saturation (SatO2, divided by 10).
    """
    Temp = oxy_sens_values[0] / 10  # Convert temp
    DO = oxy_sens_values[1] / 100   # Convert DO
    SatO2 = oxy_sens_values[2] / 10  # Convert oxygen saturation
    return [Temp, DO, SatO2]

def format_to_write(to_format):
    """
    Formats converted SeeedStudio DO sensor values for saving in file.
    """
    return f"{to_format[0]};°C;{to_format[1]};mg/L;{to_format[2]};%"

while True:
    sens_values = read_sensor()
    corrected_values = correct_oxy_sens_values(sens_values)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line_to_write = f"{timestamp};{format_to_write(corrected_values)}\n"
    print(line_to_write.strip())  # Print to console
    
    with open("datalog.csv", "a") as f:
        f.write(line_to_write)
    
    sleep(1)
