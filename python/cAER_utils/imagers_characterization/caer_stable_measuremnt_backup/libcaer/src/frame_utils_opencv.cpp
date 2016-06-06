#include "frame_utils_opencv.h"

#include <opencv2/core.hpp>
#include <opencv2/core/utility.hpp>
#include <opencv2/imgproc.hpp>

using namespace cv;
using namespace std;

static void frameUtilsOpenCVDemosaicFrame(caerFrameEvent colorFrame, caerFrameEvent monoFrame,
	enum caer_frame_utils_opencv_demosaic demosaicType);
static void frameUtilsOpenCVContrastNormalize(Mat &intensity, float clipHistPercent);
static void frameUtilsOpenCVContrastEqualize(Mat &intensity);
static void frameUtilsOpenCVContrastCLAHE(Mat &intensity, float clipLimit, int tilesGridSize);

static void frameUtilsOpenCVDemosaicFrame(caerFrameEvent colorFrame, caerFrameEvent monoFrame,
	enum caer_frame_utils_opencv_demosaic demosaicType) {
	// Initialize OpenCV Mat based on caerFrameEvent data directly (no image copy).
	Size frameSize(caerFrameEventGetLengthX(monoFrame), caerFrameEventGetLengthY(monoFrame));
	Mat monoMat(frameSize, CV_16UC(caerFrameEventGetChannelNumber(monoFrame)),
		caerFrameEventGetPixelArrayUnsafe(monoFrame));
	Mat colorMat(frameSize, CV_16UC(caerFrameEventGetChannelNumber(colorFrame)),
		caerFrameEventGetPixelArrayUnsafe(colorFrame));

	CV_Assert(monoMat.type() == CV_16UC1 && colorMat.type() == CV_16UC3);

	// Select correct type code for OpenCV demosaic algorithm.
	int code = 0;

	switch (demosaicType) {
		case DEMOSAIC_NORMAL:
			switch (caerFrameEventGetColorFilter(monoFrame)) {
				case RGBG:
					code = COLOR_BayerBG2RGB;
					break;

				case GRGB:
					code = COLOR_BayerGB2RGB;
					break;

				case GBGR:
					code = COLOR_BayerGR2RGB;
					break;

				case BGRG:
					code = COLOR_BayerRG2RGB;
					break;

				default:
					// Impossible, other color filters get filtered out above.
					break;
			}
			break;

			/*case DEMOSAIC_VARIABLE_NUMBER_OF_GRADIENTS:
			 switch (caerFrameEventGetColorFilter(monoFrame)) {
			 case RGBG:
			 code = COLOR_BayerBG2RGB_VNG;
			 break;

			 case GRGB:
			 code = COLOR_BayerGB2RGB_VNG;
			 break;

			 case GBGR:
			 code = COLOR_BayerGR2RGB_VNG;
			 break;

			 case BGRG:
			 code = COLOR_BayerRG2RGB_VNG;
			 break;

			 default:
			 // Impossible, other color filters get filtered out above.
			 break;
			 }
			 break;*/

		case DEMOSAIC_EDGE_AWARE:
			switch (caerFrameEventGetColorFilter(monoFrame)) {
				case RGBG:
					code = COLOR_BayerBG2RGB_EA;
					break;

				case GRGB:
					code = COLOR_BayerGB2RGB_EA;
					break;

				case GBGR:
					code = COLOR_BayerGR2RGB_EA;
					break;

				case BGRG:
					code = COLOR_BayerRG2RGB_EA;
					break;

				default:
					// Impossible, other color filters get filtered out above.
					break;
			}
			break;
	}

	// Convert Bayer pattern to RGB image.
	cvtColor(monoMat, colorMat, code);
}

