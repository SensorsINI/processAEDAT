#ifndef CALIBRATION_HPP_
#define CALIBRATION_HPP_

#include <iostream>
#include <sstream>
#include <time.h>
#include <stdio.h>
#include "calibration_settings.h"

#include <libcaer/events/polarity.h>
#include <libcaer/events/frame.h>

#include <opencv2/core.hpp>
#include <opencv2/core/utility.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/calib3d.hpp>

using namespace cv;
using namespace std;

class Calibration {

public:
	Calibration(CameraCalibrationSettings settings);
	void updateSettings(void);
	bool findNewPoints(caerFrameEvent frame);
	size_t foundPoints(void);
	bool runCalibrationAndSave(double *totalAvgError);

	bool loadUndistortMatrices(void);
	void undistortEvent(caerPolarityEvent polarity, caerPolarityEventPacket polarityPacket);
	void undistortFrame(caerFrameEvent frame);

private:
	CameraCalibrationSettings settings = NULL;
	int flag = 0;
	Size boardSize;

	vector<vector<Point2f> > imagePoints;
	Mat cameraMatrix;
	Mat distCoeffs;

	vector<Point2i> undistortEventMap;
	Mat undistortRemap1;
	Mat undistortRemap2;

	double computeReprojectionErrors(const vector<vector<Point3f> >& objectPoints,
		const vector<vector<Point2f> >& imagePoints, const vector<Mat>& rvecs, const vector<Mat>& tvecs,
		const Mat& cameraMatrix, const Mat& distCoeffs, vector<float>& perViewErrors, bool fisheye);
	void calcBoardCornerPositions(Size boardSize, float squareSize, vector<Point3f>& corners,
		enum CameraCalibrationPattern patternType);
	bool runCalibration(Size& imageSize, Mat& cameraMatrix, Mat& distCoeffs,
		vector<vector<Point2f> > imagePoints, vector<float>& reprojErrs, double& totalAvgErr);
	bool saveCameraParams(Size& imageSize, Mat& cameraMatrix, Mat& distCoeffs, const vector<float>& reprojErrs,
		double totalAvgErr);
};

#endif /* CALIBRATION_HPP_ */
