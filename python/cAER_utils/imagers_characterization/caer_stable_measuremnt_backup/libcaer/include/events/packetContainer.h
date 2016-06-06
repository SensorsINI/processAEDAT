/**
 * @file packetContainer.h
 *
 * EventPacketContainer format definition and handling functions.
 * An EventPacketContainer is a logical construct that contains packets
 * of events (EventPackets) of different event types, with the aim of
 * keeping related events of differing types, such as DVS and IMU data,
 * together. Such a relation is usually based on time intervals.
 */

#ifndef LIBCAER_EVENTS_PACKETCONTAINER_H_
#define LIBCAER_EVENTS_PACKETCONTAINER_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "common.h"

/**
 * EventPacketContainer data structure definition.
 * Signed integers are used for compatibility with languages that
 * do not have unsigned ones, such as Java.
 */
struct caer_event_packet_container {
	/// Number of different event packets contained.
	int32_t eventPacketsNumber;
	/// Array of pointers to the actual event packets.
	caerEventPacketHeader eventPackets[];
}__attribute__((__packed__));

/**
 * Type for pointer to EventPacketContainer data structure.
 */
typedef struct caer_event_packet_container *caerEventPacketContainer;

/**
 * Allocate a new EventPacketContainer with enough space to
 * store up to the given number of EventPacket references.
 * All packet references will be NULL initially.
 *
 * @param eventPacketsNumber the maximum number of EventPacket references
 *                           that can be stored in this container.
 *
 * @return a valid EventPacketContainer handle or NULL on error.
 */
caerEventPacketContainer caerEventPacketContainerAllocate(int32_t eventPacketsNumber);

/**
 * Free the memory occupied by an EventPacketContainer, as well as
 * freeing all of its contained EventPackets and their memory.
 * If you don't want the contained EventPackets to be freed, make
 * sure that you set their reference to NULL before calling this.

 * @param container the container to be freed.
 */
void caerEventPacketContainerFree(caerEventPacketContainer container);

/**
 * Get the maximum number of EventPacket references that can be stored
 * in this particular EventPacketContainer.
 *
 * @param container a valid EventPacketContainer handle. If NULL, zero is returned.
 *
 * @return the number of EventPacket references that can be contained.
 */
static inline int32_t caerEventPacketContainerGetEventPacketsNumber(caerEventPacketContainer container) {
	// Non-existing (empty) containers have no valid packets in them!
	if (container == NULL) {
		return (0);
	}

	return (le32toh(container->eventPacketsNumber));
}

/**
 * Set the maximum number of EventPacket references that can be stored
 * in this particular EventPacketContainer. This should never be used
 * directly, caerEventPacketContainerAllocate() sets this for you.
 *
 * @param container a valid EventPacketContainer handle. If NULL, nothing happens.
 * @param eventPacketsNumber the number of EventPacket references that can be contained.
 */
static inline void caerEventPacketContainerSetEventPacketsNumber(caerEventPacketContainer container,
	int32_t eventPacketsNumber) {
	// Non-existing (empty) containers have no valid packets in them!
	if (container == NULL) {
		return;
	}

	if (eventPacketsNumber < 0) {
		// Negative numbers (bit 31 set) are not allowed!
		caerLog(CAER_LOG_CRITICAL, "EventPacket Container",
			"Called caerEventPacketContainerSetEventPacketsNumber() with negative value!");
		return;
	}

	container->eventPacketsNumber = htole32(eventPacketsNumber);
}

/**
 * Get the reference for the EventPacket stored in this container
 * at the given index.
 *
 * @param container a valid EventPacketContainer handle. If NULL, returns NULL too.
 * @param n the index of the EventPacket to get.
 *
 * @return a reference to an EventPacket or NULL on error.
 */
static inline caerEventPacketHeader caerEventPacketContainerGetEventPacket(caerEventPacketContainer container,
	int32_t n) {
	// Non-existing (empty) containers have no valid packets in them!
	if (container == NULL) {
		return (NULL);
	}

	// Check that we're not out of bounds.
	if (n < 0 || n >= caerEventPacketContainerGetEventPacketsNumber(container)) {
		caerLog(CAER_LOG_CRITICAL, "EventPacket Container",
			"Called caerEventPacketContainerGetEventPacket() with invalid event offset %" PRIi32 ", while maximum allowed value is %" PRIi32 ". Negative values are not allowed!",
			n, caerEventPacketContainerGetEventPacketsNumber(container) - 1);
		return (NULL);
	}

	// Return a pointer to the specified event packet.
	return (container->eventPackets[n]);
}

/**
 * Set the reference for the EventPacket stored in this container
 * at the given index.
 *
 * @param container a valid EventPacketContainer handle. If NULL, nothing happens.
 * @param n the index of the EventPacket to set.
 * @param packetHeader a reference to an EventPacket's header. Can be NULL.
 */
static inline void caerEventPacketContainerSetEventPacket(caerEventPacketContainer container, int32_t n,
	caerEventPacketHeader packetHeader) {
	// Non-existing (empty) containers have no valid packets in them!
	if (container == NULL) {
		return;
	}

	// Check that we're not out of bounds.
	if (n < 0 || n >= caerEventPacketContainerGetEventPacketsNumber(container)) {
		caerLog(CAER_LOG_CRITICAL, "EventPacket Container",
			"Called caerEventPacketContainerSetEventPacket() with invalid event offset %" PRIi32 ", while maximum allowed value is %" PRIi32 ". Negative values are not allowed!",
			n, caerEventPacketContainerGetEventPacketsNumber(container) - 1);
		return;
	}

	// Store the given event packet.
	container->eventPackets[n] = packetHeader;
}

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_EVENTS_PACKETCONTAINER_H_ */
