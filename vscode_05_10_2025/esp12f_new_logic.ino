
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <NTPClient.h>

// ================== PIN CONFIG ==================
const int ledPin      = 2;   // Status LED wifi
const int togglePin   = 14;  // Cyclic pin for aquriam water filter pump
const int seasonalPin = 12;  // Seasonal pin for aquriam light
const int ldrPin      = A0;  // LDR analog input   ldr sensor
const int ldrledPin   = 12;  // LED/Relay controlled by LDR  for aquriam light day time on or off using ldr gpiopin13
const int chargerPin  = 16;  // Daily 24-hour battery charger pin 12v 1 amp 
const int dailypulspin = 15;   // daily puls pin  use for aquriam fish food fedeer 
const int waterchangeOutputpin = 0; // waterchange output pin
const int waterchangeInputpin = 5; // waterchange output pin

const int powerSensePin = 13; // Power detection input (e.g., D3)
const int airPumpPin    = 4; // Air pump output when no power

const int threshold   = 500; // LDR threshold
unsigned long previousMillis = 0;
const unsigned long interval = 200; // LDR read interval

// ================== CYCLIC TIMINGS ==================
const unsigned long onDuration  = 60UL*60UL*1000UL;   // 1 hour
const unsigned long offDuration = 120UL*60UL*1000UL;  // 2 hours

// ================== NTP CLOCK ==================
class Clock {
private:
    const char* ssid     = "Ajay_Home";
    const char* password = "Bidyut@1603";
    WiFiUDP ntpUDP;
    NTPClient timeClient;

    int hour24=0, hour12=0, minute_=0, second_=0;
    bool isPM=false;
    int month_=1, day_=1, year_=1970, weekday_=0;

    unsigned long previousTick = 0;

    const char* monthNames[12]   = {"Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"};
    const char* weekdayNames[7]  = {"Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"};

    void to12Hour(int h24){
        if(h24==0){ hour12=12; isPM=false; }
        else if(h24<12){ hour12=h24; isPM=false; }
        else if(h24==12){ hour12=12; isPM=true; }
        else { hour12=h24-12; isPM=true; }
    }

    void incrementDate(){
        day_++;
        weekday_=(weekday_+1)%7;
        int dim[]={31,28,31,30,31,30,31,31,30,31,30,31};
        if((year_%4==0 && year_%100!=0) || year_%400==0) dim[1]=29; // leap year
        if(day_>dim[month_-1]){ day_=1; month_++; if(month_>12){month_=1; year_++;} }
    }

    void setFromEpoch(time_t epoch){
        struct tm ti;
        gmtime_r(&epoch, &ti);
        second_=ti.tm_sec; minute_=ti.tm_min; hour24=ti.tm_hour; to12Hour(hour24);
        day_=ti.tm_mday; month_=ti.tm_mon+1; year_=ti.tm_year+1900; weekday_=ti.tm_wday;
        previousTick=millis();
        Serial.printf("// NTP updated: %02d:%02d:%02d %s | %s %02d, %d | %s\n",
                      hour12,minute_,second_,isPM?"PM":"AM",monthNames[month_-1],day_,year_,weekdayNames[weekday_]);
    }

    void tick(){                                                // esp own clock for ntc not update 
        unsigned long now = millis();
        if(now-previousTick>=1000){
            unsigned long steps = (now-previousTick)/1000;
            previousTick += steps*1000UL;
            for(unsigned long s=0;s<steps;s++){
                second_++;
                if(second_>=60){ second_=0; minute_++;
                    if(minute_>=60){ minute_=0; hour24++;
                        if(hour24>=24){ hour24=0; incrementDate(); }
                        to12Hour(hour24);
                    }
                }
            }
        }
    }

    void connectWiFi(){   
        WiFi.mode(WIFI_STA);
        WiFi.begin(ssid,password);
        Serial.print("\n// Connecting to WiFi");
        Serial.println();
        unsigned long start=millis();
        while(WiFi.status()!=WL_CONNECTED){
            delay(250); Serial.print(".");
            if(millis()-start>20000){
                Serial.println("\n// WiFi failed, retrying...");
                WiFi.disconnect(); WiFi.begin(ssid,password); start=millis();
            }
        }
        Serial.println("\n// WiFi connected.");
    }

