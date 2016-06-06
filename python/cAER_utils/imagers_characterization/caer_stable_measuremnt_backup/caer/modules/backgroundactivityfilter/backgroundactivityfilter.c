/*
 * backgroundactivityfilter.c
 *
 *  Created on: Jan 20, 2014
 *      Author: chtekk
 */

#include "backgroundactivityfilter.h"
#include "base/mainloop.h"
#include "base/module.h"

struct BAFilter_state {
	int64_t **timestampMap;
	int32_t deltaT;
	int16_t sizeMaxX;
	int16_t sizeMaxY;
	int8_t subSampleBy;
};

typedef struct BAFilter_state *BAFilterState;

static bool caerBackgroundActivityFilterInit(caerModuleData moduleData);
static void caerBackgroundActivityFilterRun(caerModuleData moduleData, size_t argsNumber, va_list args);
static void caerBackgroundActivityFilterConfig(caerModuleData moduleData);
static void caerBackgroundActivityFilterExit(caerModuleData moduleData);
static bool allocateTimestampMap(BAFilterState state, int16_t sourceID);

static struct caer_module_functions caerBackgroundActivityFilterFunctions = { .moduleInit =
	&caerBackgroundActivityFilterInit, .moduleRun = &caerBackgroundActivityFilterRun, .moduleConfig =
	&caerBackgroundActivityFilterConfig, .moduleExit = &caerBackgroundActivityFilterExit };

void caerBackgroundActivityFilter(uint16_t moduleID, caerPolarityEventPacket polarity) {
	caerModuleData moduleData = caerMainloopFindModule(moduleID, "BAFilter");

	caerModuleSM(&caerBackgroundActivityFilterFunctions, moduleData, sizeof(struct BAFilter_state), 1, polarity);
}

static bool caerBackgroundActivityFilterInit(caerModuleData moduleData) {
	sshsNodePutIntIfAbsent(moduleData->moduleNode, "deltaT", 30000);
	sshsNodePutByteIfAbsent(moduleData->moduleNode, "subSampleBy", 0);

	BAFilterState state = moduleData->moduleState;

	state->deltaT = sshsNodeGetInt(moduleData->moduleNode, "deltaT");
	state->subSampleBy = sshsNodeGetByte(moduleData->moduleNode, "subSampleBy");

	// Add config listeners last, to avoid having them dangling if Init doesn't succeed.
	sshsNodeAddAttributeListener(moduleData->moduleNode, moduleData, &caerModuleConfigDefaultListener);

	// Nothing that can fail here.
	return (true);
}

static void caerBackgroundActivityFilterRun(caerModuleData moduleData, size_t argsNumber, va_list args) {
	UNUSED_ARGUMENT(argsNumber);

	// Interpret variable arguments (same as above in main function).
	caerPolarityEventPacket polarity = va_arg(args, caerPolarityEventPacket);

	// Only process packets with content.
	if (polarity == NULL) {
		return;
	}

	BAFilterState state = moduleData->moduleState;

	// If the map is not allocated yet, do it.
	if (state->timestampMap == NULL) {
		if (!allocateTimestampMap(state, caerEventPacketHeaderGetEventSource(&polarity->packetHeader))) {
			// Failed to allocate memory, nothing to do.
			caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString, "Failed to allocate memory for timestampMap.");
			return;
		}
	}

	// Iterate over events and filter out ones that are not supported by other
	// events within a certain region in the specified timeframe.
	CAER_POLARITY_ITERATOR_VALID_START(polarity)
		// Get values on which to operate.
		int64_t ts = caerPolarityEventGetTimestamp64(caerPolarityIteratorElement, polarity);
		uint16_t x = caerPolarityEventGetX(caerPolarityIteratorElement);
		uint16_t y = caerPolarityEventGetY(caerPolarityIteratorElement);

		// Apply sub-sampling.
		x = U16T(x >> state->subSampleBy);
		y = U16T(y >> state->subSampleBy);

		// Get value from map.
		int64_t lastTS = state->timestampMap[x][y];

		if ((I64T(ts - lastTS) >= I64T(state->deltaT)) || (lastTS == 0)) {
			// Filter out invalid.
			caerPolarityEventInvalidate(caerPolarityIteratorElement, polarity);
		}

		// Update neighboring region.
		if (x > 0) {
			state->timestampMap[x - 1][y] = ts;
		}
		if (x < state->sizeMaxX) {
			state->timestampMap[x + 1][y] = ts;
		}

		if (y > 0) {
			state->timestampMap[x][y - 1] = ts;
		}
		if (y < state->sizeMaxY) {
			state->timestampMap[x][y + 1] = ts;
		}

		if (x > 0 && y > 0) {
			state->timestampMap[x - 1][y - 1] = ts;
		}
		if (x < state->sizeMaxX && y < state->sizeMaxY) {
			state->timestampMap[x + 1][y + 1] = ts;
		}

		if (x > 0 && y < state->sizeMaxY) {
			state->timestampMap[x - 1][y + 1] = ts;
		}
		if (x < state->sizeMaxX && y > 0) {
			state->timestampMap[x + 1][y - 1] = ts;
		}
	CAER_POLARITY_ITERATOR_VALID_END
}

static void caerBackgroundActivityFilterConfig(caerModuleData moduleData) {
	caerModuleConfigUpdateReset(moduleData);

	BAFilterState state = moduleData->moduleState;

	state->deltaT = sshsNodeGetInt(moduleData->moduleNode, "deltaT");
	state->subSampleBy = sshsNodeGetByte(moduleData->moduleNode, "subSampleBy");
}

static void caerBackgroundActivityFilterExit(caerModuleData moduleData) {
	// Remove listener, which can reference invalid memory in userData.
	sshsNodeRemoveAttributeListener(moduleData->moduleNode, moduleData, &caerModuleConfigDefaultListener);

	BAFilterState state = moduleData->moduleState;

	// Ensure map is freed.
	if (state->timestampMap != NULL) {
		free(state->timestampMap[0]);
		free(state->timestampMap);
		state->timestampMap = NULL;
	}
}

static bool allocateTimestampMap(BAFilterState state, int16_t sourceID) {
	// Get size information from source.
	sshsNode sourceInfoNode = caerMainloopGetSourceInfo((uint16_t) sourceID);
	int16_t sizeX = sshsNodeGetShort(sourceInfoNode, "dvsSizeX");
	int16_t sizeY = sshsNodeGetShort(sourceInfoNode, "dvsSizeY");

	// Initialize double-indirection contiguous 2D array, so that array[x][y]
	// is possible, see http://c-faq.com/aryptr/dynmuldimary.html for info.
	state->timestampMap = calloc((size_t) sizeX, sizeof(int64_t *));
	if (state->timestampMap == NULL) {
		return (false); // Failure.
	}

	state->timestampMap[0] = calloc((size_t) (sizeX * sizeY), sizeof(int64_t));
	if (state->timestampMap[0] == NULL) {
		free(state->timestampMap);
		state->timestampMap = NULL;

		return (false); // Failure.
	}

	for (size_t i = 1; i < (size_t) sizeX; i++) {
		state->timestampMap[i] = state->timestampMap[0] + (i * (size_t) sizeY);
	}

	// Assign max ranges for arrays (0 to MAX-1).
	state->sizeMaxX = I16T(sizeX - 1);
	state->sizeMaxY = I16T(sizeY - 1);

	// TODO: size the map differently if subSampleBy is set!
	return (true);
}
