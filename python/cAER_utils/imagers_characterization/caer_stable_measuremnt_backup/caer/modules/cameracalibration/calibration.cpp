#include "calibration.hpp"

Calibration::Calibration(CameraCalibrationSettings settings) {
	this->settings = settings;

	updateSettings();
}

void Calibration::updateSettings(void) {
	if (settings->useFisheyeModel) {
		// The fisheye model has its own enum, so overwrite the flags.
		flag = fisheye::CALIB_FIX_SKEW | fisheye::CALIB_RECOMPUTE_EXTRINSIC | fisheye::CALIB_FIX_K2
			| fisheye::CALIB_FIX_K3 | fisheye::CALIB_FIX_K4;
	}
	else {
		flag = CALIB_FIX_K4 | CALIB_FIX_K5;

		if (settings->aspectRatio) {
			flag |= CALIB_FIX_ASPECT_RATIO;
		}

		if (settings->assumeZeroTangentialDistortion) {
			flag |= CALIB_ZERO_TANGENT_DIST;
		}

		if (settings->fixPrincipalPointAtCenter) {
			flag |= CALIB_FIX_PRINCIPAL_POINT;
		}
	}

	// Update board size.
	boardSize.width = settings->boardWidth;
	boardSize.height = settings->boardHeigth;

	// Clear current image points.
	imagePoints.clear();
}

bool Calibration::findNewPoints(caerFrameEvent frame) {
	if (frame == NULL || !caerFrameEventIsValid(frame)) {
		return (false);
	}

	// Initialize OpenCV Mat based on caerFrameEvent data directly (no image copy).
	Size frameSize(caerFrameEventGetLengthX(frame), caerFrameEventGetLengthY(frame));
	Mat orig(frameSize, CV_16UC(caerFrameEventGetChannelNumber(frame)), caerFrameEventGetPixelArrayUnsafe(frame));

	// Create a new Mat that has only 8 bit depth from the original 16 bit one.
	// findCorner functions in OpenCV only support 8 bit depth.
	Mat view;
	orig.convertTo(view, CV_8UC(orig.channels()), 1.0 / 256.0);

	int chessBoardFlags = CALIB_CB_ADAPTIVE_THRESH | CALIB_CB_NORMALIZE_IMAGE;

	if (!settings->useFisheyeModel) {
		// Fast check erroneously fails with high distortions like fisheye lens.
		chessBoardFlags |= CALIB_CB_FAST_CHECK;
	}

	// Find feature points on the input image.
	vector<Point2f> pointBuf;
	bool found;

	switch (settings->calibrationPattern) {
		case CAMCALIB_CHESSBOARD:
			found = findChessboardCorners(view, boardSize, pointBuf, chessBoardFlags);
			break;

		case CAMCALIB_CIRCLES_GRID:
			found = findCirclesGrid(view, boardSize, pointBuf);
			break;

		case CAMCALIB_ASYMMETRIC_CIRCLES_GRID:
			found = findCirclesGrid(view, boardSize, pointBuf, CALIB_CB_ASYMMETRIC_GRID);
			break;

		default:
			found = false;
			break;
	}

	if (found) {
		// Improve the found corners' coordinate accuracy for chessboard pattern.
		if (settings->calibrationPattern == CAMCALIB_CHESSBOARD) {
			Mat viewGray;

			// Only convert color if not grayscale already.
			if (view.channels() == GRAYSCALE) {
				viewGray = view;
			}
			else {
				if (view.channels() == RGB) {
					cvtColor(view, viewGray, COLOR_RGB2GRAY);
				}
				else if (view.channels() == RGBA) {
					cvtColor(view, viewGray, COLOR_RGBA2GRAY);
				}
			}

			cornerSubPix(viewGray, pointBuf, Size(5, 5), Size(-1, -1),
				TermCriteria(TermCriteria::EPS + TermCriteria::COUNT, 30, 0.1));
		}

		imagePoints.push_back(pointBuf);
	}

	return (found);
}

size_t Calibration::foundPoints(void) {
	return (imagePoints.size());
}