    void updateNTP(){
        static unsigned long lastNtpTry=0;
        if(millis()-lastNtpTry>60000){
            lastNtpTry=millis();
            if(timeClient.update()) setFromEpoch(timeClient.getEpochTime());
        }
    }

public:
    Clock():timeClient(ntpUDP,"time.google.com",19800,60000) {}

    void run(){
        static bool init=false;
        if(!init){
            Serial.begin(115200);
            connectWiFi();
            timeClient.begin();
            if(timeClient.update()) setFromEpoch(timeClient.getEpochTime());
            init=true;
        }
        tick();
        updateNTP();
    }

    int getHour24(){ return hour24; }
    int getMinute(){ return minute_; }
    int getSecond(){ return second_; }
    int getMonth(){ return month_; }
    int getDay(){ return day_; }
    int getWeekday(){ return weekday_; }
    String getTimeStr(){ return String(hour12)+":"+String(minute_)+":"+String(second_)+(isPM?" PM":" AM"); }
};

Clock myClock;

// ================== STATUS LED ==================
void handleStatusLed(){
    pinMode(ledPin, OUTPUT);                            // ledpin output set
    static unsigned long lastBlink=0;
    static bool ledState=false;
    unsigned long now=millis();

    if(WiFi.status()!=WL_CONNECTED){
        if(now-lastBlink>=200){ lastBlink=now; ledState=!ledState; digitalWrite(ledPin, ledState); }
    }
    else if(!myClock.getHour24()){ 
        if(now-lastBlink>=800){ lastBlink=now; ledState=!ledState; digitalWrite(ledPin, ledState); }
    }
    else digitalWrite(ledPin,LOW);
}

// ================== CYCLIC PIN  (Aquriam water filter pump ) ==================
void handleCyclicPin(){
    static bool firstRun=true;
    static bool pinState=HIGH;
    static unsigned long lastToggle=0;
    unsigned long now=millis();

    if(firstRun){ pinMode(togglePin,OUTPUT); digitalWrite(togglePin,HIGH); firstRun=false; lastToggle=now; }

    if(pinState && now-lastToggle>=onDuration){ pinState=LOW; digitalWrite(togglePin,pinState); lastToggle=now; }
    else if(!pinState && now-lastToggle>=offDuration){ pinState=HIGH; digitalWrite(togglePin,pinState); lastToggle=now; }
}

// ================== SEASONAL PIN (aquriam light on off using month and time )==================
void handleSeasonalPin(){
    static bool firstRun=true;
    static bool pinState=LOW;
    static int lastToggleDay=-1;

    if(firstRun){ pinMode(seasonalPin,OUTPUT); digitalWrite(seasonalPin,pinState); firstRun=false; }

    int month=myClock.getMonth();
    int hour=myClock.getHour24();
    int day=myClock.getDay();
    int onHour = (month==1||month==2||month>=10) ? 17:18;
    int offHour=22;

    if(!pinState && hour>=onHour && lastToggleDay!=day){ digitalWrite(seasonalPin,HIGH); pinState=HIGH; lastToggleDay=day; }
    if(pinState && hour>=offHour){ digitalWrite(seasonalPin,LOW); pinState=LOW; }
}

