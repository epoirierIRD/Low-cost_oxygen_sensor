
#include <ModbusMaster.h>
#include <SPI.h>
#include <SD.h>
#include "RTClib.h" // this to pilot the DS1307
//#include <Ds1302.h>
//Ds1302 rtc(5, 7, 6);
//RTC_DS1307 rtc;
//include <virtuabotixRTC.h> this was activated when using the RTC provided in the report 

File myFile;


// Pin donde se conecta el bus 1-Wire

/*!
  We're using a MAX485-compatible RS485 Transceiver.
  Rx/Tx is hooked up to the hardware serial port at 'Serial'.
  The Data Enable and Receiver Enable pins are hooked up as follows:
*/
float TempC;
float Oxy;
#define MAX485_DE      3
#define MAX485_RE_NEG  2

// instantiate ModbusMaster object
ModbusMaster node;
//virtuabotixRTC now(7, 6, 5);
//pinMode(LED_BUILTIN, OUTPUT);

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

  // Modbus communication runs at 115200 baud
  Serial.begin(115200);
  Serial1.begin(9600);

   while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

 /* Serial.print("Initializing SD card...");
  if (!SD.begin(53)) {
    Serial.println("initialization failed!");
    
  }*/

  /*  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    Serial.flush();
    while (1) delay(10);
  }

 if (! rtc.isrunning()) {
    Serial.println("RTC is NOT running, let's set the time!");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
  }*/


    //rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    //rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
//now.setDS1302Time(00, 49, 7, 6, 19, 4, 2024);

/*
  myFile = SD.open("CURSO.txt", FILE_WRITE);
  if (myFile) {
    Serial.println("FECHA,HORA,TEMP...");
    myFile.println("FECHA,HORA,TEMP");
    // close the file:
    myFile.close();
    Serial.println("done.");
  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening test.txt");
  }
  */

  // Modbus slave ID 1
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
   
  // readHoldingRegisters es el codigo de funcion es decir 03, (con 4 registros)
  result = node.readHoldingRegisters(0x0000,4);
  state = !state;

  //Serial.println(result);
  //Serial.println("antes");
  //Serial.println(node.ku8MBSuccess);
  if (result == node.ku8MBSuccess)
  {
    TempC = node.getResponseBuffer(0x02)/100.0f;
    TempC = 10*TempC;
    Serial.print("Temperatura: ");
    //Serial.println(node.getResponseBuffer(0x02)/100.0f);
    Serial.println(TempC);

    Oxy = node.getResponseBuffer(0x00);
    Oxy = Oxy/100;
    Serial.print("Oxigeno: ");
    //Serial.println(node.getResponseBuffer(0x00)/100.0f);
    Serial.println(Oxy);

// Vamos a realizar las granbaciones al SD card
//now.updateTime();    
//DateTime now = rtc.now();
/*myFile = SD.open("CURSO.txt", FILE_WRITE);
if (myFile) {
    Serial.print(now.year, DEC);
    myFile.print(now.year, DEC);
    Serial.print('-');
    myFile.print('-');
    Serial.print(now.month, DEC);
    myFile.print(now.month, DEC);
    Serial.print('-');
    myFile.print('-');
    Serial.print(now.dayofmonth, DEC);
    myFile.print(now.dayofmonth, DEC);
    Serial.print(',');
    myFile.print(',');
    Serial.print(now.hours, DEC);
    myFile.print(now.hours, DEC);
    Serial.print(':');
    myFile.print(':');
    Serial.print(now.minutes, DEC);
    myFile.print(now.minutes, DEC);
    Serial.print(':');
    myFile.print(':');
    Serial.print(now.seconds, DEC);
    myFile.print(now.seconds, DEC);
    Serial.print(',');
    myFile.print(',');
    myFile.print(TempC);
    myFile.print(',');
    myFile.println(Oxy);
    // close the file:
  }
myFile.close();
*/
  delay(1000);
}
}
