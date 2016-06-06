/**
 * @file frame_utils_opencv.h
 *
 * Functions for frame enhancement and demosaicing, using
 * the popular OpenCV image processing library.
 */

#ifndef LIBCAER_FRAME_UTILS_OPENCV_H_
#define LIBCAER_FRAME_UTILS_OPENCV_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "events/frame.h"

enum caer_frame_utils_opencv_demosaic {
	DEMOSAIC_NORMAL, DEMOSAIC_EDGE_AWARE, // DEMOSAIC_VARIABLE_NUMBER_OF_GRADIENTS not supported on 16bit images currently.
};

enum caer_frame_utils_opencv_contrast {
	CONTRAST_NORMALIZATION, CONTRAST_HISTOGRAM_EQUALIZATION, CONTRAST_CLAHE,
};

enum caer_frame_utils_opencv_white_balance {
	WHITEBALANCE_SIMPLE, WHITEBALANCE_GRAYWORLD,
};

caerFrameEventPacket caerFrameUtilsOpenCVDemosaic(caerFrameEventPacket framePacket,
	enum caer_frame_utils_opencv_demosaic demosaicType);
void caerFrameUtilsOpenCVContrast(caerFrameEventPacket framePacket, enum caer_frame_utils_opencv_contrast contrastType);
void caerFrameUtilsOpenCVWhiteBalance(caerFrameEventPacket framePacket,
	enum caer_frame_utils_opencv_white_balance whiteBalanceType);

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_FRAME_UTILS_OPENCV_H_ */
