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

To do: ligne 113 du code tester l'interrogation de nouvelles adresses de registres pour voir ce que ça donne 
  result = node.readHoldingRegisters(0x0000,4);
  changer l'adresse 0x0000 avec d'autres adresses pour comprendre comment marche la fonction getResponseBuffer

  # extrait du code de la librairy
  https://github.com/jecrespo/RS485_Modbus_Arduino/blob/master/ModBusMaster485/ModbusMaster485.h#L104
  
  @ingroup constant
    */
    static const uint8_t ku8MBInvalidCRC                 = 0xE3;
    
    uint16_t getResponseBuffer(uint8_t);
    void     clearResponseBuffer();
    uint8_t  setTransmitBuffer(uint8_t, uint16_t);
    void     clearTransmitBuffer();

  16/12/2024
  To be able to communicate via the PC and windows to the probe, you must load the passerail.ino code on the device and then open modbus tester program to send commandes. Today we managed to get a code on this page
  http://4-20ma.io/ModbusMaster/examples_2_r_s485__half_duplex_2_r_s485__half_duplex_8ino-example.html#a7 
  we then adapted it to adress 0x0000 of the probe and the register 0x02 for T°C and 0x03 for the DO. DO values remain 0.01 and perhaps this is due to a bad calibration. We will try to sort that out.
  Connecting the probe and receiving data using modbus protocol and linux machine. Use mbpoll tool and run the following command as a first test:
  */
  mbpoll -a 55 -b 9600 -t 4 -r 3 -c 1 -d 8 -P none /dev/ttyUSB0;

  Careful: run 
  lsusb
  sudo dmesg | grep tty 

  This will help you identify to witch usb port your device is connected on your computer

Explanation of Each Parameter

    -a 55: Sets the Modbus slave address to 55.
    -b 9600: Sets the baud rate to 9600.
    -t 2: Specifies holding registers (Modbus function code 03). Change this if accessing a different register type:
        -t 3: Input registers (function code 04).
        -t 1: Coil (discrete outputs).
        -t 0: Discrete input.
    -r 3: Start reading from register address 3.
    -c 1: Read 1 register.
    -d 8: Sets data bits to 8.
    -P none: No parity.
    /dev/ttyUSB0: Specifies the serial port.

17/12/2024
If you want to get the ID number of your device which accordinf to the manual is at the adress 0x2000 (42001), first step is to convert 0x2000 form hexadcimal to decimal:
that gives 8192dec.
Then use this command 
mbpoll -a 55 -m rtu -b 9600 -d 8 -s 1 -P none -o 1 -r 8192 -0 -t 4 /dev/ttyUSB0

19/12/2024
We have managed to send a modbus command to change the device ID woth modbustester.exe. Modbus Poll soft for windows is interesting to see the hexadecimal command sent but we have not managed to send any command with this soft. No Rx message is visible in the communication window.
Be careful, you must write the address of the buffer you want to read/write in decimal format in modbus-tester.

Today, we also managed to identify the list of addresses available using the scan addresses tool from modbus poll soft. We also managed to calibrate the temperature sensor using modbus tester and sending 172 to address 0x1000 which means force the temp sensor to 17.2 °C.
We also managed to calibrate the DO sensor doing the slope protocol. First immerse the probe 10 cm away from the bottom in a big becher filled with tap water + sodium sulphite anhydrous to kill all dissolved oxygen an the send value 0 to address 0x1001. Second step (order of steps is important), immerse the probre 10 cm away from bottom in becher filled with tap water and perform a 100% calibration by sending 0 to address 0x1003.

