
/*Code below dowloaded from http://4-20ma.io/ModbusMaster/examples_2_r_s485__half_duplex_2_r_s485__half_duplex_8ino-example.html#a7
  and adapted by Etienne Poirier to read seeed studio oxygen probe

  --------------------------------------------------------------------------
  original comment of the code
  --------------------------------------------------------------------------
  RS485_HalfDuplex.pde - example using ModbusMaster library to communicate
  with EPSolar LS2024B controller using a half-duplex RS485 transceiver.
  This example is tested against an EPSolar LS2024B solar charge controller.
  See here for protocol specs:
  http://www.solar-elektro.cz/data/dokumenty/1733_modbus_protocol.pdf
  Library:: ModbusMaster
  Author:: Marius Kintel <marius at kintel dot net>
  Copyright:: 2009-2016 Doc Walker
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/
#include <ModbusMaster.h>
#define MAX485_DE      3
#define MAX485_RE_NEG  2
// instantiate ModbusMaster object
ModbusMaster node;
void preTransmission()
{
  digitalWrite(MAX485_RE_NEG, 1);
  digitalWrite(MAX485_DE, 1);
}
void postTransmission()
{
  digitalWrite(MAX485_RE_NEG, 0);
  digitalWrite(MAX485_DE, 0);
}
void setup()
{
  pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);
  // Init in receive mode
  digitalWrite(MAX485_RE_NEG, 0);
  digitalWrite(MAX485_DE, 0);
  // Modbus communication runs at 115200 baud but our sensor runs at 9600 baud rate by default
  // if we don't write the first line with 115200 it does not work
  // beware of the "1" in Serial1
  // Communicate with PC through USB to UART adapter, use Serail below to call
   Serial.begin(9600);
  // Use Serial1 to call the serial UART of TXD and RXD marked on the dev board
  Serial1.begin(9600);
  while (!Serial)
  {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  
  // Modbus slave ID 1, value 55 is the native slave ID of oxygen probe
  // beware of the '1' in Serial1
  node.begin(55, Serial1);
  // Callbacks allow us to configure the RS485 transceiver correctly
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);
}
bool state = true;
void loop()
{
  uint8_t result;
  uint16_t data[6];  
  /*
  // Toggle the coil at address 0x0002 (Manual Load Control)
  // I believe that this command is to start ON/OFF the sensor
  result = node.writeSingleCoil(0x0002, state);
  state = !state;
  */
  // Read 10 registers of the oxygen probe starting at 0x0000
  result = node.readHoldingRegisters(0x1010, 1);
  state = !state;
  if (result == node.ku8MBSuccess)
  {
    Serial.print("Temperature: ");
    Serial.println(10*node.getResponseBuffer(0x00)/100.0f);
    Serial.print("Oxygen: ");
    Serial.println(node.getResponseBuffer(0x00)/100.0f);
  }
  delay(1000);
}