double Calibration::computeReprojectionErrors(const vector<vector<Point3f> >& objectPoints,
	const vector<vector<Point2f> >& imagePoints, const vector<Mat>& rvecs, const vector<Mat>& tvecs,
	const Mat& cameraMatrix, const Mat& distCoeffs, vector<float>& perViewErrors, bool fisheye) {
	vector<Point2f> imagePoints2;
	size_t totalPoints = 0;
	double totalErr = 0;
	double err;

	perViewErrors.resize(objectPoints.size());

	for (size_t i = 0; i < objectPoints.size(); i++) {
		if (fisheye) {
			fisheye::projectPoints(objectPoints[i], imagePoints2, rvecs[i], tvecs[i], cameraMatrix, distCoeffs);
		}
		else {
			projectPoints(objectPoints[i], rvecs[i], tvecs[i], cameraMatrix, distCoeffs, imagePoints2);
		}

		err = norm(imagePoints[i], imagePoints2, NORM_L2);

		size_t n = objectPoints[i].size();
		perViewErrors[i] = (float) std::sqrt(err * err / n);
		totalErr += err * err;
		totalPoints += n;
	}

	return (std::sqrt(totalErr / totalPoints));
}

void Calibration::calcBoardCornerPositions(Size boardSize, float squareSize, vector<Point3f>& corners,
	enum CameraCalibrationPattern patternType) {
	corners.clear();

	switch (patternType) {
		case CAMCALIB_CHESSBOARD:
		case CAMCALIB_CIRCLES_GRID:
			for (int y = 0; y < boardSize.height; y++) {
				for (int x = 0; x < boardSize.width; x++) {
					corners.push_back(Point3f(x * squareSize, y * squareSize, 0));
				}
			}
			break;

		case CAMCALIB_ASYMMETRIC_CIRCLES_GRID:
			for (int y = 0; y < boardSize.height; y++) {
				for (int x = 0; x < boardSize.width; x++) {
					corners.push_back(Point3f((2 * x + y % 2) * squareSize, y * squareSize, 0));
				}
			}
			break;

		default:
			break;
	}
}

bool Calibration::runCalibration(Size& imageSize, Mat& cameraMatrix, Mat& distCoeffs,
	vector<vector<Point2f> > imagePoints, vector<float>& reprojErrs, double& totalAvgErr) {
	// 3x3 camera matrix to fill in.
	cameraMatrix = Mat::eye(3, 3, CV_64F);

	if (flag & CALIB_FIX_ASPECT_RATIO) {
		cameraMatrix.at<double>(0, 0) = settings->aspectRatio;
	}

	if (settings->useFisheyeModel) {
		distCoeffs = Mat::zeros(4, 1, CV_64F);
	}
	else {
		distCoeffs = Mat::zeros(8, 1, CV_64F);
	}

	vector<vector<Point3f> > objectPoints(1);

	calcBoardCornerPositions(boardSize, settings->boardSquareSize, objectPoints[0], settings->calibrationPattern);

	objectPoints.resize(imagePoints.size(), objectPoints[0]);

	// Find intrinsic and extrinsic camera parameters.
	vector<Mat> rvecs, tvecs;

	if (settings->useFisheyeModel) {
		Mat _rvecs, _tvecs;
		fisheye::calibrate(objectPoints, imagePoints, imageSize, cameraMatrix, distCoeffs, _rvecs, _tvecs, flag);

		rvecs.reserve(_rvecs.rows);
		tvecs.reserve(_tvecs.rows);

		for (size_t i = 0; i < objectPoints.size(); i++) {
			rvecs.push_back(_rvecs.row(i));
			tvecs.push_back(_tvecs.row(i));
		}
	}
	else {
		calibrateCamera(objectPoints, imagePoints, imageSize, cameraMatrix, distCoeffs, rvecs, tvecs, flag);
	}

	totalAvgErr = computeReprojectionErrors(objectPoints, imagePoints, rvecs, tvecs, cameraMatrix, distCoeffs,
		reprojErrs, settings->useFisheyeModel);

	bool ok = checkRange(cameraMatrix) && checkRange(distCoeffs) && totalAvgErr < settings->maxTotalError;

	return (ok);
}

