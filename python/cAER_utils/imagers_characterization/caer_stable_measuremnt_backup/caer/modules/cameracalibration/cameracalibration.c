#include "cameracalibration.h"
#include "calibration_settings.h"
#include "calibration_wrapper.h"
#include "base/mainloop.h"
#include "base/module.h"

struct CameraCalibrationState_struct {
	struct CameraCalibrationSettings_struct settings; // Struct containing all settings (shared)
	struct Calibration *cpp_class; // Pointer to cpp_class_object
	uint64_t lastFrameTimestamp;
	size_t lastFoundPoints;
	bool calibrationCompleted;
	bool calibrationLoaded;
};

typedef struct CameraCalibrationState_struct *CameraCalibrationState;

static bool caerCameraCalibrationInit(caerModuleData moduleData);
static void caerCameraCalibrationRun(caerModuleData moduleData, size_t argsNumber, va_list args);
static void caerCameraCalibrationConfig(caerModuleData moduleData);
static void caerCameraCalibrationExit(caerModuleData moduleData);
static void updateSettings(caerModuleData moduleData);

static struct caer_module_functions caerCameraCalibrationFunctions = { .moduleInit = &caerCameraCalibrationInit,
	.moduleRun = &caerCameraCalibrationRun, .moduleConfig = &caerCameraCalibrationConfig, .moduleExit =
		&caerCameraCalibrationExit };

void caerCameraCalibration(uint16_t moduleID, caerPolarityEventPacket polarity, caerFrameEventPacket frame) {
	caerModuleData moduleData = caerMainloopFindModule(moduleID, "CameraCalibration");

	caerModuleSM(&caerCameraCalibrationFunctions, moduleData, sizeof(struct CameraCalibrationState_struct), 2, polarity,
		frame);
}

static bool caerCameraCalibrationInit(caerModuleData moduleData) {
	CameraCalibrationState state = moduleData->moduleState;

	// Create config settings.
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "doCalibration", false); // Do calibration using live images
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "saveFileName", "camera_calib.xml"); // The name of the file where to write the calculated calibration settings
	sshsNodePutIntIfAbsent(moduleData->moduleNode, "captureDelay", 500000); // Only use a frame for calibration if at least this much time has passed
	sshsNodePutIntIfAbsent(moduleData->moduleNode, "minNumberOfPoints", 20); // Minimum number of points to start calibration with.
	sshsNodePutFloatIfAbsent(moduleData->moduleNode, "maxTotalError", 0.30f); // Maximum total average error allowed (in pixels).
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "calibrationPattern", "chessboard"); // One of the Chessboard, circles, or asymmetric circle pattern
	sshsNodePutIntIfAbsent(moduleData->moduleNode, "boardWidth", 9); // The size of the board (width)
	sshsNodePutIntIfAbsent(moduleData->moduleNode, "boardHeigth", 5); // The size of the board (heigth)
	sshsNodePutFloatIfAbsent(moduleData->moduleNode, "boardSquareSize", 1.0f); // The size of a square in your defined unit (point, millimeter, etc.)
	sshsNodePutFloatIfAbsent(moduleData->moduleNode, "aspectRatio", 0); // The aspect ratio
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "assumeZeroTangentialDistortion", false); // Assume zero tangential distortion
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "fixPrincipalPointAtCenter", false); // Fix the principal point at the center
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "useFisheyeModel", false); // Use Fisheye camera model for calibration

	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "doUndistortion", false); // Do undistortion of incoming images using calibration loaded from file
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "loadFileName", "camera_calib.xml"); // The name of the file from which to load the calibration settings for undistortion
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "fitAllPixels", false); // Whether to fit all the input pixels (black borders) or maximize the image, at the cost of loosing some pixels.

	// Update all settings.
	updateSettings(moduleData);

	// Initialize C++ class for OpenCV integration.
	state->cpp_class = calibration_init(&state->settings);
	if (state->cpp_class == NULL) {
		return (false);
	}

	// Add config listeners last, to avoid having them dangling if Init doesn't succeed.
	sshsNodeAddAttributeListener(moduleData->moduleNode, moduleData, &caerModuleConfigDefaultListener);

	return (true);
}

