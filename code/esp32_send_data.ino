#include <WiFi.h>
#include <WiFiUdp.h>
#include "DHT.h"

#define DHTPIN 23
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

const char * ssid = "ssid";
const char * pwd = "pwd";

const char * udpAddress = "udpAddress";
const int udpPort = 5006;

WiFiUDP udp;

void setup(){
  Serial.begin(115200);
  WiFi.begin(ssid, pwd);
  dht.begin();
  Serial.println("");

  // Wait for WiFi connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  udp.begin(udpPort);
}

void loop(){
  // Read temperature and humidity
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  
  // Convert to string with two decimal places
  String message = String(t, 2) + "," + String(h, 2);
  
  // Send UDP packet
  udp.beginPacket(udpAddress, udpPort);
  udp.write((const uint8_t*) message.c_str(), message.length());
  udp.endPacket();
  
  Serial.print("Sent: ");
  Serial.println(message);
  
  delay(1000);
}
