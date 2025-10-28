#include <Wire.h>
#include "RTClib.h"
#include <ESP8266WiFi.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

#define LED_PIN 2   // Onboard LED (GPIO2, active LOW)
#define LED_EXTRA 14  // extra led for notification

void initializeAndSyncRTC() {
  RTC_PCF8563 rtc;
  WiFiUDP ntpUDP;

  const char* ssid = "Ajay_Home";
  const char* password = "Bidyut@1603";
  const long utcOffsetInSeconds = 19800; // India UTC+5:30

  NTPClient timeClient(ntpUDP, "pool.ntp.org", utcOffsetInSeconds, 60000);

  // --- Serial and LED Initialization ---
  Serial.begin(115200);
  delay(1000);  // Allow Serial monitor to start

  pinMode(LED_PIN, OUTPUT); // pin set as output
  pinMode(LED_EXTRA, OUTPUT); // pin set as output

  digitalWrite(LED_PIN, HIGH); // LED OFF initially
  digitalWrite(LED_EXTRA, LOW);

  Serial.println();
  Serial.println("=== RTC + NTP Initialization ===");

  // --- RTC Check ---
  if (!rtc.begin()) {
    Serial.println("❌ Couldn't find PCF8563 RTC! LED will blink fast.");
    while (true) {
      digitalWrite(LED_PIN, LOW); delay(200);
      digitalWrite(LED_EXTRA, HIGH); delay(200);
      digitalWrite(LED_PIN, HIGH); delay(200);
      digitalWrite(LED_EXTRA, LOW); delay(200);
    }
  }
  Serial.println("✅ PCF8563 RTC found!");

  // --- Connect WiFi ---
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  unsigned long startWiFi = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startWiFi < 15000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\n❌ WiFi connection failed! LED will blink slowly.");
    while (true) {
      digitalWrite(LED_PIN, LOW); delay(500);
      digitalWrite(LED_EXTRA, HIGH); delay(500);
      digitalWrite(LED_PIN, HIGH); delay(500);
      digitalWrite(LED_EXTRA, LOW); delay(500);
    }
  }
  Serial.println("\n✅ WiFi connected!");

  // --- Get NTP Time ---
  timeClient.begin();
  Serial.println("Getting NTP time...");
  unsigned long startNTP = millis();
  bool ntpSuccess = false;

  while (!timeClient.update()) {
    Serial.println("Waiting for NTP update...");
    timeClient.forceUpdate();
    if (millis() - startNTP > 15000) {  // 15-second timeout
      Serial.println("❌ NTP update failed! LED will blink slowly.");
      ntpSuccess = false;
      break;
    }
    delay(500);
  }

  // If update succeeded before timeout
  if (millis() - startNTP <= 15000) {
    ntpSuccess = true;
  }

  // --- Result ---
  if (ntpSuccess) {
    unsigned long epochTime = timeClient.getEpochTime();
    DateTime ntpTime(epochTime);

    Serial.printf("✅ Setting RTC time to: %04d/%02d/%02d %02d:%02d:%02d\n",
                  ntpTime.year(), ntpTime.month(), ntpTime.day(),
                  ntpTime.hour(), ntpTime.minute(), ntpTime.second());

    rtc.adjust(ntpTime);
    delay(200);
    WiFi.disconnect(true);

    DateTime now = rtc.now();
    Serial.printf("RTC Confirm: %04d/%02d/%02d %02d:%02d:%02d\n",
                  now.year(), now.month(), now.day(),
                  now.hour(), now.minute(), now.second());
    Serial.println("✅ RTC Sync Complete. System Ready.");

    // ✅ LED stays ON for success
    digitalWrite(LED_PIN, LOW);  // Active LOW → LED ON
  } 
  else {
    WiFi.disconnect(true);
    Serial.println("❌ RTC not updated (NTP failed). LED will blink slowly.");
    while (true) {
      digitalWrite(LED_PIN, LOW); delay(500);
      digitalWrite(LED_EXTRA, HIGH); delay(500);
      digitalWrite(LED_PIN, HIGH); delay(500);
      digitalWrite(LED_EXTRA, LOW); delay(500);
    }
  }
}

void setup() {
  initializeAndSyncRTC();
}

void loop() {
  // Nothing here
}
