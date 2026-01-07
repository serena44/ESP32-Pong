#include <WiFi.h>
#include <HTTPClient.h>


// WIFI AND SERVER
const char* ssid = "Ur mom"; // hotspot name
const char* password = "password"; //hotspot password
const char* serverBase = "http://172.20.10.2:5000"; //laptop ip


//BUTTONS
const int buttonUp = 14;
const int buttonDown = 27;


// VARS
int paddle = 0;


void setup() {
  Serial.begin(115200);


  pinMode(buttonUp, INPUT_PULLUP);
  pinMode(buttonDown, INPUT_PULLUP);


  // CONNECT TO WIFI
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");


  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 60000) { // 20 sec timeout
    delay(500);
    Serial.print(".");
  }


  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected!");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to WiFi!");
  }
}


unsigned long lastTime = 0;


void loop() {
  if (WiFi.status() != WL_CONNECTED) return; 


  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0;
  lastTime = now;


  int up = digitalRead(buttonUp);
  int down = digitalRead(buttonDown);


  // Paddle speed
  float speed = 450; // pixels per second


  if (up == LOW)   paddle -= speed * dt;
  if (down == LOW) paddle += speed * dt;


  // Clamp paddle position
  if (paddle < 0) paddle = 0;
  if (paddle > 500) paddle = 500;


  // Send paddle to server
  HTTPClient http;
  String url = String(serverBase) + "/update?paddle=" + String((int)paddle);
  http.begin(url);
  int httpCode = http.GET();
  if (httpCode <= 0) {
    Serial.println("Error sending paddle to server");
  }
  http.end();


  delay(10);
}