static void updateSettings(caerModuleData moduleData) {
	CameraCalibrationState state = moduleData->moduleState;

	// Get current config settings.
	state->settings.doCalibration = sshsNodeGetBool(moduleData->moduleNode, "doCalibration");
	state->settings.captureDelay = U32T(sshsNodeGetInt(moduleData->moduleNode, "captureDelay"));
	state->settings.minNumberOfPoints = U32T(sshsNodeGetInt(moduleData->moduleNode, "minNumberOfPoints"));
	state->settings.maxTotalError = sshsNodeGetFloat(moduleData->moduleNode, "maxTotalError");
	state->settings.boardWidth = U32T(sshsNodeGetInt(moduleData->moduleNode, "boardWidth"));
	state->settings.boardHeigth = U32T(sshsNodeGetInt(moduleData->moduleNode, "boardHeigth"));
	state->settings.boardSquareSize = sshsNodeGetFloat(moduleData->moduleNode, "boardSquareSize");
	state->settings.aspectRatio = sshsNodeGetFloat(moduleData->moduleNode, "aspectRatio");
	state->settings.assumeZeroTangentialDistortion = sshsNodeGetBool(moduleData->moduleNode,
		"assumeZeroTangentialDistortion");
	state->settings.fixPrincipalPointAtCenter = sshsNodeGetBool(moduleData->moduleNode, "fixPrincipalPointAtCenter");
	state->settings.useFisheyeModel = sshsNodeGetBool(moduleData->moduleNode, "useFisheyeModel");
	state->settings.doUndistortion = sshsNodeGetBool(moduleData->moduleNode, "doUndistortion");
	state->settings.fitAllPixels = sshsNodeGetBool(moduleData->moduleNode, "fitAllPixels");

	// Parse calibration pattern string.
	char *calibPattern = sshsNodeGetString(moduleData->moduleNode, "calibrationPattern");

	if (caerStrEquals(calibPattern, "chessboard")) {
		state->settings.calibrationPattern = CAMCALIB_CHESSBOARD;
	}
	else if (caerStrEquals(calibPattern, "circlesGrid")) {
		state->settings.calibrationPattern = CAMCALIB_CIRCLES_GRID;
	}
	else if (caerStrEquals(calibPattern, "asymmetricCirclesGrid")) {
		state->settings.calibrationPattern = CAMCALIB_ASYMMETRIC_CIRCLES_GRID;
	}
	else {
		caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString,
			"Invalid calibration pattern defined. Select one of: chessboard, circlesGrid or asymmetricCirclesGrid. Defaulting to chessboard.");

		state->settings.calibrationPattern = CAMCALIB_CHESSBOARD;
	}

	free(calibPattern);

	// Get file strings.
	state->settings.saveFileName = sshsNodeGetString(moduleData->moduleNode, "saveFileName");
	state->settings.loadFileName = sshsNodeGetString(moduleData->moduleNode, "loadFileName");
}

static void caerCameraCalibrationConfig(caerModuleData moduleData) {
	caerModuleConfigUpdateReset(moduleData);

	CameraCalibrationState state = moduleData->moduleState;

	// Free filename strings, get reloaded in next step.
	free(state->settings.saveFileName);
	free(state->settings.loadFileName);

	// Reload all local settings.
	updateSettings(moduleData);

	// Update the C++ internal state, based on new settings.
	calibration_updateSettings(state->cpp_class);

	// Reset calibration status after any config change.
	state->lastFrameTimestamp = 0;
	state->lastFoundPoints = 0;
	state->calibrationCompleted = false;
	state->calibrationLoaded = false;
}

