#include <Arduino.h>
#include "TM1637.h"

#include "pin_allocations.h"

TM1637 top_display(PIN_TOP_CLK, PIN_TOP_DIO);
TM1637 bot_display(PIN_BOT_CLK, PIN_BOT_DIO);

int LED = PC13;

void setup_display(TM1637* disp) {
	disp->set(7); // Max brightness
	disp->init();

	delay(10);
	int8_t data[] = {8, 8, 8, 8};
	disp->display(data);
	delay(3000);
	disp->clearDisplay();
	delay(1000);
}

void setup() {
	setup_display(&top_display);
	setup_display(&bot_display);

	pinMode(LED, OUTPUT);
}


void loop() {
	digitalWrite(LED, HIGH);
	delay(500);
	digitalWrite(LED, LOW);
	delay(500);

	bot_display.displayNum(millis() % 10000);
	top_display.displayNum(millis() % 10000);
}
