#include <Wire.h>
#include <Servo.h>

#define MPU_ADDR 0x68
Servo knob;

const int SERVO_PIN = 9;

const float SERVO_MIN_DEG = -90.0;
const float SERVO_MAX_DEG =  90.0;

const float STEP_DEG = 1.5;
const int   STEP_DELAY_MS = 35;
const int   PEAK_COOLDOWN_MS = 250;

const float VIB_THRESHOLD = 55.0;
const int   VIB_SAMPLES = 12;
const int   VIB_SAMPLE_DELAY_MS = 4;

float combo[10];
int comboLen = 0;

float lastPeakAtDeg = 9999;
unsigned long lastPeakTime = 0;



int degToUs(float deg) {
  deg = constrain(deg, SERVO_MIN_DEG, SERVO_MAX_DEG);
  float servoDeg = deg + 90.0;
  return map((int)servoDeg, 0, 180, 1000, 2000);
}

void mpuWrite(byte reg, byte data) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.write(data);
  Wire.endTransmission();
}

void mpuRead14(int16_t &ax, int16_t &ay, int16_t &az, int16_t &gx, int16_t &gy, int16_t &gz) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 14, true);

  ax = Wire.read() << 8 | Wire.read();
  ay = Wire.read() << 8 | Wire.read();
  az = Wire.read() << 8 | Wire.read();
  Wire.read(); Wire.read();
  gx = Wire.read() << 8 | Wire.read();
  gy = Wire.read() << 8 | Wire.read();
  gz = Wire.read() << 8 | Wire.read();
}

float readVibration() {
  long sumMag = 0;
  for (int i = 0; i < VIB_SAMPLES; i++) {
    int16_t ax, ay, az, gx, gy, gz;
    mpuRead14(ax, ay, az, gx, gy, gz);
    long mag = abs(gx) + abs(gy) + abs(gz);
    sumMag += mag;
    delay(VIB_SAMPLE_DELAY_MS);
  }
  return (float)sumMag / (float)VIB_SAMPLES;
}

void goToDeg(float deg) {
  knob.writeMicroseconds(degToUs(deg));
}

void scanForPeaks(bool clockwise) {
  float start;
  float end;
  float step;
  if (clockwise) {
    start = SERVO_MIN_DEG;
    end   = SERVO_MAX_DEG;
    step  = STEP_DEG;
  } else {
    start = SERVO_MAX_DEG;
    end   = SERVO_MIN_DEG;
    step  = -STEP_DEG;
  }

  for (float d = start; clockwise ? d <= end : d >= end; d += step) {
    goToDeg(d);
    delay(STEP_DELAY_MS);

    float vib = readVibration();

    unsigned long now = millis();
    bool farEnough = abs(d - lastPeakAtDeg) > 6.0;
    bool timeEnough = (now - lastPeakTime) > PEAK_COOLDOWN_MS;

    if (vib > VIB_THRESHOLD && farEnough && timeEnough) {
      if (comboLen < 10) {
        combo[comboLen++] = d;
        lastPeakAtDeg = d;
        lastPeakTime = now;
        delay(120);
      }
    }

    if (comboLen >= 10) return;
  }
}

void replayCombo() {
  goToDeg(SERVO_MIN_DEG);
  delay(400);

  unsigned long t0 = millis();
  bool cw = true;

  for (int i = 0; i < comboLen; i++) {
    float target = combo[i];
    float approachFrom = cw ? (target - 3.0) : (target + 3.0);
    approachFrom = constrain(approachFrom, SERVO_MIN_DEG, SERVO_MAX_DEG);

    goToDeg(approachFrom);
    delay(120);
    goToDeg(target);
    delay(220);

    cw = !cw;
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin();

  mpuWrite(0x6B, 0x00);
  delay(100);

  knob.attach(SERVO_PIN);
  goToDeg(SERVO_MIN_DEG);
  delay(500);
}

void loop() {
  if (comboLen < 10) {
    bool clockwise = (comboLen % 2 == 0);
    scanForPeaks(clockwise);
  } else {
    replayCombo();
    while (true) delay(1000);
  }
}
