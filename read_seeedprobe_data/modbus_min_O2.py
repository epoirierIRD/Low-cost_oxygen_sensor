# Program to manipulate communicate with seeedstudion DO optical sensor
# Needs either a USB-RS485 converter or a microcontroller programmed as passthrougth 
# J Flye-Sainte-Marie 
# 03/2025


#!/usr/bin/env python3

import serial
import minimalmodbus
from time import sleep
from datetime import datetime
from datetime import datetime


client1 = minimalmodbus.Instrument('/dev/ttyUSB0', 1, debug=False)  # port name, slave address (in decimal)
client1.serial.baudrate = 9600  # baudrate
client1.serial.bytesize = 8
client1.serial.parity   = serial.PARITY_NONE
client1.serial.stopbits = 1
client1.serial.timeout  = 0.1      # seconds
client1.address         = 55        # this is the slave address number
client1.mode = minimalmodbus.MODE_RTU # rtu or ascii mode
client1.clear_buffers_before_each_transaction = True
#
sleep(1)


def read_raw_values():
	"""
	
	"""
	return client1.read_registers(0, 4)

def read_sensor():
	"""
	Read temperature, DO, ans Oxygen saturations values
	
	Return a list with:
	- temperature x 10
	- DO x 100
	- Sat x 10
	
	"""
	return client1.read_registers(256, 3)
	



def correct_oxy_sens_values(oxy_sens_values):
	"""
	Converts raw values readen from the seeedstudio DO sensor
	- temperature (divided by 10),
	- dissolved oxygen (DO, divided by 100),
	- oxygen saturation (SatO2, divided by 100).

	Parameters:
	oxy_sens_values (list): A list of sensor values. The list must contain at least 3 elements.
	        [Temp, DO, SatO2].

	Returns:
	list: A list containing the formatted values [Temp, DO, SatO2], all divided by their respective factors.

	"""
	
	Temp = oxy_sens_values[0] / 10  # Convert temp
	DO = oxy_sens_values[1] / 100   # Convert DO
	SatO2 = oxy_sens_values[2] / 10  # Convert oxygen saturation
	return [Temp, DO, SatO2]
    
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

	
def calibrate_100() :
	"""
	Calibration of the 100% saturation in air-saturated water,
	returns calibration slope 	
	"""
	client1.write_register(4099, 0, number_of_decimals=0, functioncode=6)
	return client1.read_registers(4099, 1)[0]/100

def calibrate_0() :
	"""
	Calibration of the 0% in anaerobic water (you can use sodium sulfilte in water),
	returns  the 0 offset
	Note that after zero calobration the sensor will always return a 0.04mg/L value of DO (and 0.4% saturation)
	
	"""
	client1.write_register(4097, 0, number_of_decimals=0, functioncode=6)
	return client1.read_registers(4097, 1)[0]

def calibrate_temp(temp_cal) : 
	"""
	Temperature calibration
	
	Parameter :
	Temperature of the calibration solution
	
	Returns the calibration offset
	
	When calibrating in solution, the written data is the actual temperature value × 10;
	the read data is the temperature calibration offset × 10.
	"""
	client1.write_register(4096, temp_cal*10, number_of_decimals=0, functioncode=6)
	sleep(1)
	return client1.read_registers(4096, 1)[0]/10


def set_sensor_add(address) :
	"""
	Set sensor Modbus adress
	
	Parameter:
	Modbus adress from 1 to 127, default is 55
	 
	"""
	if 1 <= address <= 127:
		print(f"Adress {address} is valid.")
		client1.write_register(8192, address, number_of_decimals=0, functioncode=6)
	else :
		print(f"Adresse {address} is invalid.")
	


def reset_sensor():
	"""
	Reset sensor 
	
	The calibration value is restored to the default value.
	Note: After the sensor is reset, it needs to be calibrated again before it can be used
	 
	"""
	client1.write_register(8224, 0, number_of_decimals=0, functioncode=6)


def set_baudrate(baudrate):
	"""
	Set sensor communication baudrate
	
	The default value is 9600. Write 0 to 4800; Write 1 to 9600; Write 2 to 19200
	
	Note that the modification will only take effect after restaring the sensor
	
	Warning : if you use a microcontroller to get data form the sensor take care to 
	set adequate microcontroller baudrate communication with sensor 

	"""
	if baudrate == 4800 : 
		client1.write_register(8195, 0, number_of_decimals=0, functioncode=6)
		print('done')
	elif baudrate == 9600:
	  	client1.write_register(8195, 1, number_of_decimals=0, functioncode=6)
	elif baudrate == 19200 :
	  	client1.write_register(8195, 2, number_of_decimals=0, functioncode=6)
	else :
		print(f"Baudrate {baudrate} is invalid.")
	sleep(1)
	print(client1.read_registers(8195, 1))
	
#set_baudrate(9600)
	
#reset_sensor()

#set_sensor_add(55)

#toto = calibrate_temp(22)
#print("calibration slope is " + str(toto))


#toto = calibrate_100()
#print("calibration slope is " + str(toto))


#toto = calibrate_0()
#print("zero offset is " + str(toto))

#sleep(1)



while True : 
	sens_values = read_sensor()  # Registernumber, number of decimals
	print(format_oxy_sens_values(correct_oxy_sens_values(sens_values)))
	line_to_write = datetime.now().strftime("%m/%d/%Y %H:%M:%S")+ ";" + format_to_write(correct_oxy_sens_values(sens_values)) +"\n"
	#print(line_to_write)
	with open("datalog.csv", "a") as f:
   		f.write(line_to_write)
	sleep(1)







