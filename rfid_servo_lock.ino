#include <SPI.h>
#include <MFRC522.h>
#include <ESP32Servo.h>

// RC522 connections
#define SS_PIN   5
#define RST_PIN  22

// Servo connection
#define SERVO_PIN 13

MFRC522 rfid(SS_PIN, RST_PIN);
Servo myServo;

bool cardHandled = false;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Initialize RFID reader
  SPI.begin(18, 19, 23, SS_PIN);
  rfid.PCD_Init();

  // Initialize servo
  myServo.setPeriodHertz(50);
  myServo.attach(SERVO_PIN, 500, 2500);
  myServo.write(0);

  Serial.println("ESP32 RFID Door Lock Ready");
  Serial.println("Scan your ID card...");
}

void loop() {
  // Rearm after the card is removed
  if (!rfid.PICC_IsNewCardPresent()) {
    cardHandled = false;
    return;
  }

  if (cardHandled) {
    return;
  }

  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  cardHandled = true;

  // Print card UID
  Serial.println();
  Serial.println("ID CARD DETECTED!");

  Serial.print("UID: ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) {
      Serial.print("0");
    }
    Serial.print(rfid.uid.uidByte[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  // Turn servo to 180 degrees
  Serial.println("Servo moving to 180 degrees...");
  myServo.write(180);
  delay(2000);

  // Return servo to 0 degrees
  Serial.println("Servo returning to 0 degrees...");
  myServo.write(0);

  Serial.println("Ready for next card.");

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  delay(500);
}