// ================== LDR CONTROL (Month + Time Based for aquriam light in day time ) ==================
void controlLdrLed() {
    static bool initialized = false;
    if (!initialized) { pinMode(ldrledPin, OUTPUT); initialized = true; }

    unsigned long now = millis();
    if (now - previousMillis >= interval) {
        previousMillis = now;

        int month  = myClock.getMonth();
        int hour   = myClock.getHour24();
        int minute = myClock.getMinute();

        int startHour = 8, startMinute = 0;
        int endHour, endMinute;

        if (month == 1 || month == 2 || month == 10 || month == 11 || month == 12) {
            endHour = 16; endMinute = 48;
        } else {
            endHour = 17; endMinute = 58;
        }

        bool withinTime = ( (hour > startHour || (hour == startHour && minute >= startMinute)) &&
                            (hour < endHour || (hour == endHour && minute <= endMinute)) );

        int val = analogRead(ldrPin);

        if (withinTime) {
            digitalWrite(ldrledPin, (val < threshold) ? HIGH : LOW);
        } else {
            digitalWrite(ldrledPin, LOW);
        }

        // Serial.printf("Month=%d | Time=%02d:%02d | LDR_value=%d | LDR_light=%s | light_Relay=%s\n",
        //               month, hour, minute, val,
        //               withinTime ? "ACTIVE" : "OFF",
        //               digitalRead(ldrledPin) ? "ON" : "OFF");
    }
}

// ================== DAILY 24-HOUR TOGGLE (Battery charging using 12v charger)==================
void dailyTogglePin(int pin){
    static bool firstRun = true;        
    static bool pinState = LOW;         
    static unsigned long lastToggle = 0;
    static int lastToggleDay = -1;      
    unsigned long now = millis();

    if(firstRun){ pinMode(pin, OUTPUT); digitalWrite(pin, pinState); firstRun = false; }

    int hour = myClock.getHour24();
    int day  = myClock.getDay();

    if(!pinState && lastToggleDay != day){  
        digitalWrite(pin, HIGH);
        pinState = HIGH;
        lastToggle = now;
        lastToggleDay = day;
        Serial.printf("// Pin %d turned ON for 2.5 hours\n", pin);
    }

    if(pinState && now - lastToggle >= 2.5 * 60 * 60 * 1000UL){
        digitalWrite(pin, LOW);
        pinState = LOW;
        Serial.printf("// Pin %d turned OFF after 2.5 hours\n", pin);
    }
}

// ================== THREE DAILY PULSES (Aquriam fish food feeder) ==================
void dailyPulsePin(int pin){
    static bool firstRun = true;
    static bool pulseActive = false;
    static unsigned long pulseStart = 0;
    unsigned long now = millis();

    int hour = myClock.getHour24();
    int minute = myClock.getMinute();

    int pulseHours[3] = {8,13,20}; // 8AM, 1PM, 8PM

    if(firstRun){ pinMode(pin, OUTPUT); digitalWrite(pin, LOW); firstRun=false; }

    for(int i=0;i<3;i++){
        if(hour==pulseHours[i] && minute==0 && !pulseActive){
            digitalWrite(pin,HIGH);
            pulseStart=now;
            pulseActive=true;
            Serial.printf("// Pin %d pulse started at %02d:00\n",pin,pulseHours[i]);
        }
    }

    if(pulseActive && now-pulseStart>=30UL*1000UL){
        digitalWrite(pin,LOW);
        pulseActive=false;
        Serial.printf("// Pin %d pulse ended\n",pin);
    }
}

