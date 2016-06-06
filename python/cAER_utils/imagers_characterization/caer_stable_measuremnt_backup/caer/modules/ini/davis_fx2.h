#ifndef DAVIS_FX2_H_
#define DAVIS_FX2_H_

#include "main.h"

#include <libcaer/events/packetContainer.h>
#include <libcaer/events/special.h>
#include <libcaer/events/polarity.h>
#include <libcaer/events/frame.h>
#include <libcaer/events/imu6.h>

caerEventPacketContainer caerInputDAVISFX2(uint16_t moduleID);

#endif /* DAVIS_FX2_H_ */