caerFrameEventPacket caerFrameUtilsOpenCVDemosaic(caerFrameEventPacket framePacket,
	enum caer_frame_utils_opencv_demosaic demosaicType) {
	if (framePacket == NULL) {
		return (NULL);
	}

	int32_t countValid = 0;
	int32_t maxLengthX = 0;
	int32_t maxLengthY = 0;

	// This only works on valid frames coming from a camera: only one color channel,
	// but with color filter information defined.
	CAER_FRAME_ITERATOR_VALID_START(framePacket)
		if (caerFrameEventGetChannelNumber(caerFrameIteratorElement) == GRAYSCALE
			&& caerFrameEventGetColorFilter(caerFrameIteratorElement) != MONO) {
			if (caerFrameEventGetColorFilter(caerFrameIteratorElement) == RGBG
				|| caerFrameEventGetColorFilter(caerFrameIteratorElement) == GRGB
				|| caerFrameEventGetColorFilter(caerFrameIteratorElement) == GBGR
				|| caerFrameEventGetColorFilter(caerFrameIteratorElement) == BGRG) {
				countValid++;

				if (caerFrameEventGetLengthX(caerFrameIteratorElement) > maxLengthX) {
					maxLengthX = caerFrameEventGetLengthX(caerFrameIteratorElement);
				}

				if (caerFrameEventGetLengthY(caerFrameIteratorElement) > maxLengthY) {
					maxLengthY = caerFrameEventGetLengthY(caerFrameIteratorElement);
				}
			}
			else {
				caerLog(CAER_LOG_WARNING, "caerFrameUtilsOpenCVDemosaic()",
					"OpenCV demosaicing doesn't support the RGBW color filter, only RGBG. Please use caerFrameUtilsDemosaic() instead.");
			}
		}
	CAER_FRAME_ITERATOR_VALID_END

	// Allocate new frame with RGB channels to hold resulting color image.
	caerFrameEventPacket colorFramePacket = caerFrameEventPacketAllocate(countValid,
		caerEventPacketHeaderGetEventSource(&framePacket->packetHeader),
		caerEventPacketHeaderGetEventTSOverflow(&framePacket->packetHeader), maxLengthX, maxLengthY, RGB);
	if (colorFramePacket == NULL) {
		return (NULL);
	}

	int32_t colorIndex = 0;

	// Now that we have a valid new color frame packet, we can convert the frames one by one.
	CAER_FRAME_ITERATOR_VALID_START(framePacket)
		if (caerFrameEventGetChannelNumber(caerFrameIteratorElement) == GRAYSCALE
			&& caerFrameEventGetColorFilter(caerFrameIteratorElement) != MONO) {
			if (caerFrameEventGetColorFilter(caerFrameIteratorElement) == RGBG
				|| caerFrameEventGetColorFilter(caerFrameIteratorElement) == GRGB
				|| caerFrameEventGetColorFilter(caerFrameIteratorElement) == GBGR
				|| caerFrameEventGetColorFilter(caerFrameIteratorElement) == BGRG) {
				// If all conditions are met, copy from framePacket's mono frame to colorFramePacket's RGB frame.
				caerFrameEvent colorFrame = caerFrameEventPacketGetEvent(colorFramePacket, colorIndex++);

				// First copy all the metadata.
				caerFrameEventSetColorFilter(colorFrame, caerFrameEventGetColorFilter(caerFrameIteratorElement));
				caerFrameEventSetLengthXLengthYChannelNumber(colorFrame,
					caerFrameEventGetLengthX(caerFrameIteratorElement),
					caerFrameEventGetLengthY(caerFrameIteratorElement), RGB, colorFramePacket);
				caerFrameEventSetPositionX(colorFrame, caerFrameEventGetPositionX(caerFrameIteratorElement));
				caerFrameEventSetPositionY(colorFrame, caerFrameEventGetPositionY(caerFrameIteratorElement));
				caerFrameEventSetROIIdentifier(colorFrame, caerFrameEventGetROIIdentifier(caerFrameIteratorElement));
				caerFrameEventSetTSStartOfFrame(colorFrame, caerFrameEventGetTSStartOfFrame(caerFrameIteratorElement));
				caerFrameEventSetTSEndOfFrame(colorFrame, caerFrameEventGetTSEndOfFrame(caerFrameIteratorElement));
				caerFrameEventSetTSStartOfExposure(colorFrame,
					caerFrameEventGetTSStartOfExposure(caerFrameIteratorElement));
				caerFrameEventSetTSEndOfExposure(colorFrame,
					caerFrameEventGetTSEndOfExposure(caerFrameIteratorElement));

				// Then the actual pixels. Only supports RGBG!
				frameUtilsOpenCVDemosaicFrame(colorFrame, caerFrameIteratorElement, demosaicType);

				// Finally validate the new frame.
				caerFrameEventValidate(colorFrame, colorFramePacket);
			}
		}
	CAER_FRAME_ITERATOR_VALID_END

	return (colorFramePacket);
}

