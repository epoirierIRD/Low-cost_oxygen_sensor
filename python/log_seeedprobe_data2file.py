#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 11:54:23 2025

@author: epoirier
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 10:00:04 2025

@author: epoirier1
"""
# Be careful to import pyserial module
import serial
import time

# Configure serial connection
serial_port = '/dev/ttyUSB0'  # Replace with your Arduino's port
baud_rate = 9600      # Match the baud rate with Arduino
output_file = 'temperature_log.txt'

# Open serial connection
try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        print(f"Connected to {serial_port} at {baud_rate} baud.")
        print("Logging data. Press Ctrl+C to stop.")

        # Open the file for appending
        with open(output_file, 'a', encoding='utf-8', newline='\n') as file:
            while True:
                # Read a line from the serial port
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        # Get current timestamp
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        # Format the log entry
                        log_entry = f"{timestamp}, {line}"
                        print(log_entry)  # Display in the console
                        # Write to file
                        file.write(log_entry + '\n')
                        file.flush()  # Ensure data is written immediately
except serial.SerialException as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("\nLogging stopped. Exiting.")
 