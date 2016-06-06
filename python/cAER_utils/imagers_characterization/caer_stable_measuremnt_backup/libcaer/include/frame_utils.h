/**
 * @file frame_utils.h
 *
 * Basic functions for frame enhancement and demosaicing, that don't
 * require any external dependencies, such as OpenCV.
 * Use of the OpenCV variants is recommended for quality and performance.
 */

#ifndef LIBCAER_FRAME_UTILS_H_
#define LIBCAER_FRAME_UTILS_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "events/frame.h"

caerFrameEventPacket caerFrameUtilsDemosaic(caerFrameEventPacket framePacket);
void caerFrameUtilsContrast(caerFrameEventPacket framePacket);
void caerFrameUtilsWhiteBalance(caerFrameEventPacket framePacket);

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_FRAME_UTILS_H_ */
