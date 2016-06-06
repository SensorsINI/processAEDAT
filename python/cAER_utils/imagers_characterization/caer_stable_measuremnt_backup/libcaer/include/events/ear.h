/**
 * @file ear.h
 *
 * Ear (Cochlea) Events format definition and handling functions.
 * This encodes events from a silicon cochlea chip, containing
 * information about which ear (microphone) generated the event,
 * as well as which channel was involved and additional information
 * on filters and neurons.
 */

#ifndef LIBCAER_EVENTS_EAR_H_
#define LIBCAER_EVENTS_EAR_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "common.h"

/**
 * Shift and mask values for the ear event values coming from
 * a cochlea: the ear position (up to 16), the channel number
 * (up to 2048), the ganglion (up to 256) and the filter (up to 256).
 * Bit 0 is the valid mark, see 'common.h' for more details.
 */
//@{
#define EAR_SHIFT 1
#define EAR_MASK 0x0000000F
#define CHANNEL_SHIFT 5
#define CHANNEL_MASK 0x000007FF
#define NEURON_SHIFT 16
#define NEURON_MASK 0x000000FF
#define FILTER_SHIFT 24
#define FILTER_MASK 0x000000FF
//@}

/**
 * Ear (cochlea) event data structure definition.
 * Contains information on events gotten from a cochlea chip:
 * ears, channels, neurons and filters are stored.
 * Signed integers are used for fields that are to be interpreted
 * directly, for compatibility with languages that do not have
 * unsigned integer types, such as Java.
 */
struct caer_ear_event {
	/// Event data. First because of valid mark.
	uint32_t data;
	/// Event timestamp.
	int32_t timestamp;
}__attribute__((__packed__));

/**
 * Type for pointer to ear (cochlea) event data structure.
 */
typedef struct caer_ear_event *caerEarEvent;

/**
 * Ear (cochlea) event packet data structure definition.
 * EventPackets are always made up of the common packet header,
 * followed by 'eventCapacity' events. Everything has to
 * be in one contiguous memory block.
 */
struct caer_ear_event_packet {
	/// The common event packet header.
	struct caer_event_packet_header packetHeader;
	/// The events array.
	struct caer_ear_event events[];
}__attribute__((__packed__));

/**
 * Type for pointer to ear (cochlea) event packet data structure.
 */
typedef struct caer_ear_event_packet *caerEarEventPacket;

/**
 * Allocate a new ear (cochlea) events packet.
 * Use free() to reclaim this memory.
 *
 * @param eventCapacity the maximum number of events this packet will hold.
 * @param eventSource the unique ID representing the source/generator of this packet.
 * @param tsOverflow the current timestamp overflow counter value for this packet.
 *
 * @return a valid EarEventPacket handle or NULL on error.
 */
caerEarEventPacket caerEarEventPacketAllocate(int32_t eventCapacity, int16_t eventSource, int32_t tsOverflow);

/**
 * Get the ear (cochlea) event at the given index from the event packet.
 *
 * @param packet a valid EarEventPacket pointer. Cannot be NULL.
 * @param n the index of the returned event. Must be within [0,eventCapacity[ bounds.
 *
 * @return the requested ear (cochlea) event. NULL on error.
 */
static inline caerEarEvent caerEarEventPacketGetEvent(caerEarEventPacket packet, int32_t n) {
	// Check that we're not out of bounds.
	if (n < 0 || n >= caerEventPacketHeaderGetEventCapacity(&packet->packetHeader)) {
		caerLog(CAER_LOG_CRITICAL, "Ear Event",
			"Called caerEarEventPacketGetEvent() with invalid event offset %" PRIi32 ", while maximum allowed value is %" PRIi32 ".",
			n, caerEventPacketHeaderGetEventCapacity(&packet->packetHeader) - 1);
		return (NULL);
	}

	// Return a pointer to the specified event.
	return (packet->events + n);
}

/**
 * Get the 32bit event timestamp, in microseconds.
 * Be aware that this wraps around! You can either ignore this fact,
 * or handle the special 'TIMESTAMP_WRAP' event that is generated when
 * this happens, or use the 64bit timestamp which never wraps around.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid EarEvent pointer. Cannot be NULL.
 *
 * @return this event's 32bit microsecond timestamp.
 */
