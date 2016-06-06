#ifndef STATISTICS_H_
#define STATISTICS_H_

#include "main.h"

#include <libcaer/events/common.h>
#include <time.h>
#include <sys/time.h>

#define CAER_STATISTICS_STRING "Total events/second: %10" PRIu64 " - Valid events/second: %10" PRIu64

struct caer_statistics_state {
	uint64_t divisionFactor;
	char *currentStatisticsString;
	// Internal book-keeping.
	struct timespec lastTime;
	uint64_t totalEventsCounter;
	uint64_t validEventsCounter;
};

typedef struct caer_statistics_state *caerStatisticsState;

// For reuse inside other modules.
bool caerStatisticsStringInit(caerStatisticsState state);
void caerStatisticsStringUpdate(caerEventPacketHeader packetHeader, caerStatisticsState state);
void caerStatisticsStringExit(caerStatisticsState state);

void caerStatistics(uint16_t moduleID, caerEventPacketHeader packetHeader, size_t divisionFactor);

#endif /* STATISTICS_H_ */
