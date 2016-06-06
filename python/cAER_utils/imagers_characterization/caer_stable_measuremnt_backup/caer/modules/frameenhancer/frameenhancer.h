#ifndef FRAMEENHANCER_H_
#define FRAMEENHANCER_H_

#include "main.h"

#include <libcaer/events/frame.h>

caerFrameEventPacket caerFrameEnhancer(uint16_t moduleID, caerFrameEventPacket frame);

#endif /* FRAMEENHANCER_H_ */
