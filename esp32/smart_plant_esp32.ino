/*
  OPTIONAL REAL-HARDWARE VERSION

  Board: ESP32
  Sensors: capacitive soil sensor + DHT11/DHT22 + LDR
  Actuator: relay/MOSFET + external pump

  Libraries:
    WiFi
    HTTPClient
    DHT sensor library

  IMPORTANT:
    Do not power a water pump directly from an ESP32 GPIO.
    Use a suitable relay/MOSFET driver and external power supply.
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

#define DHTPIN 4
#define DHTTYPE DHT22
#define SOIL_PIN 34
#define LDR_PIN 35
#define PUMP_PIN 26

const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
const char* API_URL = "https://YOUR-BACKEND.onrender.com/api/v1/readings";
const char* DEVICE_KEY = "YOUR_DEVICE_API_KEY";

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);
  dht.begin();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void loop() {
  int soilRaw = analogRead(SOIL_PIN);
  int lightRaw = analogRead(LDR_PIN);

  // Calibrate these values for your actual sensor.
  float moisture = map(soilRaw, 3500, 1200, 0, 100);
  moisture = constrain(moisture, 0, 100);

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("DHT read failed");
    delay(5000);
    return;
  }

  String json = String("{") +
    "\"device_id\":\"esp32-plant-01\"," +
    "\"soil_moisture\":" + String(moisture, 2) + "," +
    "\"temperature\":" + String(temperature, 2) + "," +
    "\"humidity\":" + String(humidity, 2) + "," +
    "\"light\":" + String(lightRaw) +
    "}";

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Key", DEVICE_KEY);

  int status = http.POST(json);
  Serial.printf("API status: %d\n", status);
  http.end();

  delay(10000);
}
