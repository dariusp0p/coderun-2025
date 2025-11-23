#include <Servo.h>

Servo knob;
const int SERVO_PIN = 9;
const int LIGHT_PIN = A0;

const int LIGHT_THRESHOLD = 520;
const int SHORT_MAX_MS = 18;
const int LONG_MIN_MS  = 28;

const int GAP_END_MS = 140;

const float ZONE_A_DEG = -70;
const float ZONE_B_DEG = -20;
const float ZONE_C_DEG =  20;
const float ZONE_D_DEG =  70;



int degToUs(float deg) {
  deg = constrain(deg, -90, 90);
  float servoDeg = deg + 90.0;
  return map((int)servoDeg, 0, 180, 1000, 2000);
}

void goZone(char z) {
  float d = 0;
  switch (z) {
    case 'A': d = ZONE_A_DEG; break;
    case 'B': d = ZONE_B_DEG; break;
    case 'C': d = ZONE_C_DEG; break;
    case 'D': d = ZONE_D_DEG; break;
    default:  d = 0;
  }
  knob.writeMicroseconds(degToUs(d));
}

char mapZone(int shortC, int longC) {
  if (shortC < 1 || shortC > 5 || longC < 1 || longC > 5) return '?';

  static const char table[5][5] = {
    {'A','A','B','A','C'},
    {'C','B','C','C','B'},
    {'D','A','C','D','C'},
    {'B','D','B','B','A'},
    {'D','C','A','B','C'}
  };
  return table[shortC-1][longC-1];
}

bool lightOn() {
  return analogRead(LIGHT_PIN) > LIGHT_THRESHOLD;
}

void setup() {
  Serial.begin(115200);
  knob.attach(SERVO_PIN);
  knob.writeMicroseconds(degToUs(0));
}

void loop() {
  while (!lightOn())
    delayMicroseconds(200);

  int shortC = 0, longC = 0;
  unsigned long lastEdge = millis();

  bool cycleEnded = false;
  while (!cycleEnded) {
    unsigned long tOnStart = millis();
    while (lightOn()) {
      if (millis() - tOnStart > 200) break;
    }
    unsigned long tOnEnd = millis();
    int onDur = (int)(tOnEnd - tOnStart);

    if (onDur <= SHORT_MAX_MS) shortC++;
    else if (onDur >= LONG_MIN_MS) longC++;
    else {
      if (onDur < (SHORT_MAX_MS + LONG_MIN_MS) / 2) shortC++;
      else longC++;
    }

    lastEdge = tOnEnd;

    unsigned long tGapStart = millis();
    while (!lightOn()) {
      if ((int)(millis() - tGapStart) > GAP_END_MS) {
        cycleEnded = true;
        break;
      }
    }
  }

  char zone = mapZone(shortC, longC);

  if (zone != '?') {
    goZone(zone);
    delay(220);
  }

  knob.writeMicroseconds(degToUs(0));
  delay(120);
}