// Print camera parameters to the output file
bool Calibration::saveCameraParams(Size& imageSize, Mat& cameraMatrix, Mat& distCoeffs, const vector<float>& reprojErrs,
	double totalAvgErr) {
	FileStorage fs(settings->saveFileName, FileStorage::WRITE);

	// Check file.
	if (!fs.isOpened()) {
		return (false);
	}

	time_t tm;
	time(&tm);
	struct tm *t2 = localtime(&tm);
	char buf[1024];
	strftime(buf, sizeof(buf) - 1, "%c", t2);

	fs << "calibration_time" << buf;

	if (!reprojErrs.empty()) {
		fs << "nr_of_frames" << (int) reprojErrs.size();
	}

	fs << "image_width" << imageSize.width;
	fs << "image_height" << imageSize.height;
	fs << "board_width" << boardSize.width;
	fs << "board_height" << boardSize.height;
	fs << "square_size" << settings->boardSquareSize;

	if (flag & CALIB_FIX_ASPECT_RATIO) {
		fs << "aspect_ratio" << settings->aspectRatio;
	}

	if (flag) {
		if (settings->useFisheyeModel) {
			sprintf(buf, "flags:%s%s%s%s%s%s", flag & fisheye::CALIB_FIX_SKEW ? " +fix_skew" : "",
				flag & fisheye::CALIB_FIX_K1 ? " +fix_k1" : "", flag & fisheye::CALIB_FIX_K2 ? " +fix_k2" : "",
				flag & fisheye::CALIB_FIX_K3 ? " +fix_k3" : "", flag & fisheye::CALIB_FIX_K4 ? " +fix_k4" : "",
				flag & fisheye::CALIB_RECOMPUTE_EXTRINSIC ? " +recompute_extrinsic" : "");
		}
		else {
			sprintf(buf, "flags:%s%s%s%s%s%s%s%s%s%s", flag & CALIB_USE_INTRINSIC_GUESS ? " +use_intrinsic_guess" : "",
				flag & CALIB_FIX_ASPECT_RATIO ? " +fix_aspect_ratio" : "",
				flag & CALIB_FIX_PRINCIPAL_POINT ? " +fix_principal_point" : "",
				flag & CALIB_ZERO_TANGENT_DIST ? " +zero_tangent_dist" : "", flag & CALIB_FIX_K1 ? " +fix_k1" : "",
				flag & CALIB_FIX_K2 ? " +fix_k2" : "", flag & CALIB_FIX_K3 ? " +fix_k3" : "",
				flag & CALIB_FIX_K4 ? " +fix_k4" : "", flag & CALIB_FIX_K5 ? " +fix_k5" : "",
				flag & CALIB_FIX_K6 ? " +fix_k6" : "");
		}

		cvWriteComment(*fs, buf, 0);
	}

	fs << "flags" << flag;

	fs << "use_fisheye_model" << settings->useFisheyeModel;

	fs << "camera_matrix" << cameraMatrix;
	fs << "distortion_coefficients" << distCoeffs;

	fs << "avg_reprojection_error" << totalAvgErr;

	if (!reprojErrs.empty()) {
		fs << "per_view_reprojection_errors" << Mat(reprojErrs);
	}

	// Close file.
	fs.release();

	return (true);
}

bool Calibration::runCalibrationAndSave(double *totalAvgError) {
	// Only run if enough valid points have been accumulated.
	if (imagePoints.size() < settings->minNumberOfPoints) {
		return (false);
	}

	// Check that image size is properly defined.
	if (settings->imageWidth <= 0 || settings->imageHeigth <= 0) {
		return (false);
	}

	Size imageSize(settings->imageWidth, settings->imageHeigth);
	vector<float> reprojErrs;
	*totalAvgError = 0;

	bool ok = runCalibration(imageSize, cameraMatrix, distCoeffs, imagePoints, reprojErrs, *totalAvgError);

	if (ok) {
		ok = saveCameraParams(imageSize, cameraMatrix, distCoeffs, reprojErrs, *totalAvgError);
	}

	return (ok);
}

