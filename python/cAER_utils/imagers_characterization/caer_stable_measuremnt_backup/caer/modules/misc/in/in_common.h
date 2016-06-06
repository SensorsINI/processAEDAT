/*
 * in_common.h
 *
 *  Created on: Okt 29, 2015
 *      Author: phineasng
 */

#ifndef IN_COMMON_H_
#define IN_COMMON_H_

#include "main.h"
#include <unistd.h>
#include <sys/uio.h>

#include <libcaer/events/common.h>
#include "base/mainloop.h" // For caerMainloopData definition.

/*
 *  Reads a single packets - remember to free the packet
 */
static inline caerEventPacketHeader caerInputCommonReadPacket(int fileDescriptor) {
	caerLog(CAER_LOG_DEBUG, "caerInputCommonReadPacket", "Inside reading function (FileDescriptor: %d)",
		fileDescriptor);

	// if for some reason, the fileDescriptor is not valid, return NULL
	if (fileDescriptor < 0) {
		return (NULL);
	}

	// allocate space for packet header
	caerEventPacketHeader header = malloc(CAER_EVENT_PACKET_HEADER_SIZE);
	ssize_t bytes_read = read(fileDescriptor, header, CAER_EVENT_PACKET_HEADER_SIZE);

	// if nothing has been read, or there was an error, return NULL
	if (bytes_read <= 0) {
		caerLog(CAER_LOG_WARNING, "caerInputCommonReadPacket", "Error while reading packet header: %zd", bytes_read);
		free(header);

		return (NULL);
	}

	// else, realloc to read the rest of the packet
	int32_t event_number = caerEventPacketHeaderGetEventNumber(header);
	int32_t event_size = caerEventPacketHeaderGetEventSize(header);

	// The total number of events written to file is assumed to be equal to the number of
	// events (i.e. no zeros written, cf. "misc/out/out_common.h")
	int32_t total_size_events = event_number * event_size;

	header = realloc(header, (size_t) (CAER_EVENT_PACKET_HEADER_SIZE + total_size_events));
	bytes_read = read(fileDescriptor, (void *) (((uint8_t *) header) + CAER_EVENT_PACKET_HEADER_SIZE),
		(size_t) total_size_events);

	// if nothing has been read, or there was an error, return NULL
	if (bytes_read <= 0) {
		caerLog(CAER_LOG_WARNING, "caerInputCommonReadPacket", "Error while reading packet: %zd", bytes_read);
		free(header);

		return (NULL);
	}

	// Remeber to free it later on!
	return (header);
}

static inline void mainloopDataNotifyIncrease(void *p) {
	caerMainloopData mainloopData = p;

	atomic_fetch_add_explicit(&mainloopData->dataAvailable, 1, memory_order_release);
}

static inline void mainloopDataNotifyDecrease(void *p) {
	caerMainloopData mainloopData = p;

	// No special memory order for decrease, because the acquire load to even start running
	// through a mainloop already synchronizes with the release store above.
	atomic_fetch_sub_explicit(&mainloopData->dataAvailable, 1, memory_order_relaxed);
}

#endif /* IN_COMMON_H_ */
