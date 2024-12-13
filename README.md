# Low-cost_oxygen_sensor

This project starts with a first objective: to interface a SEEED studio low-cost oxygen probe and verify its metrologic specs.
- first step is to interface this RS485 probe to a computer and get decent data
- At the moment 12/12/2024, this the problem we face:
the code Oxigeno_LowCost_G1_RTC_V1;ino provided that comes from our mexican friends and collects the temperature and dissolved oxygen. We have commented the parts concerning the timing of the data and the saving on SD card.
However it remains a problem as the oxygen values are not correct. This is a reading with 115200 baud rate
Temperatura: 17.20
Oxigeno: 0.01
Temperatura: 17.20
Oxigeno: 0.02
This is the first problem to fix.


13/12/2024 
we are now able to produce the CRC code (hex) ending a modbus command line. It is a 4 digits code XX XX in hexadecimal with low-byte first. It is done thanks to the python code provided by chatgpt.
