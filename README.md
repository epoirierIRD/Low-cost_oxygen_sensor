# Low-cost DO oxygen sensor from SEEED Studio, Senscap

This project starts with a first objective: to interface a SEEED studio low-cost oxygen probe and verify its metrologic specs. It means calibrate the probe and check its performances regarding the manufacturer specs and a referenc
optode on at least 3 levels: 0% stauration O2, 50% and 100%.

- First step is to interface this RS485 probe to a computer and get decent data
- Post-it for connecting probe cables on UART gravity module DFR0845
* Probe red cable: 12V
* Probe black cable : GND
* Probe blue cable : A
* Probe withe cable : B
  
## 12/12/202, problem found bad DO reading output in arduino serial monitor
This the problem we face:
We first test the code Oxigeno_LowCost_G1_RTC_V1.ino provided that comes from our mexican friends and collects the temperature and dissolved oxygen.
We have commented the parts concerning the timing of the data and the saving on SD card.
However it remains a problem as the oxygen values are not correct. This is a reading with 115200 baud rate

```
Temperatura: 17.20;
Oxigeno: 0.01;
Temperatura: 17.20;
Oxigeno: 0.02;
```
This is the first problem to fix.


## 13/12/2024, understanding the CRC code ending a modbus command and managing to generate it (not useful at the moment) 
We are now able to produce the CRC code (hex) ending a modbus command line. It is a 4 digits code XX XX in hexadecimal with low-byte first. It is done thanks to the python code provided by chatgpt.

To do: ligne 113 du code tester l'interrogation de nouvelles adresses de registres pour voir ce que ça donne 
  result = node.readHoldingRegisters(0x0000,4);
  changer l'adresse 0x0000 avec d'autres adresses pour comprendre comment marche la fonction getResponseBuffer

  ### extrait du code de la librairy
  https://github.com/jecrespo/RS485_Modbus_Arduino/blob/master/ModBusMaster485/ModbusMaster485.h#L104

  ```
  @ingroup constant
    */
    static const uint8_t ku8MBInvalidCRC                 = 0xE3;
    
    uint16_t getResponseBuffer(uint8_t);
    void     clearResponseBuffer();
    uint8_t  setTransmitBuffer(uint8_t, uint16_t);
    void     clearTransmitBuffer();
  ```

 ## 16/12/2024, talking to your device with linux and mbpoll cmd lines (free soft)
**To be able to communicate via the PC and windows to the probe, you must load the passerail.ino code on the device and then open modbus tester program to send commandes. Otherwise the port remains busy.** Today we managed to get a code on this page
http://4-20ma.io/ModbusMaster/examples_2_r_s485__half_duplex_2_r_s485__half_duplex_8ino-example.html#a7 
we then adapted it to adress 0x0000 of the probe and the register 0x02 for T°C and 0x03 for the DO. DO values remain 0.01 and perhaps this is due to a bad calibration. We will try to sort that out.
Connecting the probe and receiving data using modbus protocol and linux machine. Use mbpoll tool and run the following command as a first test:
  ```console
  mbpoll -a 55 -b 9600 -t 4 -r 3 -c 1 -d 8 -P none /dev/ttyUSB0;
  ```
  Careful: run 
  ```console
  lsusb
  sudo dmesg | grep tty
  ```
  This will help you identify to witch usb port your device is connected on your computer

 Explanation of Each Parameter (extract from Chatgpt)
 ```
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
```

## 17/12/2024, mbpoll getting reading single register, device ID successfull
If you want to get the ID number of your device which accordinf to the manual is at the adress 0x2000 (42001), first step is to convert 0x2000 form hexadcimal to decimal:
that gives 8192dec.
Then use this command 
```console
mbpoll -a 55 -m rtu -b 9600 -d 8 -s 1 -P none -o 1 -r 8192 -0 -t 4 /dev/ttyUSB0
```

## 19/12/2024, modbustester succeed to write to register. Modbus poll.exe helps finfind the register list, calibration achieved in T and DO
Success: We have managed to send a modbus command to change the device ID with modbustester.exe. 
Modbus Poll soft for windows is interesting to see the hexadecimal command sent but we have not managed to send any command with this soft. No Rx message is visible in the communication window.
Be careful, you must write the address of the buffer you want to read/write in decimal format in modbus-tester.

Insert image here

