#include <ModbusMaster.h>  // Inclure la bibliothèque ModbusMaster

#define MAX485_DE      3
#define MAX485_RE_NEG  2

// Créer une instance de l'objet ModbusMaster
ModbusMaster node;

void preTransmission() {
  digitalWrite(MAX485_RE_NEG, 1);
  digitalWrite(MAX485_DE, 1);
}

void postTransmission() {
  digitalWrite(MAX485_RE_NEG, 0);
  digitalWrite(MAX485_DE, 0);
}

void setup() {
  pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);

  // Initialisation en mode réception pour RS485
  digitalWrite(MAX485_RE_NEG, 0);
  digitalWrite(MAX485_DE, 0);

  // Initialisation du port série pour le débogage
  Serial.begin(9600);
  while (!Serial) {
    ; // Attendre la connexion série (nécessaire pour certaines cartes)
  }

  // Initialisation de Serial1 pour la communication Modbus
  Serial1.begin(9600);

  // Initialisation de la communication Modbus
  node.begin(55, Serial1); // ID de l'esclave 55
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);

  Serial.println("Communication Modbus initialisée.");
}

void loop() {
  uint8_t result;
  float temperature = 0.0;
  float DO_value = 0.0;
  float DO_saturation = 0.0;

  // Lire la température à l'adresse 0x0100
  result = node.readHoldingRegisters(0x0100, 1);  // Adresse 0x0100
  if (result == node.ku8MBSuccess) {
    temperature = node.getResponseBuffer(0x00) / 10.0f; // En Celsius
  } else {
    Serial.println("Erreur lors de la lecture de la température");
  }

  // Lire la valeur DO à l'adresse 0x0101 (DO en mg/L)
  result = node.readHoldingRegisters(0x0101, 1);  // Adresse 0x0101
  if (result == node.ku8MBSuccess) {
    DO_value = node.getResponseBuffer(0x00) / 100.0f;  // En mg/L
  } else {
    Serial.println("Erreur lors de la lecture de DO");
  }

  // Lire la valeur DO saturée à l'adresse 0x0102
  result = node.readHoldingRegisters(0x0102, 1);  // Adresse 0x0102
  if (result == node.ku8MBSuccess) {
    DO_saturation = node.getResponseBuffer(0x00) / 100.0f;  // En mg/L
  } else {
    Serial.println("Erreur lors de la lecture de DO saturé");
  }


  // Afficher les données dans le moniteur série
  Serial.print("Température: ");
  Serial.print(temperature);
  Serial.print("°C, DO: ");
  Serial.print(DO_value);
  Serial.print("mg/L, DO Saturé: ");
  Serial.print(DO_saturation);
  Serial.println("%");

  // Attendre avant la prochaine lecture
  delay(1000);  // Ajuster le délai si nécessaire
}

