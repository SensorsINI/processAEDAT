/*
 * backgroundactivityfilter.h
 *
 *  Created on: Jan 20, 2014
 *      Author: chtekk
 */

#ifndef BACKGROUNDACTIVITYFILTER_H_
#define BACKGROUNDACTIVITYFILTER_H_

#include "main.h"

#include <libcaer/events/polarity.h>

void caerBackgroundActivityFilter(uint16_t moduleID, caerPolarityEventPacket polarity);

#endif /* BACKGROUNDACTIVITYFILTER_H_ */
