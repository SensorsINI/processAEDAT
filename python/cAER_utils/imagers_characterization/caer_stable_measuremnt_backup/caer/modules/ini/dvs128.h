/*
 * dvs128.h
 *
 *  Created on: Nov 26, 2013
 *      Author: chtekk
 */

#ifndef DVS128_H_
#define DVS128_H_

#include "main.h"

#include <libcaer/events/packetContainer.h>
#include <libcaer/events/special.h>
#include <libcaer/events/polarity.h>

caerEventPacketContainer caerInputDVS128(uint16_t moduleID);

#endif /* DVS128_H_ */
