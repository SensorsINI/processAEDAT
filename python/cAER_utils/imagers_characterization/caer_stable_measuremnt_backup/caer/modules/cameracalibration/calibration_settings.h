#ifndef CALIBRATION_SETTINGS_H_
#define CALIBRATION_SETTINGS_H_

enum CameraCalibrationPattern { CAMCALIB_CHESSBOARD, CAMCALIB_CIRCLES_GRID, CAMCALIB_ASYMMETRIC_CIRCLES_GRID };

struct CameraCalibrationSettings_struct {
	bool doCalibration;
	char *saveFileName;
	uint32_t captureDelay;
	uint32_t minNumberOfPoints;
	float maxTotalError;
	enum CameraCalibrationPattern calibrationPattern;
	uint32_t boardWidth;
	uint32_t boardHeigth;
	float boardSquareSize;
	float aspectRatio;
	bool assumeZeroTangentialDistortion;
	bool fixPrincipalPointAtCenter;
	bool useFisheyeModel;
	bool doUndistortion;
	char *loadFileName;
	bool fitAllPixels;
	uint32_t imageWidth;
	uint32_t imageHeigth;
};

typedef struct CameraCalibrationSettings_struct *CameraCalibrationSettings;

#endif /* CALIBRATION_SETTINGS_H_ */
