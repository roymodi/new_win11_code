#include <Arduino.h>

#define INPUT_PIN   14   // e.g. D5 — change to your input pin
#define OUTPUT_PIN  12   // e.g. D6 — the pin that toggles

// Function A – runs when input is HIGH
void functionA() {
  Serial.println("Input HIGH -> Function A running");
  digitalWrite(OUTPUT_PIN, LOW);  // Make sure output is off
}

// Function B – runs when input is LOW (10s on, 15s off loop)
void functionB() {
  static unsigned long lastToggle = 0;
  static bool outputState = false;
  static bool initialized = false;

  // Run initialization once when entering low mode
  if (!initialized) {
    Serial.println("Input LOW -> Function B active");
    lastToggle = millis();
    outputState = false;
    digitalWrite(OUTPUT_PIN, LOW);
    initialized = true;
  }

  unsigned long currentMillis = millis();

  // ON for 10 sec, OFF for 15 sec
  if (outputState && (currentMillis - lastToggle >= 10000)) {
    outputState = false;
    digitalWrite(OUTPUT_PIN, LOW);
    lastToggle = currentMillis;
    Serial.println("Output OFF");
  } else if (!outputState && (currentMillis - lastToggle >= 15000)) {
    outputState = true;
    digitalWrite(OUTPUT_PIN, HIGH);
    lastToggle = currentMillis;
    Serial.println("Output ON");
  }

  // If input goes high again, reset
  if (digitalRead(INPUT_PIN) == HIGH) {
    initialized = false;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(INPUT_PIN, INPUT);     // or INPUT_PULLUP if using pull-up
  pinMode(OUTPUT_PIN, OUTPUT);
  digitalWrite(OUTPUT_PIN, LOW);
  Serial.println("ESP-12F RTC Control Ready");
}

void loop() {
  if (digitalRead(INPUT_PIN) == HIGH) {
    functionA();
  } else {
    functionB();
  }
}
