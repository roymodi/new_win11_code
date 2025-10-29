#include <Wire.h>

class RTC_PCF8563 {
private:
  const byte PCF8563_ADDR = 0x51;

  int bcdToDec(byte val) {
    return ((val >> 4) * 10 + (val & 0x0F));
  }

  const char* weekDays[7] = {
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
  };

  void readTimeData(byte &sec, byte &min, byte &hour, byte &day, byte &month, byte &year) {
    Wire.beginTransmission(PCF8563_ADDR);
    Wire.write(0x02);  // Start at seconds register
    Wire.endTransmission();

    Wire.requestFrom(PCF8563_ADDR, 7);
    sec   = Wire.read() & 0x7F;
    min   = Wire.read() & 0x7F;
    hour  = Wire.read() & 0x3F;
    day   = Wire.read() & 0x3F;
    Wire.read(); // weekday (ignored)
    month = Wire.read() & 0x1F;
    year  = Wire.read();
  }

  int calcWeekday(uint16_t y, uint8_t mo, uint8_t d) {
    int Y = (mo < 3) ? (y - 1) : y;
    int M = (mo < 3) ? (mo + 12) : mo;
    int K = Y % 100;
    int J = Y / 100;
    int f = d + ((13 * (M + 1)) / 5) + K + (K / 4) + (J / 4) + (5 * J);
    return ((f + 6) % 7);  // Sunday=0, Monday=1, etc.
  }

public:
  RTC_PCF8563() {}

  // ✅ Combined setup function
  void beginAll() {
    Serial.begin(115200);
    Wire.begin();
    Serial.println("RTC Initialized!");
  }

  String getTimeAMPM() {
    byte sec, min, hour, day, month, year;
    readTimeData(sec, min, hour, day, month, year);

    uint8_t s = bcdToDec(sec);
    uint8_t m = bcdToDec(min);
    uint8_t h = bcdToDec(hour);

    String ampm = "AM";
    uint8_t hour12 = h;
    if (h == 0) { hour12 = 12; ampm = "AM"; }
    else if (h == 12) { ampm = "PM"; }
    else if (h > 12) { hour12 = h - 12; ampm = "PM"; }

    char buffer[20];
    sprintf(buffer, "%02d:%02d:%02d %s", hour12, m, s, ampm.c_str());
    return String(buffer);
  }

  String getWeekday() {
    byte sec, min, hour, day, month, year;
    readTimeData(sec, min, hour, day, month, year);

    uint8_t d = bcdToDec(day);
    uint8_t mo = bcdToDec(month);
    uint16_t y = 2000 + bcdToDec(year);

    int index = calcWeekday(y, mo, d);
    return String(weekDays[index]);
  }

  String getMonth() {
    byte sec, min, hour, day, month, year;
    readTimeData(sec, min, hour, day, month, year);

    uint8_t mo = bcdToDec(month);

    const char* months[12] = {
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"
    };

    if (mo >= 1 && mo <= 12)
      return String(months[mo - 1]);
    else
      return String("Invalid");
  }
};

// --- Global object ---
RTC_PCF8563 rtc;

void setup() {
  rtc.beginAll();  // ✅ One call handles Serial + Wire init  (rtc object and beginall class  )
}

void loop() {
  Serial.print("Time: ");
  Serial.println(rtc.getTimeAMPM());

  Serial.print("Weekday: ");
  Serial.println(rtc.getWeekday());

  Serial.print("Month: ");
  Serial.println(rtc.getMonth());

  Serial.println("---------------------");
  delay(1000);
}
