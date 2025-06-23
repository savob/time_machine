#ifndef _PIN_ALLOCATIONS_H
#define _PIN_ALLOCATIONS_H

#include <PinNames.h>

#define PIN_LED		PC_13		// For debugging purposes

#define PIN_TOP_CLK PB_8
#define PIN_TOP_DIO PB_9

#define PIN_BOT_CLK PB_6
#define PIN_BOT_DIO PB_7

#define PIN_ENC_BUT PA_3        // Button pin for the encoder when pressed
#define PIN_ENC_CLK PA_4        // "Clock" pin for the encoder, really just one phase
#define PIN_ENC_DIR PA_5        // "Direction" pin for the encoder, really just one phase

#define ACTIVE_ENC_BUT  LOW     // Active state of user button
#define FORWARD_ENC_DIR HIGH    // What state DIR needs to be to count as turning "forward"

#endif