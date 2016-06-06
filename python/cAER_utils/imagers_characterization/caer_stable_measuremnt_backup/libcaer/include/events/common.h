/**
 * @file common.h
 *
 * Common EventPacket header format definition and handling functions.
 * Every EventPacket, of any type, has as a first member a common header,
 * which describes various properties of the contained events. This allows
 * easy parsing of events. See the 'struct caer_event_packet_header'
 * documentation for more details.
 */

#ifndef LIBCAER_EVENTS_COMMON_H_
#define LIBCAER_EVENTS_COMMON_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "../libcaer.h"

/**
 * Generic validity mark:
 * this bit is used to mark whether an event is still
 * valid or not, and can be used to efficiently filter
 * out events from a packet.
 * The caerXXXEventValidate() and caerXXXEventInvalidate()
 * functions should be used to toggle this!
 * 0 in the 0th bit of the first byte means invalid, 1 means valid.
 * This way zeroing-out an event packet sets all its events to invalid.
 * Care must be taken to put the field containing the validity
 * mark always as the first member of an event.
 */
//@{
#define VALID_MARK_SHIFT 0
#define VALID_MARK_MASK 0x00000001
//@}

/**
 * 64bit timestamp support:
 * since timestamps wrap around after some time, being only 31 bit (32 bit signed int),
 * another timestamp at the packet level provides another 31 bit (32 bit signed int),
 * to enable the generation of a 62 bit (64 bit signed int) microsecond timestamp which
 * is guaranteed to never wrap around (in the next 146'138 years at least).
 * The TSOverflow needs to be shifted by 31 thus when constructing such a timestamp.
 */
#define TS_OVERFLOW_SHIFT 31

/**
 * List of supported event types.
 * Each event type has its own integer representation.
 * All event types below 100 are reserved for use
 * by libcaer and cAER.
 * DO NOT USE THEM FOR YOUR OWN EVENT TYPES!
 */
enum caer_default_event_types {
	SPECIAL_EVENT = 0,  //!< Special events.
	POLARITY_EVENT = 1, //!< Polarity (change, DVS) events.
	FRAME_EVENT = 2,    //!< Frame (intensity, APS) events.
	IMU6_EVENT = 3,     //!< 6 axes IMU events.
	IMU9_EVENT = 4,     //!< 9 axes IMU events.
	SAMPLE_EVENT = 5,   //!< ADC sample events.
	EAR_EVENT = 6,      //!< Ear (cochlea) events.
	CONFIG_EVENT = 7,   //!< Device configuration events.
	POINT1D_EVENT = 8,  //!< 1D measurement events.
	POINT2D_EVENT = 9,  //!< 2D measurement events.
	POINT3D_EVENT = 10, //!< 3D measurement events.
};

/**
 * Size of the EventPacket header.
 * This is constant across all supported systems.
 */
#define CAER_EVENT_PACKET_HEADER_SIZE 28

/**
 * EventPacket header data structure definition.
 * The size, also defined in CAER_EVENT_PACKET_HEADER_SIZE,
 * must always be constant. The header is common to all
 * types of event packets and is always the very first
 * member of an event packet data structure.
 * Signed integers are used for compatibility with languages that
 * do not have unsigned ones, such as Java.
 */
struct caer_event_packet_header {
	/// Numerical type ID, unique to each event type (see 'enum caer_default_event_types').
	int16_t eventType;
	/// Numerical source ID, unique inside a process, identifies who generated the events.
	int16_t eventSource;
	/// Size of one event in bytes.
	int32_t eventSize;
	/// Offset from the start of an event, in bytes, at which the main 32 bit time-stamp can be found.
	int32_t eventTSOffset;
	/// Overflow counter for the standard 32bit event time-stamp. Used to generate the 64 bit time-stamp.
	int32_t eventTSOverflow;
	/// Maximum number of events this packet can store.
	int32_t eventCapacity;
	/// Total number of events present in this packet (valid + invalid).
	int32_t eventNumber;
	/// Total number of valid events present in this packet.
	int32_t eventValid;
}__attribute__((__packed__));

/**
 * Type for pointer to EventPacket header data structure.
 */
typedef struct caer_event_packet_header *caerEventPacketHeader;

/**
 * Return the numerical event type ID, representing the event type this
 * EventPacket is containing.
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 *
 * @return the numerical event type (see 'enum caer_default_event_types').
 */
static inline int16_t caerEventPacketHeaderGetEventType(caerEventPacketHeader header) {
	return (le16toh(header->eventType));
}