static void caerCameraCalibrationExit(caerModuleData moduleData) {
	// Remove listener, which can reference invalid memory in userData.
	sshsNodeRemoveAttributeListener(moduleData->moduleNode, moduleData, &caerModuleConfigDefaultListener);

	CameraCalibrationState state = moduleData->moduleState;

	calibration_destroy(state->cpp_class);

	free(state->settings.saveFileName);
	free(state->settings.loadFileName);
}

static void caerCameraCalibrationRun(caerModuleData moduleData, size_t argsNumber, va_list args) {
	UNUSED_ARGUMENT(argsNumber);

	// Interpret variable arguments (same as above in main function).
	caerPolarityEventPacket polarity = va_arg(args, caerPolarityEventPacket);
	caerFrameEventPacket frame = va_arg(args, caerFrameEventPacket);

	CameraCalibrationState state = moduleData->moduleState;

	// As soon as we have a packet, we can get the source ID and initialize the image size.
	if (polarity != NULL || frame != NULL) {
		int16_t sourceID = -1;

		if (polarity != NULL) {
			sourceID = caerEventPacketHeaderGetEventSource(&polarity->packetHeader);
		}

		if (frame != NULL) {
			sourceID = caerEventPacketHeaderGetEventSource(&frame->packetHeader);
		}

		// At this point we must have a valid source ID.
		// Get size information from source.
		sshsNode sourceInfoNode = caerMainloopGetSourceInfo((uint16_t) sourceID);
		state->settings.imageWidth = U32T(sshsNodeGetShort(sourceInfoNode, "apsSizeX"));
		state->settings.imageHeigth = U32T(sshsNodeGetShort(sourceInfoNode, "apsSizeY"));
	}

	// Calibration is done only using frames.
	if (state->settings.doCalibration && !state->calibrationCompleted && frame != NULL) {
		CAER_FRAME_ITERATOR_VALID_START(frame)
			// Only work on new frames if enough time has passed between this and the last used one.
			uint64_t currTimestamp = U64T(caerFrameEventGetTSStartOfFrame64(caerFrameIteratorElement, frame));

			// If enough time has passed, try to add a new point set.
			if ((currTimestamp - state->lastFrameTimestamp) >= state->settings.captureDelay) {
				state->lastFrameTimestamp = currTimestamp;

				bool foundPoint = calibration_findNewPoints(state->cpp_class, caerFrameIteratorElement);
				caerLog(CAER_LOG_WARNING, moduleData->moduleSubSystemString,
					"Searching for new point set, result = %d.", foundPoint);
			}
		CAER_FRAME_ITERATOR_VALID_END

		// If enough points have been found in this round, try doing calibration.
		size_t foundPoints = calibration_foundPoints(state->cpp_class);

		if (foundPoints >= state->settings.minNumberOfPoints && foundPoints > state->lastFoundPoints) {
			state->lastFoundPoints = foundPoints;

			double totalAvgError;
			state->calibrationCompleted = calibration_runCalibrationAndSave(state->cpp_class, &totalAvgError);
			caerLog(CAER_LOG_WARNING, moduleData->moduleSubSystemString,
				"Executing calibration, result = %d, error = %f.", state->calibrationCompleted, totalAvgError);
		}
	}

	// At this point we always try to load the calibration settings for undistortion.
	// Maybe they just got created or exist from a previous run.
	if (state->settings.doUndistortion && !state->calibrationLoaded) {
		state->calibrationLoaded = calibration_loadUndistortMatrices(state->cpp_class);
	}

	// Undistortion can be applied to both frames and events.
	if (state->settings.doUndistortion && state->calibrationLoaded) {
		if (frame != NULL) {
			CAER_FRAME_ITERATOR_VALID_START(frame)
				calibration_undistortFrame(state->cpp_class, caerFrameIteratorElement);
			CAER_FRAME_ITERATOR_VALID_END
		}

		if (polarity != NULL) {
			CAER_POLARITY_ITERATOR_VALID_START(polarity)
				calibration_undistortEvent(state->cpp_class, caerPolarityIteratorElement, polarity);
			CAER_POLARITY_ITERATOR_VALID_END
		}
	}
}
