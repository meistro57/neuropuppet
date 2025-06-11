// motor_control.ino - Arduino Mega stepper control for Neuropuppet
// Controls 6 stepper motors via A4988 drivers using step/direction pins.
// Receives serial commands from Raspberry Pi in the format "Mx:steps".
// Optional homing with limit switches on pins D2-D7.

const int NUM_MOTORS = 6;

// Step and direction pin assignments (edit to match wiring)
const int stepPins[NUM_MOTORS] = {22, 24, 26, 28, 30, 32};
const int dirPins[NUM_MOTORS]  = {23, 25, 27, 29, 31, 33};

// Limit switch pins for homing (D2-D7)
const int limitPins[NUM_MOTORS] = {2, 3, 4, 5, 6, 7};

const int START_DELAY_US = 2000; // microseconds at start/end of move
const int MIN_DELAY_US   = 600;  // minimum delay during constant speed
const int RAMP_STEPS     = 50;   // number of steps for acceleration/deceleration

String inputString = "";

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < NUM_MOTORS; i++) {
    pinMode(stepPins[i], OUTPUT);
    pinMode(dirPins[i], OUTPUT);
    pinMode(limitPins[i], INPUT_PULLUP);
  }
}

// Perform a homing move until limit switch is triggered
void homeMotor(int id) {
  digitalWrite(dirPins[id], LOW); // assume LOW moves toward switch
  while (digitalRead(limitPins[id]) == HIGH) {
    digitalWrite(stepPins[id], HIGH);
    delayMicroseconds(MIN_DELAY_US);
    digitalWrite(stepPins[id], LOW);
    delayMicroseconds(MIN_DELAY_US);
  }
}

void homeAll() {
  for (int i = 0; i < NUM_MOTORS; i++) {
    homeMotor(i);
  }
}

// Move a motor a given number of steps with a simple accel ramp
void moveMotor(int id, long steps) {
  if (id < 0 || id >= NUM_MOTORS) return;
  bool dir = steps >= 0;
  if (!dir) steps = -steps;
  digitalWrite(dirPins[id], dir ? HIGH : LOW);

  long ramp = steps < RAMP_STEPS ? steps / 2 : RAMP_STEPS;
  for (long i = 0; i < steps; i++) {
    int del = MIN_DELAY_US;
    if (i < ramp) {
      del = START_DELAY_US - (START_DELAY_US - MIN_DELAY_US) * i / ramp;
    } else if (i > steps - ramp) {
      long j = steps - i;
      del = START_DELAY_US - (START_DELAY_US - MIN_DELAY_US) * j / ramp;
    }
    digitalWrite(stepPins[id], HIGH);
    delayMicroseconds(del);
    digitalWrite(stepPins[id], LOW);
    delayMicroseconds(del);
  }
}

// Parse and execute a command string
void handleCommand(String cmd) {
  cmd.trim();
  if (cmd.equalsIgnoreCase("HOME")) {
    homeAll();
    return;
  }
  if (cmd.charAt(0) != 'M') return;
  int colon = cmd.indexOf(':');
  if (colon == -1) return;
  int motorId = cmd.substring(1, colon).toInt() - 1; // convert to 0-based index
  long steps = cmd.substring(colon + 1).toInt();
  moveMotor(motorId, steps);
}

void loop() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      handleCommand(inputString);
      inputString = "";
    } else {
      inputString += inChar;
    }
  }
}

