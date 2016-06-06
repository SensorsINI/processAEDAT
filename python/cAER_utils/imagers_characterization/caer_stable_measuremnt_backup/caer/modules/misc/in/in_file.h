/*
 * file.h (input) 
 *
 *  Created on: Okt 29, 2015
 *      Author: phineasng
 */

#ifndef FILE_INPUT_H_
#define FILE_INPUT_H_

#include "in_common.h"
#include <libcaer/events/packetContainer.h>

caerEventPacketContainer caerInputFile(uint16_t moduleID);

#endif /* FILE_INPUT_H_ */