// ================== WEEKLY WATER CHANGE sunday ==================
void weeklyWaterChange(int outPin,int inPin){
    static bool firstRun=true;
    static bool step1Done=false;
    static bool step2Done=false;
    static unsigned long stepStart=0;
    static int lastWeekDay=-1;
    unsigned long now=millis();

    int hour=myClock.getHour24();
    int minute=myClock.getMinute();
    int weekday=myClock.getWeekday();

    if(firstRun){
        pinMode(outPin,OUTPUT);
        pinMode(inPin,OUTPUT);
        digitalWrite(outPin,LOW);
        digitalWrite(inPin,LOW);
        firstRun=false;
    }

    if(weekday==0 && lastWeekDay!=myClock.getDay()){ step1Done=false; step2Done=false; lastWeekDay=myClock.getDay(); }

    if(!step1Done && weekday==0 && hour==8 && minute==0){
        digitalWrite(outPin,HIGH);
        stepStart=now;
        step1Done=true;
        Serial.println("// Water OUT pump started");
    }

    if(step1Done && digitalRead(outPin) && now-stepStart>=18UL*60UL*1000UL){
        digitalWrite(outPin,LOW);
        stepStart=now;
        Serial.println("// Water OUT pump stopped");
    }

    if(step1Done && !step2Done && !digitalRead(outPin) && now-stepStart>=5UL*60UL*1000UL){
        digitalWrite(inPin,HIGH);
        stepStart=now;
        step2Done=true;
        Serial.println("// Water IN pump started");
    }

    if(step2Done && digitalRead(inPin) && now-stepStart>=18UL*60UL*1000UL){
        digitalWrite(inPin,LOW);
        Serial.println("// Water IN pump stopped");
    }
}
//  digital pin status print in serial monitor
void digital_pin_status() {
    static unsigned long lastMillis = 0;       // Last timestamp
    static int lineIndex = 0;                   // Which line to print
    unsigned long now = millis();

    if (now - lastMillis >= 2000) {            // 2 seconds passed
        lastMillis = now;

        switch(lineIndex) {
            case 0: Serial.println(String("ledPin = ") + (digitalRead(ledPin) ? "HIGH(Led_off)" : "LOW(Led_on)")); break;
            case 1: Serial.println(String("togglePin = ") + (digitalRead(togglePin) ? "HIGH" : "LOW")); break;
            case 2: Serial.println(String("seasonalPin = ") + (digitalRead(seasonalPin) ? "HIGH" : "LOW")); break;
            case 3: Serial.println(String("ldr_value = ") + analogRead(ldrPin)); break;
            case 4: Serial.println(String("ldrledPin = ") + (digitalRead(ldrledPin) ? "HIGH" : "LOW")); break;
            case 5: Serial.println(String("chargerPin = ") + (digitalRead(chargerPin) ? "HIGH" : "LOW")); break;
            case 6: Serial.println(String("dailypulspin = ") + (digitalRead(dailypulspin) ? "HIGH" : "LOW")); break;
            case 7: Serial.println(String("waterchangeOutputpin = ") + (digitalRead(waterchangeOutputpin) ? "HIGH" : "LOW")); break;
            case 8: Serial.println(String("waterchangeInputpin = ") + (digitalRead(waterchangeInputpin) ? "HIGH" : "LOW")); break;
        }

        lineIndex++;                            // Move to next line
        if (lineIndex > 8) lineIndex = 0;       // Reset after last line
    }
}



void setup() {
    // Optional: put your one-time initialization here
    Serial.begin(115200);
    // Any other setup code can go here
}


// ================== POWER CHECK AND MAIN CONTROL ==================
void loop(){
    static bool initialized = false;
    if (!initialized) {
        pinMode(powerSensePin, INPUT);
        pinMode(airPumpPin, OUTPUT);
        digitalWrite(airPumpPin, LOW);
        initialized = true;
    }

    static unsigned long lastCheck = 0;
    static bool powerPresent = true;
    unsigned long now = millis();

    // Check power every 500 ms
    if (now - lastCheck >= 500) {
        lastCheck = now;
        int val = digitalRead(powerSensePin);
        powerPresent = (val == HIGH); // HIGH = electricity present
    }

    if (powerPresent) {
        // --- Normal aquarium operations ---
        digitalWrite(airPumpPin, LOW);
        myClock.run();
        handleCyclicPin();
        handleSeasonalPin();
        controlLdrLed();
        handleStatusLed();
        dailyTogglePin(chargerPin);
        dailyPulsePin(dailypulspin);
        weeklyWaterChange(waterchangeOutputpin,waterchangeInputpin);
        digital_pin_status();
    } 
    else {
        // --- No power: run air pump in 10s ON / 20s OFF cycle ---
        static unsigned long lastToggle = 0;
        static bool airState = false;
        if (airState && now - lastToggle >= 10000UL) {
            airState = false;
            digitalWrite(airPumpPin, LOW);
            lastToggle = now;
            Serial.println("// Air pump OFF (no power)");
        } 
        else if (!airState && now - lastToggle >= 20000UL) {
            airState = true;
            digitalWrite(airPumpPin, HIGH);
            lastToggle = now;
            Serial.println("// Air pump ON (no power)");
        }
    }
}