Today, we also managed to identify the list of addresses available using the scan addresses tool from modbus poll soft. 
We also managed to calibrate the temperature sensor using modbus tester and sending 172 to address 0x1000 which means force the temp sensor to 17.2 °C.
We also managed to calibrate the DO sensor doing the slope protocol. 
- First immerse the probe 10 cm away from the bottom in a 1L beaker filled with tap water + sodium sulphite anhydrous to kill all dissolved oxygen an then send value 0 to address 0x1001.
- Second step **(order of steps is important)**, immerse the probre 10 cm away from bottom in becher filled with tap water and perform a 100% calibration by sending 0 to address 0x1003.
**Finally, the DO values outputted in arduino serial monitor remain at 0.01 which is not satisfying. We must dig into that. We suspect a dysfunctionning of the DO readings of the probe. To be examinated after the holidays.**

## 20/12/2024, trying to install node-red to read data from modbus device
I got help from RTCE forum regarding this task.
Check the topic here: https://rtce.forum.inrae.fr/t/communication-rs485-modbus-rtu-seeed-studio-dissolved-oxygen-probe/319/4?u=poirier_etienne1
Emmanuel Landrivon recommends using node-red (open-source) to communicate with the DO Probe through a USB<->RS485 adapter. Node-red is a tool to produce code via a graphic interface. Supposed to be easier for beginners like me. So I will try using node red to read/write the buffers of my DO Probe.
Eventually I will interface my device via node red to an ESP32 firebeetle via Tasmota (+ module RS485) :https://tasmota.github.io/docs/Modbus-Bridge/
So that's the plan, let's dive into it:

###Installing node red on linux/debian/ubuntu:
- First install nvm (Node version manager). nvm is a tool that can help manage Node.js installations.
  Check this page: https://nodejs.org/en/download/package-manager/
  
```Bash
# installs nvm (Node Version Manager). 
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# download and install Node.js (you may need to restart the terminal)
nvm install 22

# verifies the right Node.js version is in the environment
node -v # should print `v22.12.0`

# verifies the right npm version is in the environment
npm -v # should print `10.9.0`
```
Don't forget now to source the bashrc file to be able to activate nvm command

```Bash
source /home/epoirier/.bashrc
```
The previous installation of nvw installed v12 version which is not enough. Upgrade to nvm v18 version (at least, v20 available too) to be able to run node red.

```Bash
nvm install v18
```
You are now goo to run node red command:
```Bash
node-red
```
If at this step, it says ''node-red function nor found'', it means perhaps that you did not have npm and nvm installed, so check that they are installed and run again the code block ''Installing node red on linux/debian/ubuntu:''

1. Verify Node.js Installation

Node-RED depends on Node.js. Check if Node.js is installed and its version:
```Bash
node -v
```
If you see an error or the version is below the required version (typically Node.js 14.x or higher), you’ll need to install or update Node.js.

Install Node.js (Latest LTS version):
```Bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

Verify npm:
```Bash
npm -v
```

If npm is missing, install it:
```Bash
sudo apt install npm
```

2. Install Node-RED

Once Node.js and npm are set up, install Node-RED globally using npm:
```Bash
sudo npm install -g --unsafe-perm node-red
```

Check if Node-RED was installed:
```Bash
node-red -v
```

Your node red is now running in your terminal.
Supposing that your are working locally on your laptop for this first test, go to your web browser and type http://localhost:1880 to access the node red editor.
You will get this page in your web browser.

![screenshot](Imagefolder/node-red.png)

However, if you miss the modbus command function on the left panel. Quit Node-RED and execute this command in your terminal:
```Bash
npm install node-red-contrib-modbus
```
Check the page for modbus package installation in Node-red: https://flows.nodered.org/node/node-red-contrib-modbus
Start again your node-RED and begin creating your first flow.
It seems that the modbus nodes don't show up in the Palette. So on your web interface go to Manage Palette/Palette/Install
and choose: node-red-contrib-modbus
Check this page for more details: https://flowfuse.com/node-red/protocol/modbus/




Please check-out this page regarding node red and nvm installation on linux debian: 
https://nodered.org/docs/getting-started/local
https://nodered.org/docs/faq/node-versions

## 07/01/2025, node-red working to read data from the sensor

Working on node-red the 20/12/2024, 06/01 and 07/01/2025, I managed to get it working on my laptop (running Ubuntu) and my desk computer running ubuntu too.
Below is the picture of my first flow (flux-1.json) to be found in the github files and user interface created with it.

![screenshot](Imagefolder/flux-1.png)
![screenshot](Imagefolder/flux-1_ui.png)


However I had to face seberal problems which I will try to present her.

### Insert an image in node-red dashboard (or ui, standing for user interface)

If you want to insert an image in node-red dashboard as per the image of my probe, you must first do that:
```Bash
# go to the location of your node-red server
cd ~/.node-red
# create a public directory to put your images
mkdir ~/.node-red/public
# put your image in /public
cp mylocation/image.jpg ~/.node-red/public
# edit the settings.js file to tell node-red where you store your images
vim  ~/.node-red/settings.js
```
In this file settings.js, go to this line
```js
// httpStatic: '/home/nol/node-red-static/', //single static source
```
Add a new line below telling that your image will be in public
```js
httpStatic: require('path').join(__dirname, 'public'),
```
Restart node-red.

### Solving a cyclic dependency issue in Node.js

If for some reasons your nodes modbus read become stuck on waiting status. Also when running red-node on your console, you have this error message:
```bash
Error: Circular config node dependency detected: modbus-client
    at Flow.start (/usr/local/lib/node_modules/node-red/node_modules/@node-red/runtime/lib/flows/Flow.js:227:43)