void caerFrameUtilsOpenCVContrast(caerFrameEventPacket framePacket,
	enum caer_frame_utils_opencv_contrast contrastType) {
	if (framePacket == NULL) {
		return;
	}

	CAER_FRAME_ITERATOR_VALID_START(framePacket)
		Size frameSize(caerFrameEventGetLengthX(caerFrameIteratorElement),
			caerFrameEventGetLengthY(caerFrameIteratorElement));
		Mat orig(frameSize, CV_16UC(caerFrameEventGetChannelNumber(caerFrameIteratorElement)),
			caerFrameEventGetPixelArrayUnsafe(caerFrameIteratorElement));

		CV_Assert(orig.type() == CV_16UC1 || orig.type() == CV_16UC3 || orig.type() == CV_16UC4);

		// This generally only works well on grayscale intensity images.
		// So, if this is a grayscale image, good, else if its a color
		// image we convert it to YCrCb and operate on the Y channel only.
		Mat intensity;
		vector<Mat> yCrCbPlanes(3);
		Mat rgbaAlpha;

		// Grayscale, no intensity extraction needed.
		if (orig.channels() == GRAYSCALE) {
			intensity = orig;
		}
		else {
			// Color image, extract RGB and intensity/luminance.
			Mat rgb;

			if (orig.channels() == RGBA) {
				// We separate Alpha from RGB first.
				// We will restore alpha at the end.
				rgb = Mat(orig.rows, orig.cols, CV_16UC3);
				rgbaAlpha = Mat(orig.rows, orig.cols, CV_16UC1);

				Mat out[] = { rgb, rgbaAlpha };
				// rgba[0] -> rgb[0], rgba[1] -> rgb[1],
				// rgba[2] -> rgb[2], rgba[3] -> rgbaAlpha[0]
				int channelTransform[] = { 0, 0, 1, 1, 2, 2, 3, 3 };
				mixChannels(&orig, 1, out, 2, channelTransform, 4);
			}
			else {
				// Already an RGB image.
				rgb = orig;
				CV_Assert(rgb.type() == CV_16UC3);
			}

			// First we convert from RGB to a color space with
			// separate luminance channel.
			Mat rgbYCrCb;
			cvtColor(rgb, rgbYCrCb, COLOR_RGB2YCrCb);

			CV_Assert(rgbYCrCb.type() == CV_16UC3);

			// Then we split it up so that we can access the luminance
			// channel on its own separately.
			split(rgbYCrCb, yCrCbPlanes);

			// Now we have the luminance image in yCrCbPlanes[0].
			intensity = yCrCbPlanes[0];
		}

		CV_Assert(intensity.type() == CV_16UC1);

		// Apply contrast enhancement algorithm.
		switch (contrastType) {
			case CONTRAST_NORMALIZATION:
				frameUtilsOpenCVContrastNormalize(intensity, 1.0);
				break;

			case CONTRAST_HISTOGRAM_EQUALIZATION:
				frameUtilsOpenCVContrastEqualize(intensity);
				break;

			case CONTRAST_CLAHE:
				frameUtilsOpenCVContrastCLAHE(intensity, 4.0, 8);
				break;
		}

		// If original was a color frame, we have to mix the various
		// components back together into an RGB(A) image.
		if (orig.channels() != GRAYSCALE) {
			Mat YCrCbrgb;
			merge(yCrCbPlanes, YCrCbrgb);

			CV_Assert(YCrCbrgb.type() == CV_16UC3);

			if (orig.channels() == RGBA) {
				Mat rgb;
				cvtColor(YCrCbrgb, rgb, COLOR_YCrCb2RGB);

				CV_Assert(rgb.type() == CV_16UC3);

				// Restore original alpha.
				Mat in[] = { rgb, rgbaAlpha };
				// rgb[0] -> rgba[0], rgb[1] -> rgba[1],
				// rgb[2] -> rgba[2], rgbaAlpha[0] -> rgba[3]
				int channelTransform[] = { 0, 0, 1, 1, 2, 2, 3, 3 };
				mixChannels(in, 2, &orig, 1, channelTransform, 4);
			}
			else {
				cvtColor(YCrCbrgb, orig, COLOR_YCrCb2RGB);
			}
		}
	CAER_FRAME_ITERATOR_VALID_END
}