/**
 * Set the numerical event type ID, representing the event type this
 * EventPacket will contain.
 * All event types below 100 are reserved for use by libcaer and cAER.
 * DO NOT USE THEM FOR YOUR OWN EVENT TYPES!
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 * @param eventType the numerical event type (see 'enum caer_default_event_types').
 */
static inline void caerEventPacketHeaderSetEventType(caerEventPacketHeader header, int16_t eventType) {
	if (eventType < 0) {
		// Negative numbers (bit 31 set) are not allowed!
		caerLog(CAER_LOG_CRITICAL, "EventPacket Header",
			"Called caerEventPacketHeaderSetEventType() with negative value!");
		return;
	}

	header->eventType = htole16(eventType);
}

/**
 * Get the numerical event source ID, representing the event source
 * that generated all the events present in this packet.
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 *
 * @return the numerical event source ID.
 */
static inline int16_t caerEventPacketHeaderGetEventSource(caerEventPacketHeader header) {
	return (le16toh(header->eventSource));
}

/**
 * Set the numerical event source ID, representing the event source
 * that generated all the events present in this packet.
 * This ID should be unique at least within a process, if not within
 * the whole system, to guarantee correct identification of who
 * generated an event later on.
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 * @param eventSource the numerical event source ID.
 */
static inline void caerEventPacketHeaderSetEventSource(caerEventPacketHeader header, int16_t eventSource) {
	if (eventSource < 0) {
		// Negative numbers (bit 31 set) are not allowed!
		caerLog(CAER_LOG_CRITICAL, "EventPacket Header",
			"Called caerEventPacketHeaderSetEventSource() with negative value!");
		return;
	}

	header->eventSource = htole16(eventSource);
}

/**
 * Get the size of a single event, in bytes.
 * All events inside an event packet always have the same size.
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 *
 * @return the event size in bytes.
 */
static inline int32_t caerEventPacketHeaderGetEventSize(caerEventPacketHeader header) {
	return (le32toh(header->eventSize));
}

/**
 * Set the size of a single event, in bytes.
 * All events inside an event packet always have the same size.
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 * @param eventSize the event size in bytes.
 */
static inline void caerEventPacketHeaderSetEventSize(caerEventPacketHeader header, int32_t eventSize) {
	if (eventSize < 0) {
		// Negative numbers (bit 31 set) are not allowed!
		caerLog(CAER_LOG_CRITICAL, "EventPacket Header",
			"Called caerEventPacketHeaderSetEventSize() with negative value!");
		return;
	}

	header->eventSize = htole32(eventSize);
}

/**
 * Get the offset, in bytes, to where the field with the main
 * 32 bit timestamp is stored. This is useful for generic access
 * to the timestamp field, given that different event types might
 * have it at different offsets or might even have multiple
 * timestamps, in which case this offset references the 'main'
 * timestamp, the most representative one.
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 *
 * @return the event timestamp offset in bytes.
 */
static inline int32_t caerEventPacketHeaderGetEventTSOffset(caerEventPacketHeader header) {
	return (le32toh(header->eventTSOffset));
}

/**
 * Set the offset, in bytes, to where the field with the main
 * 32 bit timestamp is stored. This is useful for generic access
 * to the timestamp field, given that different event types might
 * have it at different offsets or might even have multiple
 * timestamps, in which case this offset references the 'main'
 * timestamp, the most representative one.
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 * @param eventTSOffset the event timestamp offset in bytes.
 */
static inline void caerEventPacketHeaderSetEventTSOffset(caerEventPacketHeader header, int32_t eventTSOffset) {
	if (eventTSOffset < 0) {
		// Negative numbers (bit 31 set) are not allowed!
		caerLog(CAER_LOG_CRITICAL, "EventPacket Header",
			"Called caerEventPacketHeaderSetEventTSOffset() with negative value!");
		return;
	}

	header->eventTSOffset = htole32(eventTSOffset);
}

/**
 * Get the 32 bit timestamp overflow counter (in microseconds). This is per-packet
 * and is used to generate a 64 bit timestamp that never wraps around.
 * Since timestamps wrap around after some time, being only 31 bit (32 bit signed int),
 * another timestamp at the packet level provides another 31 bit (32 bit signed int),
 * to enable the generation of a 62 bit (64 bit signed int) microsecond timestamp which
 * is guaranteed to never wrap around (in the next 146'138 years at least).
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 *
 * @return the packet-level timestamp overflow counter, in microseconds.
 */
