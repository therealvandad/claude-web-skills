// fanctl: protocol v1, newline-terminated ASCII at 115200 baud. loop() never blocks.
const char PROTOCOL[] = "1";
const uint8_t PINS[] = {9, 10};                 // PWM-capable pins, one per fan
const uint8_t FANS = sizeof(PINS);
uint8_t percent[FANS] = {40, 40};
char buf[40];                                   // one incoming line, without the newline
uint8_t len = 0;
bool tooLong = false;

void apply(uint8_t f) { analogWrite(PINS[f], map(percent[f], 0, 100, 0, 255)); }
unsigned long rpmOf(uint8_t f) { return percent[f] * 30UL; }   // STUB: replace with real tach pulse counting

bool toInt(const char* s, long& out) {         // strict: "12" yes, "12x" and "" no
  if (!s) return false;
  char* end;
  out = strtol(s, &end, 10);
  return end != s && *end == '\0';
}

void handle(char* line) {
  char* verb = strtok(line, " ");
  if (!verb) return;                            // blank line: ignore
  if (!strcmp(verb, "PING")) Serial.println(F("PONG"));
  else if (!strcmp(verb, "VER")) { Serial.print(F("VER ")); Serial.println(PROTOCOL); }
  else if (!strcmp(verb, "GET")) {
    for (uint8_t f = 0; f < FANS; f++) { Serial.print(F("RPM ")); Serial.print(f); Serial.print(' '); Serial.println(rpmOf(f)); }
  } else if (!strcmp(verb, "SET")) {
    long fan, pct;
    if (!toInt(strtok(NULL, " "), fan) || !toInt(strtok(NULL, " "), pct) || strtok(NULL, " ")) Serial.println(F("ERR args"));
    else if (fan < 0 || fan >= FANS || pct < 0 || pct > 100) Serial.println(F("ERR range"));
    else { percent[fan] = pct; apply(fan); Serial.println(F("OK")); }
  } else Serial.println(F("ERR unknown"));
}

void setup() {
  Serial.begin(115200);
  // Uno/Nano only: Timer1 prescaler 1 moves pins 9 and 10 from 490 Hz to ~31 kHz, which 4-pin PC fans expect.
  // TCCR1B = (TCCR1B & 0b11111000) | 0x01;
  for (uint8_t f = 0; f < FANS; f++) { pinMode(PINS[f], OUTPUT); apply(f); }
}

void loop() {
  while (Serial.available() > 0) {              // take only what has already arrived
    char c = Serial.read();
    if (c == '\r') continue;                    // accept \r\n as well as \n
    if (c != '\n') {
      if (len < sizeof buf - 1) buf[len++] = c; else tooLong = true;
      continue;
    }
    buf[len] = 0;
    if (tooLong) Serial.println(F("ERR long")); else handle(buf);
    len = 0;
    tooLong = false;
  }
  // other non-blocking work goes here (count tach pulses, update a display); never delay()
}