static inline int32_t caerEarEventGetTimestamp(caerEarEvent event) {
	return (le32toh(event->timestamp));
}

/**
 * Get the 64bit event timestamp, in microseconds.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid EarEvent pointer. Cannot be NULL.
 * @param packet the EarEventPacket pointer for the packet containing this event. Cannot be NULL.
 *
 * @return this event's 64bit microsecond timestamp.
 */
static inline int64_t caerEarEventGetTimestamp64(caerEarEvent event, caerEarEventPacket packet) {
	return (I64T(
		(U64T(caerEventPacketHeaderGetEventTSOverflow(&packet->packetHeader)) << TS_OVERFLOW_SHIFT) | U64T(caerEarEventGetTimestamp(event))));
}

/**
 * Set the 32bit event timestamp, the value has to be in microseconds.
 *
 * @param event a valid EarEvent pointer. Cannot be NULL.
 * @param timestamp a positive 32bit microsecond timestamp.
 */
static inline void caerEarEventSetTimestamp(caerEarEvent event, int32_t timestamp) {
	if (timestamp < 0) {
		// Negative means using the 31st bit!
		caerLog(CAER_LOG_CRITICAL, "Ear Event", "Called caerEarEventSetTimestamp() with negative value!");
		return;
	}

	event->timestamp = htole32(timestamp);
}

/**
 * Check if this ear (cochlea) event is valid.
 *
 * @param event a valid EarEvent pointer. Cannot be NULL.
 *
 * @return true if valid, false if not.
 */
static inline bool caerEarEventIsValid(caerEarEvent event) {
	return (GET_NUMBITS32(event->data, VALID_MARK_SHIFT, VALID_MARK_MASK));
}

/**
 * Validate the current event by setting its valid bit to true
 * and increasing the event packet's event count and valid
 * event count. Only works on events that are invalid.
 * DO NOT CALL THIS AFTER HAVING PREVIOUSLY ALREADY
 * INVALIDATED THIS EVENT, the total count will be incorrect.
 *
 * @param event a valid EarEvent pointer. Cannot be NULL.
 * @param packet the EarEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerEarEventValidate(caerEarEvent event, caerEarEventPacket packet) {
	if (!caerEarEventIsValid(event)) {
		SET_NUMBITS32(event->data, VALID_MARK_SHIFT, VALID_MARK_MASK, 1);

		// Also increase number of events and valid events.
		// Only call this on (still) invalid events!
		caerEventPacketHeaderSetEventNumber(&packet->packetHeader,
			caerEventPacketHeaderGetEventNumber(&packet->packetHeader) + 1);
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) + 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Ear Event", "Called caerEarEventValidate() on already valid event.");
	}
}

/**
 * Invalidate the current event by setting its valid bit
 * to false and decreasing the number of valid events held
 * in the packet. Only works with events that are already
 * valid!
 *
 * @param event a valid EarEvent pointer. Cannot be NULL.
 * @param packet the EarEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerEarEventInvalidate(caerEarEvent event, caerEarEventPacket packet) {
	if (caerEarEventIsValid(event)) {
		CLEAR_NUMBITS32(event->data, VALID_MARK_SHIFT, VALID_MARK_MASK);

		// Also decrease number of valid events. Number of total events doesn't change.
		// Only call this on valid events!
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) - 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Ear Event", "Called caerEarEventInvalidate() on already invalid event.");
	}
}

/**
 * Get the numerical ID of the ear (microphone).
 * Usually, 0 is left, 1 is right for 2 ear cochleas.
 * For 4 ear cochleas, 0 is front left, 1 is front right,
 * 2 is back left and 3 is back right.
 *
 * @param event a valid EarEvent pointer. Cannot be NULL.
 *
 * @return the ear (microphone) ID.
 */
static inline uint8_t caerEarEventGetEar(caerEarEvent event) {
	return U8T(GET_NUMBITS32(event->data, EAR_SHIFT, EAR_MASK));
}

/**
 * Set the numerical ID of the ear (microphone).
 * Usually, 0 is left, 1 is right for 2 ear cochleas.
 * For 4 ear cochleas, 0 is front left, 1 is front right,
 * 2 is back left and 3 is back right.
 *
 * @param event a valid EarEvent pointer. Cannot be NULL.
 * @param ear the ear (microphone) ID.
 */
