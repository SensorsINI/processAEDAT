#include "frameenhancer.h"
#include "base/mainloop.h"
#include "base/module.h"
#include <libcaer/frame_utils.h>
#ifdef ENABLE_FRAMEENHANCER_OPENCV
	#include <libcaer/frame_utils_opencv.h>
#endif

struct FrameEnhancer_state {
	bool doDemosaic;
	int demosaicType;
	bool doContrast;
	int contrastType;
	bool doWhiteBalance;
	int whiteBalanceType;
};

typedef struct FrameEnhancer_state *FrameEnhancerState;

static bool caerFrameEnhancerInit(caerModuleData moduleData);
static void caerFrameEnhancerRun(caerModuleData moduleData, size_t argsNumber, va_list args);
static void caerFrameEnhancerConfig(caerModuleData moduleData);
static void caerFrameEnhancerExit(caerModuleData moduleData);

static struct caer_module_functions caerFrameEnhancerFunctions = { .moduleInit = &caerFrameEnhancerInit, .moduleRun =
	&caerFrameEnhancerRun, .moduleConfig = &caerFrameEnhancerConfig, .moduleExit = &caerFrameEnhancerExit };

caerFrameEventPacket caerFrameEnhancer(uint16_t moduleID, caerFrameEventPacket frame) {
	caerModuleData moduleData = caerMainloopFindModule(moduleID, "FrameEnhancer");

	// By default, same as input frame packet.
	caerFrameEventPacket enhancedFrame = frame;

	caerModuleSM(&caerFrameEnhancerFunctions, moduleData, sizeof(struct FrameEnhancer_state), 2, frame, &enhancedFrame);

	return (enhancedFrame);
}

static bool caerFrameEnhancerInit(caerModuleData moduleData) {
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "doDemosaic", false);
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "doContrast", false);
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "doWhiteBalance", false);

#ifdef ENABLE_FRAMEENHANCER_OPENCV
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "demosaicType", "opencv_edge_aware");
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "contrastType", "opencv_clahe");
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "whiteBalanceType", "opencv_grayworld");
#else
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "demosaicType", "standard");
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "contrastType", "standard");
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "whiteBalanceType", "standard");
#endif

	FrameEnhancerState state = moduleData->moduleState;

	// Add config listeners last, to avoid having them dangling if Init doesn't succeed.
	sshsNodeAddAttributeListener(moduleData->moduleNode, moduleData, &caerModuleConfigDefaultListener);

	// Nothing that can fail here.
	return (true);
}

static void caerFrameEnhancerRun(caerModuleData moduleData, size_t argsNumber, va_list args) {
	UNUSED_ARGUMENT(argsNumber);

	// Interpret variable arguments (same as above in main function).
	caerFrameEventPacket frame = va_arg(args, caerFrameEventPacket);
	caerFrameEventPacket *enhancedFrame = va_arg(args, caerFrameEventPacket *);

	// Only process packets with content.
	if (frame == NULL) {
		return;
	}

	FrameEnhancerState state = moduleData->moduleState;

	if (state->doDemosaic) {
#ifdef ENABLE_FRAMEENHANCER_OPENCV
		switch (state->demosaicType) {
			case 0:
				*enhancedFrame = caerFrameUtilsDemosaic(frame);
				break;

			case 1:
				*enhancedFrame = caerFrameUtilsOpenCVDemosaic(frame, DEMOSAIC_NORMAL);
				break;

			case 2:
				*enhancedFrame = caerFrameUtilsOpenCVDemosaic(frame, DEMOSAIC_EDGE_AWARE);
				break;
		}
#else
		*enhancedFrame = caerFrameUtilsDemosaic(frame);
#endif
	}

	if (state->doWhiteBalance) {
#ifdef ENABLE_FRAMEENHANCER_OPENCV
		switch (state->whiteBalanceType) {
			case 0:
				caerFrameUtilsWhiteBalance(*enhancedFrame);
				break;

			case 1:
				caerFrameUtilsOpenCVWhiteBalance(*enhancedFrame, WHITEBALANCE_SIMPLE);
				break;

			case 2:
				caerFrameUtilsOpenCVWhiteBalance(*enhancedFrame, WHITEBALANCE_GRAYWORLD);
				break;
		}
#else
		caerFrameUtilsWhiteBalance(*enhancedFrame);
#endif
	}

	if (state->doContrast) {
#ifdef ENABLE_FRAMEENHANCER_OPENCV
		switch (state->contrastType) {
			case 0:
				caerFrameUtilsContrast(*enhancedFrame);
				break;

			case 1:
				caerFrameUtilsOpenCVContrast(*enhancedFrame, CONTRAST_NORMALIZATION);
				break;

			case 2:
				caerFrameUtilsOpenCVContrast(*enhancedFrame, CONTRAST_HISTOGRAM_EQUALIZATION);
				break;

			case 3:
				caerFrameUtilsOpenCVContrast(*enhancedFrame, CONTRAST_CLAHE);
				break;
		}
#else
		caerFrameUtilsContrast(*enhancedFrame);
#endif
	}
}

static void caerFrameEnhancerConfig(caerModuleData moduleData) {
	caerModuleConfigUpdateReset(moduleData);

	FrameEnhancerState state = moduleData->moduleState;

}

static void caerFrameEnhancerExit(caerModuleData moduleData) {
	// Remove listener, which can reference invalid memory in userData.
	sshsNodeRemoveAttributeListener(moduleData->moduleNode, moduleData, &caerModuleConfigDefaultListener);

	FrameEnhancerState state = moduleData->moduleState;

}