bool Calibration::loadUndistortMatrices(void) {
	// Open file with undistort matrices.
	FileStorage fs(settings->loadFileName, FileStorage::READ);

	// Check file.
	if (!fs.isOpened()) {
		return (false);
	}

	Mat undistortCameraMatrix;
	Mat undistortDistCoeffs;
	bool useFisheyeModel = false;

	fs["camera_matrix"] >> undistortCameraMatrix;
	fs["distortion_coefficients"] >> undistortDistCoeffs;
	fs["use_fisheye_model"] >> useFisheyeModel;

	// Close file.
	fs.release();

	// Check that image size is properly defined.
	if (settings->imageWidth <= 0 || settings->imageHeigth <= 0) {
		return (false);
	}

	// Generate maps for frame remap().
	Size imageSize(settings->imageWidth, settings->imageHeigth);

	// Allocate undistort events maps.
	vector<Point2f> undistortEventInputMap;
	undistortEventInputMap.reserve(settings->imageWidth * settings->imageHeigth);

	vector<Point2f> undistortEventOutputMap;
	undistortEventOutputMap.reserve(settings->imageWidth * settings->imageHeigth);

	// Populate undistort events input map with all possible (x, y) address combinations.
	for (size_t y = 0; y < settings->imageHeigth; y++) {
		for (size_t x = 0; x < settings->imageWidth; x++) {
			// Use center of pixel to get better approximation, since we're using floats anyway.
			undistortEventInputMap.push_back(Point2f(x + 0.5, y + 0.5));
		}
	}

	if (useFisheyeModel) {
		Mat optimalCameramatrix;
		fisheye::estimateNewCameraMatrixForUndistortRectify(undistortCameraMatrix, undistortDistCoeffs, imageSize,
			Matx33d::eye(), optimalCameramatrix, 1);

		fisheye::initUndistortRectifyMap(undistortCameraMatrix, undistortDistCoeffs, Matx33d::eye(),
			(settings->fitAllPixels) ? (optimalCameramatrix) : (undistortCameraMatrix), imageSize,
			CV_16SC2, undistortRemap1, undistortRemap2);

		fisheye::undistortPoints(undistortEventInputMap, undistortEventOutputMap, undistortCameraMatrix,
			undistortDistCoeffs, Matx33d::eye(),
			(settings->fitAllPixels) ? (optimalCameramatrix) : (undistortCameraMatrix));
	}
	else {
		// fitAllPixels is not supported for standard lenses. The computation looks strange for APS frames
		// and completely fails for DVS events.
		initUndistortRectifyMap(undistortCameraMatrix, undistortDistCoeffs, Matx33d::eye(), undistortCameraMatrix,
			imageSize, CV_16SC2, undistortRemap1, undistortRemap2);

		undistortPoints(undistortEventInputMap, undistortEventOutputMap, undistortCameraMatrix, undistortDistCoeffs,
			Matx33d::eye(), undistortCameraMatrix);
	}

	// Convert undistortEventOutputMap to integer from float for faster calculations later on.
	undistortEventMap.clear();
	undistortEventMap.reserve(settings->imageWidth * settings->imageHeigth);

	for (size_t i = 0; i < undistortEventOutputMap.size(); i++) {
		undistortEventMap.push_back(undistortEventOutputMap.at(i));
	}

	return (true);
}

void Calibration::undistortEvent(caerPolarityEvent polarity, caerPolarityEventPacket polarityPacket) {
	if (polarity == NULL || !caerPolarityEventIsValid(polarity) || polarityPacket == NULL) {
		return;
	}

	// Get new coordinates at which event shall be remapped.
	size_t mapIdx = (caerPolarityEventGetY(polarity) * settings->imageWidth) + caerPolarityEventGetX(polarity);
	Point2i eventUndistort = undistortEventMap.at(mapIdx);

	// Check that new coordinates are still within view boundary. If not, keep old ones and invalidate event.
	if (eventUndistort.x < 0 || eventUndistort.x >= (int) settings->imageWidth || eventUndistort.y < 0
		|| eventUndistort.y >= (int) settings->imageHeigth) {
		caerPolarityEventInvalidate(polarity, polarityPacket);
	}
	else {
		// Else use new, remapped coordinates.
		caerPolarityEventSetX(polarity, eventUndistort.x);
		caerPolarityEventSetY(polarity, eventUndistort.y);
	}
}

void Calibration::undistortFrame(caerFrameEvent frame) {
	if (frame == NULL || !caerFrameEventIsValid(frame)) {
		return;
	}

	Size frameSize(caerFrameEventGetLengthX(frame), caerFrameEventGetLengthY(frame));
	Mat view(frameSize, CV_16UC(caerFrameEventGetChannelNumber(frame)), caerFrameEventGetPixelArrayUnsafe(frame));
	Mat inputView = view.clone();

	remap(inputView, view, undistortRemap1, undistortRemap2, INTER_CUBIC, BORDER_CONSTANT);
}
