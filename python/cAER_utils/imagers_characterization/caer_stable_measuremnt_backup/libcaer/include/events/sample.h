/**
 * @file sample.h
 *
 * Sample (ADC) Events format definition and handling functions.
 * Represents different types of ADC readings, up to 24 bits
 * of resolution.
 */

#ifndef LIBCAER_EVENTS_SAMPLE_H_
#define LIBCAER_EVENTS_SAMPLE_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "common.h"

/**
 * Shift and mask values for the sample type and the actual
 * sample value of an ADC sample.
 * Up to 128 sample types are supported, with 24 bits of
 * data per sample. Higher values mean a higher voltage,
 * 0 is ground.
 * Bit 0 is the valid mark, see 'common.h' for more details.
 */
//@{
#define SAMPLE_TYPE_SHIFT 1
#define SAMPLE_TYPE_MASK 0x0000007F
#define SAMPLE_SHIFT 8
#define SAMPLE_MASK 0x00FFFFFF
//@}

/**
 * ADC sample event data structure definition.
 * Contains a type indication to separate different ADC readouts,
 * as well as a value for that readout, up to 24 bits resolution.
 * Signed integers are used for fields that are to be interpreted
 * directly, for compatibility with languages that do not have
 * unsigned integer types, such as Java.
 */
struct caer_sample_event {
	/// Event data. First because of valid mark.
	uint32_t data;
	/// Event timestamp.
	int32_t timestamp;
}__attribute__((__packed__));

/**
 * Type for pointer to ADC sample event data structure.
 */
typedef struct caer_sample_event *caerSampleEvent;

/**
 * ADC sample event packet data structure definition.
 * EventPackets are always made up of the common packet header,
 * followed by 'eventCapacity' events. Everything has to
 * be in one contiguous memory block.
 */
struct caer_sample_event_packet {
	/// The common event packet header.
	struct caer_event_packet_header packetHeader;
	/// The events array.
	struct caer_sample_event events[];
}__attribute__((__packed__));

/**
 * Type for pointer to ADC sample event packet data structure.
 */
typedef struct caer_sample_event_packet *caerSampleEventPacket;

/**
 * Allocate a new ADC sample events packet.
 * Use free() to reclaim this memory.
 *
 * @param eventCapacity the maximum number of events this packet will hold.
 * @param eventSource the unique ID representing the source/generator of this packet.
 * @param tsOverflow the current timestamp overflow counter value for this packet.
 *
 * @return a valid SampleEventPacket handle or NULL on error.
 */
caerSampleEventPacket caerSampleEventPacketAllocate(int32_t eventCapacity, int16_t eventSource, int32_t tsOverflow);

/**
 * Get the ADC sample event at the given index from the event packet.
 *
 * @param packet a valid SampleEventPacket pointer. Cannot be NULL.
 * @param n the index of the returned event. Must be within [0,eventCapacity[ bounds.
 *
 * @return the requested ADC sample event. NULL on error.
 */
