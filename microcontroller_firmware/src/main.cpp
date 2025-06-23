#include <Arduino.h>
#include "TM1637.h"
#include <USBKeyboard.h>

#include "pin_allocations_pico.h"

typedef enum _EncoderState {
	ENCODER_NO_INPUT = 0,
	ENCODER_BUTTON_PRESS,
	ENCODER_SPIN_FWD,
	ENCODER_SPIN_REV,
} EncoderState;

TM1637 top_display(PIN_TOP_CLK, PIN_TOP_DIO);
TM1637 bot_display(PIN_BOT_CLK, PIN_BOT_DIO);

USBKeyboard keyboard_interface(true);

volatile EncoderState turning_state = ENCODER_NO_INPUT;

void encoder_interrupt() {
	const unsigned long DEBOUNCE_MS = 40;
	static unsigned long next_interrupt_ms = 0; // Mark next allowed edge event

	unsigned long current_ms = millis();

	if (current_ms < next_interrupt_ms) return;
	next_interrupt_ms = current_ms + DEBOUNCE_MS;

	if (digitalRead(PIN_ENC_DIR) == FORWARD_ENC_DIR) turning_state = ENCODER_SPIN_FWD;
	else turning_state = ENCODER_SPIN_REV;

	// To avoid the occasional reverse signal when one stopsfffrfrfrfffrrr turning
	static EncoderState previous_turning_state = ENCODER_SPIN_FWD;
	const uint_fast8_t NEEDED_COUNTS_TO_SWITCH = 2;
	static uint_fast8_t opposite_counts = 0;

	if (turning_state == previous_turning_state) {
		opposite_counts = 0;
		return;
	}
	
	opposite_counts++;
	if (opposite_counts < NEEDED_COUNTS_TO_SWITCH) turning_state = ENCODER_NO_INPUT;
	else {
		previous_turning_state = turning_state;
		opposite_counts = 0;
	}
}

// Made this function so we can adjust it easiler later like to use interrupts
// This can only return one action per check 
EncoderState check_encoder() {
	static int last_button_state = LOW;
	int current_button_state = digitalRead(PIN_ENC_BUT);
	bool button_changed = last_button_state != current_button_state;
	last_button_state = current_button_state;

	if (button_changed && (current_button_state == ACTIVE_ENC_BUT)) return ENCODER_BUTTON_PRESS;

	// See if the encoder had anything happen
	EncoderState return_val = turning_state;
	turning_state = ENCODER_NO_INPUT;
	return return_val;
}

void send_character(char data) {
	keyboard_interface.key_code(data);
	Serial.println(data);
}

void setup_display(TM1637* disp) {
	disp->set(7); // Max brightness
	disp->init();

	delay(10);
	int8_t data[] = {8, 8, 8, 8}; // Illuminate all segments for checking
	disp->display(data);
	delay(1000);
	disp->clearDisplay();
	delay(500);

	Serial.begin(115200); // Used to get data for displays 
}

void setup() {
	pinMode(PIN_LED, OUTPUT);

	setup_display(&top_display);
	setup_display(&bot_display);

	if (ACTIVE_ENC_BUT == HIGH) pinMode(PIN_ENC_BUT, INPUT_PULLDOWN);
	else pinMode(PIN_ENC_BUT, INPUT_PULLUP);
	pinMode(PIN_ENC_CLK, INPUT_PULLDOWN);
	pinMode(PIN_ENC_DIR, INPUT_PULLDOWN);
	attachInterrupt(PIN_ENC_CLK, encoder_interrupt, FALLING);
}

void loop() {
	EncoderState state = check_encoder();
	
	switch (state) {
		case ENCODER_SPIN_FWD:
		send_character('f');
		break;
		case ENCODER_BUTTON_PRESS:
		send_character('p');
		break;
		case ENCODER_SPIN_REV:
		send_character('r');
		break;
		default:
		break;
	}

	if (Serial.available()) {
		uint32_t time_code = Serial.parseInt(SKIP_WHITESPACE);

		uint16_t year_code = time_code / 10000;
		uint16_t date_code = time_code % 10000;

		top_display.displayNum(year_code);
		bot_display.displayNum(date_code);
		if (date_code < 1000) bot_display.display(0, '0'); // Add leading zero for date codes if needed (e.g. _625)
	}
	
	delay(1);
}
