#include <Wire.h>
#include "RTClib.h"
#include <ESP8266WiFi.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

void initializeAndSyncRTC() {
  // Declare objects inside the function
  RTC_PCF8563 rtc;
  WiFiUDP ntpUDP;

  const char* ssid = "Ajay_Home";
  const char* password = "Bidyut@1603";

  // Set timezone offset in seconds (example: India UTC+5:30 = 19800)
  const long utcOffsetInSeconds = 19800;

  NTPClient timeClient(ntpUDP, "pool.ntp.org", utcOffsetInSeconds, 60000);

  Serial.begin(115200);
  Wire.begin(4, 5); // SDA=GPIO4, SCL=GPIO5
  delay(200);

  Serial.println();
  Serial.println("=== RTC + NTP Initialization ===");

  if (!rtc.begin()) {
    Serial.println("❌ Couldn't find PCF8563 RTC!");
    while (1); // Halt if RTC not found
  }
  Serial.println("✅ PCF8563 RTC found!");

  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 15000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\n❌ WiFi connection failed!");
    return;
  }
  Serial.println("\n✅ WiFi connected!");

  timeClient.begin();
  Serial.println("Getting NTP time...");

  unsigned long startNTP = millis();
  while (!timeClient.update()) {
    Serial.println("Waiting for NTP update...");
    timeClient.forceUpdate();
    if (millis() - startNTP > 15000) {  // 15 seconds timeout
      Serial.println("❌ NTP update failed!");
      WiFi.disconnect(true);
      return;
    }
    delay(500);
  }

  unsigned long epochTime = timeClient.getEpochTime();
  DateTime ntpTime(epochTime);

  Serial.printf("✅ Setting RTC time to: %04d/%02d/%02d %02d:%02d:%02d\n",
                ntpTime.year(), ntpTime.month(), ntpTime.day(),
                ntpTime.hour(), ntpTime.minute(), ntpTime.second());

  rtc.adjust(ntpTime);

  WiFi.disconnect(true);
  Serial.println("✅ WiFi disconnected. RTC updated successfully!");

  DateTime now = rtc.now();
  Serial.printf("RTC Confirm: %04d/%02d/%02d  %02d:%02d:%02d\n",
                now.year(), now.month(), now.day(),
                now.hour(), now.minute(), now.second());

  Serial.println("✅ RTC Sync Complete. System Ready.");
}

void setup() {
  initializeAndSyncRTC();
}

void loop() {
  // Nothing here
}
