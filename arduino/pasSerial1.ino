void setup() {
//Communicate with PC through USB to UART, use Serial to call
Serial.begin(9600);
//Use Serial1 to call the serial UART of TXD and RXD marked on the development board
Serial1.begin(9600);
}

void loop() {
  if (Serial.available()) 
    Serial1.write(Serial.read());
  if (Serial1.available())
    Serial.write(Serial1.read());
}