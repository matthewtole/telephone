int outputPins[] = { 2, 3,  4,  5 };
int inputPins[]  = { 8, 9, 10, 11 };

char buttons[ 4 ][ 4 ] = {
  { '?', '2', '3', '1' },
  { '?', '5', '6', '4' },
  { '?', '0', '#', '*' },
  { '?', '8', '9', '7' },
};

void setup() {
  for (int i = 0; i < 4; i += 1 ) {
    pinMode(outputPins[i], INPUT_PULLUP);
  }
  for (int i = 0; i < 4; i += 1 ) {
    pinMode(inputPins[i], INPUT_PULLUP);
  }

  Serial.begin(9600);
}


void loop() {
  for (int out = 0; out < 4; out += 1 ) {
    pinMode(outputPins[out], OUTPUT);
    digitalWrite(outputPins[out], LOW);
    for (int in = 0; in < 4; in += 1 ) {
      if (digitalRead(inputPins[in]) == LOW) {
        Serial.println(buttons[in][out]);
      }
    }
    pinMode(outputPins[out], INPUT_PULLUP);
  }
}