static inline int32_t caerEventPacketHeaderGetEventTSOverflow(caerEventPacketHeader header) {
	return (le32toh(header->eventTSOverflow));
}

/**
 * Set the 32 bit timestamp overflow counter (in microseconds). This is per-packet
 * and is used to generate a 64 bit timestamp that never wraps around.
 * Since timestamps wrap around after some time, being only 31 bit (32 bit signed int),
 * another timestamp at the packet level provides another 31 bit (32 bit signed int),
 * to enable the generation of a 62 bit (64 bit signed int) microsecond timestamp which
 * is guaranteed to never wrap around (in the next 146'138 years at least).
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 * @param eventTSOverflow the packet-level timestamp overflow counter, in microseconds.
 */
static inline void caerEventPacketHeaderSetEventTSOverflow(caerEventPacketHeader header, int32_t eventTSOverflow) {
	if (eventTSOverflow < 0) {
		// Negative numbers (bit 31 set) are not allowed!
		caerLog(CAER_LOG_CRITICAL, "EventPacket Header",
			"Called caerEventPacketHeaderSetEventTSOverflow() with negative value!");
		return;
	}

	header->eventTSOverflow = htole32(eventTSOverflow);
}

/**
 * Get the maximum number of events this packet can store.
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 *
 * @return the number of events this packet can hold.
 */
static inline int32_t caerEventPacketHeaderGetEventCapacity(caerEventPacketHeader header) {
	return (le32toh(header->eventCapacity));
}

/**
 * Set the maximum number of events this packet can store.
 * This is determined at packet allocation time and should
 * not be changed during the life-time of the packet.
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 * @param eventsCapacity the number of events this packet can hold.
 */
static inline void caerEventPacketHeaderSetEventCapacity(caerEventPacketHeader header, int32_t eventsCapacity) {
	if (eventsCapacity < 0) {
		// Negative numbers (bit 31 set) are not allowed!
		caerLog(CAER_LOG_CRITICAL, "EventPacket Header",
			"Called caerEventPacketHeaderSetEventCapacity() with negative value!");
		return;
	}

	header->eventCapacity = htole32(eventsCapacity);
}

/**
 * Get the number of events currently stored in this packet,
 * considering both valid and invalid events.
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 *
 * @return the number of events in this packet.
 */
static inline int32_t caerEventPacketHeaderGetEventNumber(caerEventPacketHeader header) {
	return (le32toh(header->eventNumber));
}

/**
 * Set the number of events currently stored in this packet,
 * considering both valid and invalid events.
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 * @param eventsNumber the number of events in this packet.
 */
static inline void caerEventPacketHeaderSetEventNumber(caerEventPacketHeader header, int32_t eventsNumber) {
	if (eventsNumber < 0) {
		// Negative numbers (bit 31 set) are not allowed!
		caerLog(CAER_LOG_CRITICAL, "EventPacket Header",
			"Called caerEventPacketHeaderSetEventNumber() with negative value!");
		return;
	}

	header->eventNumber = htole32(eventsNumber);
}

/**
 * Get the number of valid events in this packet, disregarding
 * invalid ones (where the invalid mark is set).
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 *
 * @return the number of valid events in this packet.
 */
static inline int32_t caerEventPacketHeaderGetEventValid(caerEventPacketHeader header) {
	return (le32toh(header->eventValid));
}

/**
 * Set the number of valid events in this packet, disregarding
 * invalid ones (where the invalid mark is set).
 *
 * @param header a valid EventPacket header pointer. Cannot be NULL.
 * @param eventsValid the number of valid events in this packet.
 */
static inline void caerEventPacketHeaderSetEventValid(caerEventPacketHeader header, int32_t eventsValid) {
	if (eventsValid < 0) {
		// Negative numbers (bit 31 set) are not allowed!
		caerLog(CAER_LOG_CRITICAL, "EventPacket Header",
			"Called caerEventPacketHeaderSetEventValid() with negative value!");
		return;
	}

	header->eventValid = htole32(eventsValid);
}

/**
 * Get a generic pointer to an event, without having to know what event
 * type the packet is containing.
 *
 * @param headerPtr a valid EventPacket header pointer. Cannot be NULL.
 * @param n the index of the returned event. Must be within [0,eventCapacity[ bounds.
 *
 * @return a generic pointer to the requested event. NULL on error.
 */
