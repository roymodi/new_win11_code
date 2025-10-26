#include <U8g2lib.h>
#include <Wire.h>

// For ESP12F GPIO4 (SDA), GPIO5 (SCL)
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

void setup() {
  Wire.begin(4, 5);  // SDA, SCL
  u8g2.begin();
}

void loop() {
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.drawStr(0, 20, "Hello DST-031!");
  u8g2.sendBuffer();
  delay(1000);
}
