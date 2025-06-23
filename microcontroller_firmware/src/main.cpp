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

// Made this function so we can adjust it easiler later like to use interrupts
// This can only return 
EncoderState check_encoder() {
	static int last_button_state = LOW;
	int current_button_state = digitalRead(PIN_ENC_BUT);
	bool button_changed = last_button_state != current_button_state;
	last_button_state = current_button_state;

	if (button_changed && (current_button_state == ACTIVE_ENC_BUT)) return ENCODER_BUTTON_PRESS;

	static int last_encoder_state = LOW;
	int current_encoder_state = digitalRead(PIN_ENC_CLK);
	bool encoder_changed = last_encoder_state != current_encoder_state;
	last_encoder_state = current_button_state; 

	// Only sending encoder updates on a falling edge
	if (encoder_changed == false || current_encoder_state == HIGH) return ENCODER_NO_INPUT; 
	
	if (digitalRead(PIN_ENC_DIR) == FORWARD_ENC_DIR) return ENCODER_SPIN_FWD;
	else return ENCODER_SPIN_REV;
}

TM1637 top_display(PIN_TOP_CLK, PIN_TOP_DIO);
TM1637 bot_display(PIN_BOT_CLK, PIN_BOT_DIO);

USBKeyboard keyboard_interface(true);

void setup_display(TM1637* disp) {
	disp->set(7); // Max brightness
	disp->init();

	delay(10);
	int8_t data[] = {8, 8, 8, 8}; // Illuminate all segments for checking
	disp->display(data);
	delay(3000);
	disp->clearDisplay();
	delay(1000);
}

void setup() {
	pinMode(PIN_LED, OUTPUT);

	setup_display(&top_display);
	setup_display(&bot_display);

	if (ACTIVE_ENC_BUT == HIGH) pinMode(PIN_ENC_BUT, INPUT_PULLDOWN);
	else pinMode(PIN_ENC_BUT, INPUT_PULLUP);
	pinMode(PIN_ENC_CLK, INPUT_PULLDOWN);
	pinMode(PIN_ENC_DIR, INPUT_PULLDOWN);
}

void loop() {
	EncoderState state = check_encoder();
	bot_display.displayNum(millis() % 10000);
	top_display.displayNum(state);

	switch (state) {
	case ENCODER_SPIN_FWD:
		keyboard_interface.key_code('f');
		break;
	case ENCODER_BUTTON_PRESS:
		keyboard_interface.key_code('p');
		break;
	case ENCODER_SPIN_REV:
		keyboard_interface.key_code('r');
		break;
	default:
		break;
	}

	delay(10);
}
