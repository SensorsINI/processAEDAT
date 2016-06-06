#ifndef VISUALIZER_H_
#define VISUALIZER_H_

#include "main.h"
#include "base/module.h"
#include <libcaer/events/polarity.h>
#include <libcaer/events/frame.h>
#include <libcaer/events/imu6.h>
#include <allegro5/allegro.h>

#define VISUALIZER_DEFAULT_ZOOM 2.0f
#define VISUALIZER_REFRESH_RATE 60.0f

typedef struct caer_visualizer_state *caerVisualizerState;
typedef bool (*caerVisualizerRenderer)(caerVisualizerState state, caerEventPacketHeader packetHeader);
typedef void (*caerVisualizerEventHandler)(caerVisualizerState state, ALLEGRO_EVENT event);

// For reuse inside other modules.
caerVisualizerState caerVisualizerInit(caerVisualizerRenderer renderer, caerVisualizerEventHandler eventHandler,
	int32_t bitmapSizeX, int32_t bitmapSizeY, float defaultZoomFactor, bool defaultShowStatistics,
	caerModuleData parentModule);
void caerVisualizerUpdate(caerVisualizerState state, caerEventPacketHeader packetHeader);
void caerVisualizerExit(caerVisualizerState state);

bool caerVisualizerRendererPolarityEvents(caerVisualizerState state, caerEventPacketHeader polarityEventPacketHeader);
bool caerVisualizerRendererFrameEvents(caerVisualizerState state, caerEventPacketHeader frameEventPacketHeader);
bool caerVisualizerRendererIMU6Events(caerVisualizerState state, caerEventPacketHeader imu6EventPacketHeader);

void caerVisualizer(uint16_t moduleID, const char *name, caerVisualizerRenderer renderer,
	caerVisualizerEventHandler eventHandler, caerEventPacketHeader packetHeader);

void caerVisualizerSystemInit(void);

#endif /* VISUALIZER_H_ */
