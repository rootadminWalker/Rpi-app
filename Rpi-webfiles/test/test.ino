#include <Servo.h>

Servo outdoor;
Servo indoor;
Servo return_door;

int trig = 9;
int echo = 10;

char signal_from_computer = "";

void setup() {
  Serial.begin(9600);
  outdoor.attach(7);
  indoor.attach(5);
  return_door.attach(6);
  outdoor.write(40);
  indoor.write(40);
  return_door.write(105);
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
}

int ping_cm() {
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long duration = pulseIn(echo, HIGH);
  int distance = duration * 0.0343 / 2;
  return distance;
}

void loop() {
int distance = ping_cm();
Serial.println(distance);
  if (Serial.available()) {
    signal_from_computer = Serial.read();
    if (signal_from_computer == 49) {
      outdoor.write(75);
      delay(3000);
      
      outdoor.write(40);
      delay(3000);
      
      indoor.write(80);
      delay(3000);
      
      indoor.write(40);
      delay(3000);
    } 
    
    } if (signal_from_computer == 50) {
      return_door.write(38);
    } if (signal_from_computer == 51) {
      return_door.write(105);
    }
}

