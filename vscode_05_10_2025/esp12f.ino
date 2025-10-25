void pinCycleController() {
  static const int outputPin = 2;
  static const unsigned long oneHour = 60UL * 60UL * 1000UL;
  static const unsigned long onTime  = 1UL * oneHour;
  static const unsigned long offTime = 1.5 * oneHour;
  
  static bool initialized = false;
  static bool pinState = false;
  static unsigned long previousMillis = 0;
  
  if (!initialized) {
    pinMode(outputPin, OUTPUT);
    digitalWrite(outputPin, LOW);
    Serial.println("Starting pin cycle...");
    previousMillis = millis();
    initialized = true;
  }
  
  unsigned long currentMillis = millis();
  
  if (pinState) {
    if (currentMillis - previousMillis >= onTime) {
      pinState = false;
      previousMillis = currentMillis;
      digitalWrite(outputPin, LOW);
      Serial.println("Pin turned OFF");
      Serial.print("Time (ms): ");
      Serial.println(currentMillis);
    }
  } else {
    if (currentMillis - previousMillis >= offTime) {
      pinState = true;
      previousMillis = currentMillis;
      digitalWrite(outputPin, HIGH);
      Serial.println("Pin turned ON");
      Serial.print("Time (ms): ");
      Serial.println(currentMillis);
    }
  }
}

void setup() {
  // Optional: you can call pinCycleController here if you want init to run immediately
  Serial.begin(115200);
}

void loop() {
  pinCycleController();  // Your single function called repeatedly
}
