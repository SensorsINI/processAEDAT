#ifndef CAMERACALIBRATION_H_
#define CAMERACALIBRATION_H_

#include "main.h"

#include <libcaer/events/polarity.h>
#include <libcaer/events/frame.h>

void caerCameraCalibration(uint16_t moduleID, caerPolarityEventPacket polarity, caerFrameEventPacket frame);

#endif /* CAMERACALIBRATION_H_ */
