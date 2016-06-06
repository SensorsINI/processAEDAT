#ifndef CALIBRATION_WRAPPER_H_
#define CALIBRATION_WRAPPER_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "calibration_settings.h"

typedef struct Calibration Calibration;

Calibration *calibration_init(CameraCalibrationSettings settings);
void calibration_destroy(Calibration *calibClass);
void calibration_updateSettings(Calibration *calibClass);
bool calibration_findNewPoints(Calibration *calibClass, caerFrameEvent frame);
size_t calibration_foundPoints(Calibration *calibClass);
bool calibration_runCalibrationAndSave(Calibration *calibClass, double *totalAvgError);
bool calibration_loadUndistortMatrices(Calibration *calibClass);
void calibration_undistortEvent(Calibration *calibClass, caerPolarityEvent polarity,
	caerPolarityEventPacket polarityPacket);
void calibration_undistortFrame(Calibration *calibClass, caerFrameEvent frame);

#ifdef __cplusplus
}
#endif

#endif /* CALIBRATION_WRAPPER_H_ */
