/*
 * out_common.h
 *
 *  Created on: Jan 9, 2014
 *      Author: chtekk
 */

#ifndef OUT_COMMON_H_
#define OUT_COMMON_H_

#include "main.h"
#include <unistd.h>
#include <sys/uio.h>

#include <libcaer/events/common.h>
#include <libcaer/events/polarity.h>

#define IOVEC_SIZE 512

static inline void caerOutputCommonWriteFull(int fileDescriptor, void *startAddress, size_t fullLength,
bool excludeHeader, size_t maxBytesPerPacket) {
	// Skip header if requested.
	if (excludeHeader) {
		startAddress = ((uint8_t *) startAddress) + sizeof(struct caer_event_packet_header);
		fullLength -= sizeof(struct caer_event_packet_header);
	}

	if (maxBytesPerPacket == 0) {
		// Write out everything in one big packet.
		write(fileDescriptor, startAddress, fullLength);
	}
	else {
		// Write data out in chunks of specified size.
		// TODO: ensure event size boundaries are automatically met.
		while (fullLength > 0) {
			size_t bytesToSend = maxBytesPerPacket;
			if (bytesToSend > fullLength) {
				bytesToSend = fullLength;
			}

			write(fileDescriptor, startAddress, bytesToSend);

			startAddress = ((uint8_t *) startAddress) + bytesToSend;
			fullLength -= bytesToSend;
		}
	}
}

static inline void caerOutputWriteOldAERHack(int fileDescriptor, void *startAddress, size_t fullLength) {
	UNUSED_ARGUMENT(fullLength);

	// Check that we're working with polarity events, which are the only support
	// format for old AER compatibility.
	caerEventPacketHeader packetHeader = startAddress;

	if (caerEventPacketHeaderGetEventType(packetHeader) != POLARITY_EVENT) {
		return;
	}

	// Convert the events to the old format and write them out.
	CAER_POLARITY_ITERATOR_ALL_START((caerPolarityEventPacket) packetHeader)
		uint32_t data = U32T((caerPolarityEventGetPolarity(caerPolarityIteratorElement) & 0x01) << 11);
		data |= U32T(((239 - caerPolarityEventGetX(caerPolarityIteratorElement)) & 0x3FF) << 12);
		data |= U32T((caerPolarityEventGetY(caerPolarityIteratorElement) & 0x1FF) << 22);
		data = htobe32(data);

		write(fileDescriptor, &data, 4);

		int32_t ts = caerPolarityEventGetTimestamp(caerPolarityIteratorElement);
		ts = I32T(htobe32(U32T(ts)));

		write(fileDescriptor, &ts, 4);
	CAER_POLARITY_ITERATOR_ALL_END
}

static inline void caerOutputCommonWriteFullSGIO(int fileDescriptor, struct iovec *sgioMemory, size_t sgioLength,
bool excludeHeader, size_t maxBytesPerPacket) {
	// Skip header if requested.
	if (excludeHeader) {
		sgioMemory[0].iov_base = ((uint8_t *) sgioMemory[0].iov_base) + sizeof(struct caer_event_packet_header);
		sgioMemory[0].iov_len -= sizeof(struct caer_event_packet_header);

		// Handle case where first IOVEC was only the header, so we skip it altogether.
		if (sgioMemory[0].iov_len == 0) {
			sgioMemory[0].iov_base = NULL;

			// Don't consider this IOVEC for the writev() call.
			sgioMemory += 1;
			sgioLength -= 1;
		}
	}

	if (maxBytesPerPacket == 0) {
		// Write out everything in one big packet.
		writev(fileDescriptor, sgioMemory, (int) sgioLength);
	}
	else {
		// TODO: implement this.
	}
}