static inline void *caerGenericEventGetEvent(caerEventPacketHeader headerPtr, int32_t n) {
	// Check that we're not out of bounds.
	if (n < 0 || n >= caerEventPacketHeaderGetEventCapacity(headerPtr)) {
		caerLog(CAER_LOG_CRITICAL, "Generic Event",
			"Called caerGenericEventGetEvent() with invalid event offset %" PRIi32 ", while maximum allowed value is %" PRIi32 ". Negative values are not allowed!",
			n, caerEventPacketHeaderGetEventCapacity(headerPtr) - 1);
		return (NULL);
	}

	// Return a pointer to the specified event.
	return (((uint8_t *) headerPtr)
		+ (CAER_EVENT_PACKET_HEADER_SIZE + U64T(n * caerEventPacketHeaderGetEventSize(headerPtr))));
}

/**
 * Get the main 32 bit timestamp for a generic event, without having to
 * know what event type the packet is containing.
 *
 * @param eventPtr a generic pointer to an event. Cannot be NULL.
 * @param headerPtr a valid EventPacket header pointer. Cannot be NULL.
 *
 * @return the main 32 bit timestamp of this event.
 */
static inline int32_t caerGenericEventGetTimestamp(void *eventPtr, caerEventPacketHeader headerPtr) {
	return (le32toh(*((int32_t *) (((uint8_t *) eventPtr) + U64T(caerEventPacketHeaderGetEventTSOffset(headerPtr))))));
}

/**
 * Get the main 64 bit timestamp for a generic event, without having to
 * know what event type the packet is containing. This takes the
 * per-packet timestamp into account too, generating a timestamp
 * that doesn't suffer from overflow problems.
 *
 * @param eventPtr a generic pointer to an event. Cannot be NULL.
 * @param headerPtr a valid EventPacket header pointer. Cannot be NULL.
 *
 * @return the main 64 bit timestamp of this event.
 */
static inline int64_t caerGenericEventGetTimestamp64(void *eventPtr, caerEventPacketHeader headerPtr) {
	return (I64T(
		(U64T(caerEventPacketHeaderGetEventTSOverflow(headerPtr)) << TS_OVERFLOW_SHIFT) | U64T(caerGenericEventGetTimestamp(eventPtr, headerPtr))));
}

/**
 * Check if the given generic event is valid or not.
 *
 * @param eventPtr a generic pointer to an event. Cannot be NULL.
 *
 * @return true if the event is valid, false otherwise.
 */
static inline bool caerGenericEventIsValid(void *eventPtr) {
	// Look at first byte of event memory's lowest bit.
	// This should always work since first event member must contain the valid mark
	// and memory is little-endian, so lowest bit must be in first byte of memory.
	return (*((uint8_t *) eventPtr) & VALID_MARK_MASK);
}

/**
 * Generic iterator over all events in a packet.
 * Returns the current index in the 'caerIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerIteratorElement' variable
 * of type EVENT_TYPE.
 *
 * PACKET_HEADER: a valid EventPacket header pointer. Cannot be NULL.
 * EVENT_TYPE: the event pointer type for this EventPacket (ie. caerPolarityEvent or caerFrameEvent).
 */
