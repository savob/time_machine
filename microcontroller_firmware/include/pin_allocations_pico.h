#ifndef _PIN_ALLOCATIONS_H
#define _PIN_ALLOCATIONS_H

#include <PinNames.h>

#define PIN_LED		25		// For debugging purposes

#define PIN_TOP_CLK 7
#define PIN_TOP_DIO 8

#define PIN_BOT_CLK 9
#define PIN_BOT_DIO 10

#define PIN_ENC_BUT 11		// Button pin for the encoder when pressed
#define PIN_ENC_CLK 12		// "Clock" pin for the encoder, really just one phase
#define PIN_ENC_DIR 13		// "Direction" pin for the encoder, really just one phase

#define ACTIVE_ENC_BUT	LOW		// Active state of user button
#define FORWARD_ENC_DIR	HIGH	// What state DIR needs to be to count as turning "forward"

#endif