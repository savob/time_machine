#ifndef _PIN_ALLOCATIONS_H
#define _PIN_ALLOCATIONS_H

#include <PinNames.h>

#define PIN_LED		25		// For debugging purposes

#define PIN_BOT_CLK 16
#define PIN_BOT_DIO 17

#define PIN_TOP_CLK 19
#define PIN_TOP_DIO 20

#define PIN_ENC_BUT 6		// Button pin for the encoder when pressed
#define PIN_ENC_CLK 9		// "Clock" pin for the encoder, really just one phase
#define PIN_ENC_DIR 7		// "Direction" pin for the encoder, really just one phase

#define ACTIVE_ENC_BUT	LOW	// Active state of user button
#define FORWARD_ENC_DIR	LOW	// What state DIR needs to be to count as turning "forward"


#endif