static inline void caerEarEventSetEar(caerEarEvent event, uint8_t ear) {
	CLEAR_NUMBITS32(event->data, EAR_SHIFT, EAR_MASK);
	SET_NUMBITS32(event->data, EAR_SHIFT, EAR_MASK, ear);
}

/**
 * Get the channel (frequency band) ID.
 * The channels count from 0 upward, where 0 is the highest
 * frequency channel, while higher numbers are progressively
 * lower frequency channels. This is derived from how the actual
 * human ear works.
 *
 * @param event a valid EarEvent pointer. Cannot be NULL.
 *
 * @return the channel (frequency band) ID.
 */
static inline uint16_t caerEarEventGetChannel(caerEarEvent event) {
	return U16T(GET_NUMBITS32(event->data, CHANNEL_SHIFT, CHANNEL_MASK));
}

/**
 * Set the channel (frequency band) ID.
 * The channels count from 0 upward, where 0 is the highest
 * frequency channel, while higher numbers are progressively
 * lower frequency channels. This is derived from how the actual
 * human ear works.
 *
 * @param event a valid EarEvent pointer. Cannot be NULL.
 * @param channel the channel (frequency band) ID.
 */
static inline void caerEarEventSetChannel(caerEarEvent event, uint16_t channel) {
	CLEAR_NUMBITS32(event->data, CHANNEL_SHIFT, CHANNEL_MASK);
	SET_NUMBITS32(event->data, CHANNEL_SHIFT, CHANNEL_MASK, channel);
}

static inline uint8_t caerEarEventGetNeuron(caerEarEvent event) {
	return U8T(GET_NUMBITS32(event->data, NEURON_SHIFT, NEURON_MASK));
}

static inline void caerEarEventSetNeuron(caerEarEvent event, uint8_t neuron) {
	CLEAR_NUMBITS32(event->data, NEURON_SHIFT, NEURON_MASK);
	SET_NUMBITS32(event->data, NEURON_SHIFT, NEURON_MASK, neuron);
}

static inline uint8_t caerEarEventGetFilter(caerEarEvent event) {
	return U8T(GET_NUMBITS32(event->data, FILTER_SHIFT, FILTER_MASK));
}

static inline void caerEarEventSetFilter(caerEarEvent event, uint8_t filter) {
	CLEAR_NUMBITS32(event->data, FILTER_SHIFT, FILTER_MASK);
	SET_NUMBITS32(event->data, FILTER_SHIFT, FILTER_MASK, filter);
}

/**
 * Iterator over all ear events in a packet.
 * Returns the current index in the 'caerEarIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerEarIteratorElement' variable
 * of type caerEarEvent.
 *
 * EAR_PACKET: a valid EarEventPacket pointer. Cannot be NULL.
 */
#define CAER_EAR_ITERATOR_ALL_START(EAR_PACKET) \
	for (int32_t caerEarIteratorCounter = 0; \
		caerEarIteratorCounter < caerEventPacketHeaderGetEventNumber(&(EAR_PACKET)->packetHeader); \
		caerEarIteratorCounter++) { \
		caerEarEvent caerEarIteratorElement = caerEarEventPacketGetEvent(EAR_PACKET, caerEarIteratorCounter);

/**
 * Iterator close statement.
 */
#define CAER_EAR_ITERATOR_ALL_END }

/**
 * Iterator over only the valid ear events in a packet.
 * Returns the current index in the 'caerEarIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerEarIteratorElement' variable
 * of type caerEarEvent.
 *
 * EAR_PACKET: a valid EarEventPacket pointer. Cannot be NULL.
 */
#define CAER_EAR_ITERATOR_VALID_START(EAR_PACKET) \
	for (int32_t caerEarIteratorCounter = 0; \
		caerEarIteratorCounter < caerEventPacketHeaderGetEventNumber(&(EAR_PACKET)->packetHeader); \
		caerEarIteratorCounter++) { \
		caerEarEvent caerEarIteratorElement = caerEarEventPacketGetEvent(EAR_PACKET, caerEarIteratorCounter); \
		if (!caerEarEventIsValid(caerEarIteratorElement)) { continue; } // Skip invalid ear events.

/**
 * Iterator close statement.
 */
#define CAER_EAR_ITERATOR_VALID_END }

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_EVENTS_EAR_H_ */