static inline void caerOutputCommonSend(const char *subSystemString, caerEventPacketHeader packetHeader,
	int fileDescriptor, struct iovec *sgioMemory, bool validOnly, bool excludeHeader, size_t maxBytesPerPacket,
	bool oldAERFormat) {
	// If validOnly is not specified, we can just send the whole packet
	// in one go directly.
	if (!validOnly) {
		// First we need to fix the event capacity, since we don't want to
		// send the zeroed-out tail of the packet to conserve bandwidth.
		int32_t oldCapacity = caerEventPacketHeaderGetEventCapacity(packetHeader);

		// Set it to the event number, which we'll use when writing the packet.
		int32_t eventNumber = caerEventPacketHeaderGetEventNumber(packetHeader);
		caerEventPacketHeaderSetEventCapacity(packetHeader, eventNumber);

		// Write the whole packet, up to the last event.
		if (oldAERFormat) {
			caerOutputWriteOldAERHack(fileDescriptor, packetHeader,
				sizeof(*packetHeader) + (size_t) (eventNumber * caerEventPacketHeaderGetEventSize(packetHeader)));
		}
		else {
			caerOutputCommonWriteFull(fileDescriptor, packetHeader,
				sizeof(*packetHeader) + (size_t) (eventNumber * caerEventPacketHeaderGetEventSize(packetHeader)),
				excludeHeader, maxBytesPerPacket);
		}

		// Reset to old value.
		caerEventPacketHeaderSetEventCapacity(packetHeader, oldCapacity);
	}
	else {
		// To conserve bandwidth, we only transmit the valid events here, so
		// the values for capacity and number will have to be adjusted.
		int32_t oldCapacity = caerEventPacketHeaderGetEventCapacity(packetHeader);
		int32_t oldNumber = caerEventPacketHeaderGetEventNumber(packetHeader);

		int32_t eventValid = caerEventPacketHeaderGetEventValid(packetHeader);

		// Use scatter/gather IO to write only the valid events out more
		// efficiently if possible, this is limited by the number of iovec
		// structs available, and so we have to determine if it's possible
		// to actually satisfy the request this way, by looking at how many
		// invalid events there are, each of which could be a split point
		// in the event packet buffer. +1 for the packet header part.
		int32_t eventSize = caerEventPacketHeaderGetEventSize(packetHeader);

		if (sgioMemory != NULL && (oldNumber - eventValid + 1) <= IOVEC_SIZE) {
			size_t iovecUsed = 0;

			// Scan thorough packet and commit valid runs.
			sgioMemory[iovecUsed].iov_base = packetHeader;
			sgioMemory[iovecUsed].iov_len = sizeof(struct caer_event_packet_header);

			for (int32_t i = 0; i < oldNumber; i++) {
				void *currEvent = caerGenericEventGetEvent(packetHeader, i);

				if (caerGenericEventIsValid(currEvent)) {
					// If this is the first valid packet after an invalid run,
					// set the data for the new run, else just make current longer.
					if (sgioMemory[iovecUsed].iov_base == NULL) {
						sgioMemory[iovecUsed].iov_base = currEvent;
						sgioMemory[iovecUsed].iov_len = (size_t) eventSize;
					}
					else {
						sgioMemory[iovecUsed].iov_len += (size_t) eventSize;
					}
				}
				else {
					// Start a new run, if not already done!
					if (sgioMemory[iovecUsed].iov_base != NULL) {
						sgioMemory[++iovecUsed].iov_base = NULL;
					}
				}
			}

			caerEventPacketHeaderSetEventCapacity(packetHeader, eventValid);
			caerEventPacketHeaderSetEventNumber(packetHeader, eventValid);

			// Done, do the call.
			caerOutputCommonWriteFullSGIO(fileDescriptor, sgioMemory, iovecUsed + 1, excludeHeader, maxBytesPerPacket);
		}
		else {
			// Else we use a much slower allocate-copy-free approach.
			uint8_t *tmpValidEvents = malloc(
				sizeof(struct caer_event_packet_header) + (size_t) (eventValid * eventSize));

			if (tmpValidEvents == NULL) {
				// Failure to allocate memory, just don't send packet and log this.
				caerLog(CAER_LOG_ALERT, subSystemString, "Failed to allocate memory for valid event copy.");
			}
			else {
				// Go through all valid events and copy them.
				size_t currOffset = sizeof(struct caer_event_packet_header);

				for (int32_t i = 0; i < oldNumber; i++) {
					void *currEvent = caerGenericEventGetEvent(packetHeader, i);

					if (caerGenericEventIsValid(currEvent)) {
						memcpy(tmpValidEvents + currOffset, currEvent, (size_t) eventSize);
						currOffset += (size_t) eventSize;
					}
				}

				caerEventPacketHeaderSetEventCapacity(packetHeader, eventValid);
				caerEventPacketHeaderSetEventNumber(packetHeader, eventValid);

				// Last, copy the header, _after_ it's been manipulated/updated.
				memcpy(tmpValidEvents, packetHeader, sizeof(struct caer_event_packet_header));

				caerOutputCommonWriteFull(fileDescriptor, tmpValidEvents, currOffset, excludeHeader, maxBytesPerPacket);

				free(tmpValidEvents);
			}
		}

		// Reset to old value.
		caerEventPacketHeaderSetEventCapacity(packetHeader, oldCapacity);
		caerEventPacketHeaderSetEventNumber(packetHeader, oldNumber);
	}
}

#endif /* OUT_COMMON_H_ */