#define CAER_ITERATOR_ALL_START(PACKET_HEADER, EVENT_TYPE) \
	for (int32_t caerIteratorCounter = 0; \
		caerIteratorCounter < caerEventPacketHeaderGetEventNumber(PACKET_HEADER); \
		caerIteratorCounter++) { \
		EVENT_TYPE caerIteratorElement = (EVENT_TYPE) caerGenericEventGetEvent(PACKET_HEADER, caerIteratorCounter);

/**
 * Generic iterator close statement.
 */
#define CAER_ITERATOR_ALL_END }

/**
 * Generic iterator over only the valid events in a packet.
 * Returns the current index in the 'caerIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerIteratorElement' variable
 * of type EVENT_TYPE.
 *
 * PACKET_HEADER: a valid EventPacket header pointer. Cannot be NULL.
 * EVENT_TYPE: the event pointer type for this EventPacket (ie. caerPolarityEvent or caerFrameEvent).
 */
#define CAER_ITERATOR_VALID_START(PACKET_HEADER, EVENT_TYPE) \
	for (int32_t caerIteratorCounter = 0; \
		caerIteratorCounter < caerEventPacketHeaderGetEventNumber(PACKET_HEADER); \
		caerIteratorCounter++) { \
		EVENT_TYPE caerIteratorElement = (EVENT_TYPE) caerGenericEventGetEvent(PACKET_HEADER, caerIteratorCounter); \
		if (!caerGenericEventIsValid(caerIteratorElement)) { continue; } // Skip invalid events.

/**
 * Generic iterator close statement.
 */
#define CAER_ITERATOR_VALID_END }

// Functions for event packet copying.

/**
 * Make a full copy of an event packet (up to eventCapacity).
 *
 * @param eventPacket an event packet to copy.
 *
 * @return a full copy of an event packet.
 */
static inline void *caerCopyEventPacket(void *eventPacket) {
	// Handle empty event packets.
	if (eventPacket == NULL) {
		return (NULL);
	}

	// Calculate needed memory for new event packet.
	caerEventPacketHeader header = (caerEventPacketHeader) eventPacket;
	int32_t eventSize = caerEventPacketHeaderGetEventSize(header);
	int32_t eventNumber = caerEventPacketHeaderGetEventNumber(header);
	int32_t eventCapacity = caerEventPacketHeaderGetEventCapacity(header);
	size_t packetMem = CAER_EVENT_PACKET_HEADER_SIZE + (size_t) (eventSize * eventCapacity);
	size_t dataMem = CAER_EVENT_PACKET_HEADER_SIZE + (size_t) (eventSize * eventNumber);

	// Allocate memory for new event packet.
	caerEventPacketHeader eventPacketCopy = (caerEventPacketHeader) malloc(packetMem);
	if (eventPacketCopy == NULL) {
		// Failed to allocate memory.
		return (NULL);
	}

	// Copy the data over.
	memcpy(eventPacketCopy, eventPacket, dataMem);

	return (eventPacketCopy);
}

/**
 * Make a copy of an event packet, sized down to only include the
 * currently present events (eventNumber, valid+invalid), and not
 * including the possible extra unused events (up to eventCapacity).
 *
 * @param eventPacket an event packet to copy.
 *
 * @return a sized down copy of an event packet.
 */
static inline void *caerCopyEventPacketOnlyEvents(void *eventPacket) {
	// Handle empty event packets.
	if (eventPacket == NULL) {
		return (NULL);
	}

	// Calculate needed memory for new event packet.
	caerEventPacketHeader header = (caerEventPacketHeader) eventPacket;
	int32_t eventSize = caerEventPacketHeaderGetEventSize(header);
	int32_t eventNumber = caerEventPacketHeaderGetEventNumber(header);
	size_t packetMem = CAER_EVENT_PACKET_HEADER_SIZE + (size_t) (eventSize * eventNumber);

	// Allocate memory for new event packet.
	caerEventPacketHeader eventPacketCopy = (caerEventPacketHeader) malloc(packetMem);
	if (eventPacketCopy == NULL) {
		// Failed to allocate memory.
		return (NULL);
	}

	// Copy the data over.
	memcpy(eventPacketCopy, eventPacket, packetMem);

	// Set the event capacity to the event number, since we only allocated
	// memory for that many events.
	caerEventPacketHeaderSetEventCapacity(eventPacketCopy, eventNumber);

	return (eventPacketCopy);
}

/**
 * Make a copy of an event packet, sized down to only include the
 * currently valid events (eventValid), and discarding everything else.
 *
 * @param eventPacket an event packet to copy.
 *
 * @return a copy of an event packet, containing only valid events.
 */
static inline void *caerCopyEventPacketOnlyValidEvents(void *eventPacket) {
	// Handle empty event packets.
	if (eventPacket == NULL) {
		return (NULL);
	}

	// Calculate needed memory for new event packet.
	caerEventPacketHeader header = (caerEventPacketHeader) eventPacket;
	int32_t eventSize = caerEventPacketHeaderGetEventSize(header);
	int32_t eventValid = caerEventPacketHeaderGetEventValid(header);
	size_t packetMem = CAER_EVENT_PACKET_HEADER_SIZE + (size_t) (eventSize * eventValid);

	// Allocate memory for new event packet.
	caerEventPacketHeader eventPacketCopy = (caerEventPacketHeader) malloc(packetMem);
	if (eventPacketCopy == NULL) {
		// Failed to allocate memory.
		return (NULL);
	}

	// Copy the data over. Must check every event for validity!
	size_t offset = 0;
	CAER_ITERATOR_VALID_START(header, void *)
		memcpy(eventPacketCopy + offset, caerIteratorElement, (size_t) eventSize);
		offset += (size_t) eventSize;
	CAER_ITERATOR_VALID_END

	// Set the event capacity and the event number to the number of
	// valid events, since we only copied those.
	caerEventPacketHeaderSetEventCapacity(eventPacketCopy, eventValid);
	caerEventPacketHeaderSetEventNumber(eventPacketCopy, eventValid);

	return (eventPacketCopy);
}

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_EVENTS_COMMON_H_ */
