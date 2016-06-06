#include "calibration.hpp"
#include "calibration_wrapper.h"

Calibration *calibration_init(CameraCalibrationSettings settings) {
	try {
		return (new Calibration(settings));
	}
	catch (const std::exception& ex) {
		caerLog(CAER_LOG_ERROR, "calibration_init()", "Failed with C++ exception: %s", ex.what());
		return (NULL);
	}
}

void calibration_destroy(Calibration *calibClass) {
	try {
		delete calibClass;
	}
	catch (const std::exception& ex) {
		caerLog(CAER_LOG_ERROR, "calibration_destroy()", "Failed with C++ exception: %s", ex.what());
	}
}

void calibration_updateSettings(Calibration *calibClass) {
	try {
		calibClass->updateSettings();
	}
	catch (const std::exception& ex) {
		caerLog(CAER_LOG_ERROR, "calibration_updateSettings()", "Failed with C++ exception: %s", ex.what());
	}
}

bool calibration_findNewPoints(Calibration *calibClass, caerFrameEvent frame) {
	try {
		return (calibClass->findNewPoints(frame));
	}
	catch (const std::exception& ex) {
		caerLog(CAER_LOG_ERROR, "calibration_findNewPoints()", "Failed with C++ exception: %s", ex.what());
		return (false);
	}
}

size_t calibration_foundPoints(Calibration *calibClass) {
	try {
		return (calibClass->foundPoints());
	}
	catch (const std::exception& ex) {
		caerLog(CAER_LOG_ERROR, "calibration_foundPoints()", "Failed with C++ exception: %s", ex.what());
		return (0);
	}
}

bool calibration_runCalibrationAndSave(Calibration *calibClass, double *totalAvgError) {
	try {
		return (calibClass->runCalibrationAndSave(totalAvgError));
	}
	catch (const std::exception& ex) {
		caerLog(CAER_LOG_ERROR, "calibration_runCalibrationAndSave()", "Failed with C++ exception: %s", ex.what());
		return (false);
	}
}

bool calibration_loadUndistortMatrices(Calibration *calibClass) {
	try {
		return (calibClass->loadUndistortMatrices());
	}
	catch (const std::exception& ex) {
		caerLog(CAER_LOG_ERROR, "calibration_loadUndistortMatrices()", "Failed with C++ exception: %s", ex.what());
		return (false);
	}
}

void calibration_undistortEvent(Calibration *calibClass, caerPolarityEvent polarity,
	caerPolarityEventPacket polarityPacket) {
	try {
		calibClass->undistortEvent(polarity, polarityPacket);
	}
	catch (const std::exception& ex) {
		caerLog(CAER_LOG_ERROR, "calibration_undistortEvent()", "Failed with C++ exception: %s", ex.what());
	}
}

void calibration_undistortFrame(Calibration *calibClass, caerFrameEvent frame) {
	try {
		calibClass->undistortFrame(frame);
	}
	catch (const std::exception& ex) {
		caerLog(CAER_LOG_ERROR, "calibration_undistortFrame()", "Failed with C++ exception: %s", ex.what());
	}
}