```
You won't go anywhere else until you solve the issue on the modbus-client. My solution is to remove the old client and create a new one.

### Modbus reader node reconnecting (status yellow)

Don't use the same Poll rate for each modbus read node. It may create a connection issue to poll data at the same time. Choose diffrent rates such as 1s, 2s, 3s, etc...

## 07/01/2025, node-red flow2 finished. Looking good

I managed to finish flow 2 integrating the write registers nodes to be able to calibrate the probe.
I have done a gross calibration and well try now to test the accuracy of the probe.
Flow 2 is to be found under node-red folder and is nammed flow2-do_probe.json.
![screenshot](Imagefolder/flow-2_ui.png)

## 09/01/2025, meeting with jonathan flye sainte-marie

When showing him the node-red flow I realize that the temperature looks wrong: 23°C instead of 19°C expected.
Moreover the saturation of DO is 0.1% so wrong.
Instructions from Jonathan to continue the project are:
* validate or not the quality of the sensor in term of metrology. First get a fast response from the sensor. In fact node-red flow is very slow
at the moment. Perhaps I am not interrogating the right adresses. It takes time when calibrating the sensor temp for example and the DO value is not responding fast.
* for autonomous deployment. Plan is to integrate the sensor on OSO CTD P2I instead of the cond. sensor.
So the aim is to be able to interface the sensor with arduino and build a code for the OSO to work with the sensor.
Jonathan has bought a thread tap G3/4 to connect the sensor to a waterproof logger using à O ring seal.
the goal is to talk with it with a code on a ESP32.
* create a python library to talk with the sensor using python code. Building a library is new to me. There wuld functions as
  start DO, get DO, get temp, calDO,....

## 13/01/2025, calibration test in lab

### Problem to be solved on probe S/N 24000304
I tested the calibration of the current probe (I gave it the S/N 24000304, because of what I read at addresses 0x2004 and 0x2005). **But it does not accept the 100% saturated water cal. It gives 0.1% saturation instead.** Perhaps there is a x100 issue to solve??

### Calibration success on probe S/N 24100906
However I also tested the calibration using the same node-red flow on the new probe given by Jonathan. It works fine besides a few things:
* Response time very long on temeprature value (perhaps because the probe is not fully submerged. It takes 1-2 min for the sensor to converge to the true temperature. Offset corrected on tempertaure sensor is 0.2, 0.3°C. After a stabilization, probe temperature is near ref temperature +/- 0.1°C.
* We did a 100% saturated water cal on the new probe (S/N graved on probe housing: S/N24100906) and it worked fine
* we did then a 0% cal and it outputted 0.1% which is good.
* There was a mistake on mg/L DO value red in the node-red flow. We were reading the wrong address. It is solved now on flow 3.
* We managed in flow 3 to have all the modbus read nodes at 1s rate

  ![screenshot](Imagefolder/flow3_100percent_probe906.png)

### Increasing the data rate, logging the data
* modpoll tests output the data at 1s rate
* according to jonathan, mexicans managed to logged the data on sd card, they managed to get the data from the sensor at a best rate that what we get with the node-red interface
* An idea is to use modpoll command and python to talk to the sensor. Good, bad?
* An idea is to undersand correctly the modpoll commands to write and read in each register as they seem faster
* An idea is to abandon node-red and migrate to arduino to get better data rate, quicker sensor time response.