void caerFrameUtilsOpenCVWhiteBalance(caerFrameEventPacket framePacket,
	enum caer_frame_utils_opencv_white_balance whiteBalanceType) {

}

static void frameUtilsOpenCVContrastNormalize(Mat &intensity, float clipHistPercent) {
	CV_Assert(intensity.type() == CV_16UC1);
	CV_Assert(clipHistPercent >= 0 && clipHistPercent < 100);

	// O(x, y) = alpha * I(x, y) + beta, where alpha maximizes the range
	// (contrast) and beta shifts it so lowest is zero (brightness).
	double minValue, maxValue;

	if (clipHistPercent == 0) {
		// Determine minimum and maximum values.
		minMaxLoc(intensity, &minValue, &maxValue);
	}
	else {
		// Calculate histogram.
		int histSize = UINT16_MAX + 1;
		float hRange[] = { 0, (float) histSize };
		const float *histRange = { hRange };
		bool uniform = true;
		bool accumulate = false;

		Mat hist;
		calcHist(&intensity, 1, 0, Mat(), hist, 1, &histSize, &histRange, uniform, accumulate);

		// Calculate cumulative distribution from the histogram.
		for (size_t i = 1; i < (size_t) histSize; i++) {
			hist.at<float>(i) += hist.at<float>(i - 1);
		}

		// Locate points that cut at required value.
		float max = hist.at<float>(histSize - 1);
		clipHistPercent *= (max / 100.0); // Calculate absolute value from percent.
		clipHistPercent /= 2.0; // Left and right wings, so divide by two.

		// Locate left cut.
		minValue = 0;
		while (hist.at<float>(minValue) < clipHistPercent) {
			minValue++;
		}

		// Locate right cut.
		maxValue = UINT16_MAX;
		while (hist.at<float>(maxValue) >= (max - clipHistPercent)) {
			maxValue--;
		}
	}

	// Use min/max to calculate input range.
	double range = maxValue - minValue;

	// Calculate alpha (contrast).
	double alpha = ((double) UINT16_MAX) / range;

	// Calculate beta (brightness).
	double beta = -minValue * alpha;

	// Apply alpha and beta to pixels array.
	intensity.convertTo(intensity, -1, alpha, beta);
}

static void frameUtilsOpenCVContrastEqualize(Mat &intensity) {
	CV_Assert(intensity.type() == CV_16UC1);

	// Calculate histogram.
	int histSize = UINT16_MAX + 1;
	float hRange[] = { 0, (float) histSize };
	const float *histRange = { hRange };
	bool uniform = true;
	bool accumulate = false;

	Mat hist;
	calcHist(&intensity, 1, 0, Mat(), hist, 1, &histSize, &histRange, uniform, accumulate);

	// Calculate CDF from the histogram.
	for (size_t i = 1; i < (size_t) histSize; i++) {
		hist.at<float>(i) += hist.at<float>(i - 1);
	}

	// Total number of pixels. Must be the last value!
	float total = hist.at<float>(histSize - 1);

	// Smallest non-zero CDF value. Must be  the first non-zero value!
	float min = 0;
	for (size_t i = 0; i < (size_t) histSize; i++) {
		if (hist.at<float>(i) > 0) {
			min = hist.at<float>(i);
			break;
		}
	}

	// Calculate lookup table for histogram equalization.
	hist -= min;
	hist /= (total - min);
	hist *= (float) UINT16_MAX;

	// Apply lookup table to input image.
	for_each(intensity.begin<uint16_t>(), intensity.end<uint16_t>(),
		[&hist](uint16_t &elem) {elem = hist.at<float>(elem);});
}

static void frameUtilsOpenCVContrastCLAHE(Mat &intensity, float clipLimit, int tilesGridSize) {
	CV_Assert(intensity.type() == CV_16UC1);
	CV_Assert(clipLimit >= 0 && clipLimit < 100);
	CV_Assert(tilesGridSize >= 1 && tilesGridSize <= 64);

	// Apply the CLAHE algorithm to the intensity channel (luminance).
	Ptr<CLAHE> clahe = createCLAHE();
	clahe->setClipLimit(clipLimit);
	clahe->setTilesGridSize(Size(tilesGridSize, tilesGridSize));
	clahe->apply(intensity, intensity);
}