static inline caerSampleEvent caerSampleEventPacketGetEvent(caerSampleEventPacket packet, int32_t n) {
	// Check that we're not out of bounds.
	if (n < 0 || n >= caerEventPacketHeaderGetEventCapacity(&packet->packetHeader)) {
		caerLog(CAER_LOG_CRITICAL, "Sample Event",
			"Called caerSampleEventPacketGetEvent() with invalid event offset %" PRIi32 ", while maximum allowed value is %" PRIi32 ".",
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
 * @param event a valid SampleEvent pointer. Cannot be NULL.
 *
 * @return this event's 32bit microsecond timestamp.
 */
static inline int32_t caerSampleEventGetTimestamp(caerSampleEvent event) {
	return (le32toh(event->timestamp));
}

/**
 * Get the 64bit event timestamp, in microseconds.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid SampleEvent pointer. Cannot be NULL.
 * @param packet the SampleEventPacket pointer for the packet containing this event. Cannot be NULL.
 *
 * @return this event's 64bit microsecond timestamp.
 */
static inline int64_t caerSampleEventGetTimestamp64(caerSampleEvent event, caerSampleEventPacket packet) {
	return (I64T(
		(U64T(caerEventPacketHeaderGetEventTSOverflow(&packet->packetHeader)) << TS_OVERFLOW_SHIFT) | U64T(caerSampleEventGetTimestamp(event))));
}

/**
 * Set the 32bit event timestamp, the value has to be in microseconds.
 *
 * @param event a valid SampleEvent pointer. Cannot be NULL.
 * @param timestamp a positive 32bit microsecond timestamp.
 */
static inline void caerSampleEventSetTimestamp(caerSampleEvent event, int32_t timestamp) {
	if (timestamp < 0) {
		// Negative means using the 31st bit!
		caerLog(CAER_LOG_CRITICAL, "Sample Event", "Called caerSampleEventSetTimestamp() with negative value!");
		return;
	}

	event->timestamp = htole32(timestamp);
}

/**
 * Check if this ADC sample event is valid.
 *
 * @param event a valid SampleEvent pointer. Cannot be NULL.
 *
 * @return true if valid, false if not.
 */
static inline bool caerSampleEventIsValid(caerSampleEvent event) {
	return (GET_NUMBITS32(event->data, VALID_MARK_SHIFT, VALID_MARK_MASK));
}

/**
 * Validate the current event by setting its valid bit to true
 * and increasing the event packet's event count and valid
 * event count. Only works on events that are invalid.
 * DO NOT CALL THIS AFTER HAVING PREVIOUSLY ALREADY
 * INVALIDATED THIS EVENT, the total count will be incorrect.
 *
 * @param event a valid SampleEvent pointer. Cannot be NULL.
 * @param packet the SampleEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerSampleEventValidate(caerSampleEvent event, caerSampleEventPacket packet) {
	if (!caerSampleEventIsValid(event)) {
		SET_NUMBITS32(event->data, VALID_MARK_SHIFT, VALID_MARK_MASK, 1);

		// Also increase number of events and valid events.
		// Only call this on (still) invalid events!
		caerEventPacketHeaderSetEventNumber(&packet->packetHeader,
			caerEventPacketHeaderGetEventNumber(&packet->packetHeader) + 1);
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) + 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Sample Event", "Called caerSampleEventValidate() on already valid event.");
	}
}

/**
 * Invalidate the current event by setting its valid bit
 * to false and decreasing the number of valid events held
 * in the packet. Only works with events that are already
 * valid!
 *
 * @param event a valid SampleEvent pointer. Cannot be NULL.
 * @param packet the SampleEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerSampleEventInvalidate(caerSampleEvent event, caerSampleEventPacket packet) {
	if (caerSampleEventIsValid(event)) {
		CLEAR_NUMBITS32(event->data, VALID_MARK_SHIFT, VALID_MARK_MASK);

		// Also decrease number of valid events. Number of total events doesn't change.
		// Only call this on valid events!
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) - 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Sample Event", "Called caerSampleEventInvalidate() on already invalid event.");
	}
}

/**
 * Get the ADC sample event type. This is useful to distinguish
 * between different measurements, for example from two separate
 * microphones on a device.
 *
 * @param event a valid SampleEvent pointer. Cannot be NULL.
 *
 * @return the ADC sample type.
 */
static inline uint8_t caerSampleEventGetType(caerSampleEvent event) {
	return U8T(GET_NUMBITS32(event->data, SAMPLE_TYPE_SHIFT, SAMPLE_TYPE_MASK));
}

/**
 * Set the ADC sample event type. This is useful to distinguish
 * between different measurements, for example from two separate
 * microphones on a device.
 *
 * @param event a valid SampleEvent pointer. Cannot be NULL.
 * @param type the ADC sample type.
 */
static inline void caerSampleEventSetType(caerSampleEvent event, uint8_t type) {
	CLEAR_NUMBITS32(event->data, SAMPLE_TYPE_SHIFT, SAMPLE_TYPE_MASK);
	SET_NUMBITS32(event->data, SAMPLE_TYPE_SHIFT, SAMPLE_TYPE_MASK, type);
}

/**
 * Get the ADC sample value. Up to 24 bits of resolution are possible.
 * Higher values mean a higher voltage, 0 is ground.
 *
 * @param event a valid SampleEvent pointer. Cannot be NULL.
 *
 * @return the ADC sample value.
 */
static inline uint32_t caerSampleEventGetSample(caerSampleEvent event) {
	return U32T(GET_NUMBITS32(event->data, SAMPLE_SHIFT, SAMPLE_MASK));
}

/**
 * Set the ADC sample value. Up to 24 bits of resolution are possible.
 * Higher values mean a higher voltage, 0 is ground.
 *
 * @param event a valid SampleEvent pointer. Cannot be NULL.
 * @param sample the ADC sample value.
 */
static inline void caerSampleEventSetSample(caerSampleEvent event, uint32_t sample) {
	CLEAR_NUMBITS32(event->data, SAMPLE_SHIFT, SAMPLE_MASK);
	SET_NUMBITS32(event->data, SAMPLE_SHIFT, SAMPLE_MASK, sample);
}

/**
 * Iterator over all sample events in a packet.
 * Returns the current index in the 'caerSampleIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerSampleIteratorElement' variable
 * of type caerSampleEvent.
 *
 * SAMPLE_PACKET: a valid SampleEventPacket pointer. Cannot be NULL.
 */
#define CAER_SAMPLE_ITERATOR_ALL_START(SAMPLE_PACKET) \
	for (int32_t caerSampleIteratorCounter = 0; \
		caerSampleIteratorCounter < caerEventPacketHeaderGetEventNumber(&(SAMPLE_PACKET)->packetHeader); \
		caerSampleIteratorCounter++) { \
		caerSampleEvent caerSampleIteratorElement = caerSampleEventPacketGetEvent(SAMPLE_PACKET, caerSampleIteratorCounter);

/**
 * Iterator close statement.
 */
#define CAER_SAMPLE_ITERATOR_ALL_END }

/**
 * Iterator over only the valid sample events in a packet.
 * Returns the current index in the 'caerSampleIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerSampleIteratorElement' variable
 * of type caerSampleEvent.
 *
 * SAMPLE_PACKET: a valid SampleEventPacket pointer. Cannot be NULL.
 */
#define CAER_SAMPLE_ITERATOR_VALID_START(SAMPLE_PACKET) \
	for (int32_t caerSampleIteratorCounter = 0; \
		caerSampleIteratorCounter < caerEventPacketHeaderGetEventNumber(&(SAMPLE_PACKET)->packetHeader); \
		caerSampleIteratorCounter++) { \
		caerSampleEvent caerSampleIteratorElement = caerSampleEventPacketGetEvent(SAMPLE_PACKET, caerSampleIteratorCounter); \
		if (!caerSampleEventIsValid(caerSampleIteratorElement)) { continue; } // Skip invalid sample events.

/**
 * Iterator close statement.
 */
#define CAER_SAMPLE_ITERATOR_VALID_END }

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_EVENTS_SAMPLE_H_ */
