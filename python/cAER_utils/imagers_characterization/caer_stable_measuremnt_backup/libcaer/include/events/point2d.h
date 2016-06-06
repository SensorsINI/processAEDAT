/**
 * @file point2d.h
 *
 * THIS EVENT DEFINITIONS IS STILL TO BE CONSIDERED EXPERIMENTAL
 * AND IS SUBJECT TO FUTURE CHANGES AND REVISIONS!
 *
 * Point2D Events format definition and handling functions.
 * This contains two dimensional data points as floats,
 * together with support for distinguishing type and scale.
 */

#ifndef LIBCAER_EVENTS_POINT2D_H_
#define LIBCAER_EVENTS_POINT2D_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "common.h"

/**
 * Shift and mask values for type and scale information
 * associated with a Point2D event.
 * Up to 128 types are supported. The scale is given as orders
 * of magnitude, from 10^-128 to 10^127.
 * Bit 0 is the valid mark, see 'common.h' for more details.
 */
//@{
#define POINT2D_TYPE_SHIFT 1
#define POINT2D_TYPE_MASK 0x0000007F
#define POINT2D_SCALE_SHIFT 8
#define POINT2D_SCALE_MASK 0x000000FF
//@}

/**
 * Point2D event data structure definition.
 * This contains information about the measurement, such as a type
 * and a scale field, together with the usual validity mark.
 * The two measurements (x, y) are stored as floats.
 * Floats are in IEEE 754-2008 binary32 format.
 * Signed integers are used for fields that are to be interpreted
 * directly, for compatibility with languages that do not have
 * unsigned integer types, such as Java.
 */
struct caer_point2d_event {
	/// Event information. First because of valid mark.
	uint32_t info;
	/// Event timestamp.
	int32_t timestamp;
	/// X axis measurement.
	float x;
	/// Y axis measurement.
	float y;
}__attribute__((__packed__));

/**
 * Type for pointer to Point2D event data structure.
 */
typedef struct caer_point2d_event *caerPoint2DEvent;

/**
 * Point2D event packet data structure definition.
 * EventPackets are always made up of the common packet header,
 * followed by 'eventCapacity' events. Everything has to
 * be in one contiguous memory block.
 */
struct caer_point2d_event_packet {
	/// The common event packet header.
	struct caer_event_packet_header packetHeader;
	/// The events array.
	struct caer_point2d_event events[];
}__attribute__((__packed__));

/**
 * Type for pointer to Point2D event packet data structure.
 */
typedef struct caer_point2d_event_packet *caerPoint2DEventPacket;

/**
 * Allocate a new Point2D events packet.
 * Use free() to reclaim this memory.
 *
 * @param eventCapacity the maximum number of events this packet will hold.
 * @param eventSource the unique ID representing the source/generator of this packet.
 * @param tsOverflow the current timestamp overflow counter value for this packet.
 *
 * @return a valid Point2DEventPacket handle or NULL on error.
 */
caerPoint2DEventPacket caerPoint2DEventPacketAllocate(int32_t eventCapacity, int16_t eventSource, int32_t tsOverflow);

/**
 * Get the Point2D event at the given index from the event packet.
 *
 * @param packet a valid Point2DEventPacket pointer. Cannot be NULL.
 * @param n the index of the returned event. Must be within [0,eventCapacity[ bounds.
 *
 * @return the requested Point2D event. NULL on error.
 */
static inline caerPoint2DEvent caerPoint2DEventPacketGetEvent(caerPoint2DEventPacket packet, int32_t n) {
	// Check that we're not out of bounds.
	if (n < 0 || n >= caerEventPacketHeaderGetEventCapacity(&packet->packetHeader)) {
		caerLog(CAER_LOG_CRITICAL, "Point2D Event",
			"Called caerPoint2DEventPacketGetEvent() with invalid event offset %" PRIi32 ", while maximum allowed value is %" PRIi32 ".",
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
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 *
 * @return this event's 32bit microsecond timestamp.
 */
static inline int32_t caerPoint2DEventGetTimestamp(caerPoint2DEvent event) {
	return (le32toh(event->timestamp));
}

/**
 * Get the 64bit event timestamp, in microseconds.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 * @param packet the Point2DEventPacket pointer for the packet containing this event. Cannot be NULL.
 *
 * @return this event's 64bit microsecond timestamp.
 */
static inline int64_t caerPoint2DEventGetTimestamp64(caerPoint2DEvent event, caerPoint2DEventPacket packet) {
	return (I64T(
		(U64T(caerEventPacketHeaderGetEventTSOverflow(&packet->packetHeader)) << TS_OVERFLOW_SHIFT) | U64T(caerPoint2DEventGetTimestamp(event))));
}

/**
 * Set the 32bit event timestamp, the value has to be in microseconds.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 * @param timestamp a positive 32bit microsecond timestamp.
 */
static inline void caerPoint2DEventSetTimestamp(caerPoint2DEvent event, int32_t timestamp) {
	if (timestamp < 0) {
		// Negative means using the 31st bit!
		caerLog(CAER_LOG_CRITICAL, "Point2D Event", "Called caerPoint2DEventSetTimestamp() with negative value!");
		return;
	}

	event->timestamp = htole32(timestamp);
}

/**
 * Check if this Point2D event is valid.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 *
 * @return true if valid, false if not.
 */
static inline bool caerPoint2DEventIsValid(caerPoint2DEvent event) {
	return (GET_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK));
}

/**
 * Validate the current event by setting its valid bit to true
 * and increasing the event packet's event count and valid
 * event count. Only works on events that are invalid.
 * DO NOT CALL THIS AFTER HAVING PREVIOUSLY ALREADY
 * INVALIDATED THIS EVENT, the total count will be incorrect.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 * @param packet the Point2DEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerPoint2DEventValidate(caerPoint2DEvent event, caerPoint2DEventPacket packet) {
	if (!caerPoint2DEventIsValid(event)) {
		SET_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK, 1);

		// Also increase number of events and valid events.
		// Only call this on (still) invalid events!
		caerEventPacketHeaderSetEventNumber(&packet->packetHeader,
			caerEventPacketHeaderGetEventNumber(&packet->packetHeader) + 1);
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) + 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Point2D Event", "Called caerPoint2DEventValidate() on already valid event.");
	}
}

/**
 * Invalidate the current event by setting its valid bit
 * to false and decreasing the number of valid events held
 * in the packet. Only works with events that are already
 * valid!
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 * @param packet the Point2DEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerPoint2DEventInvalidate(caerPoint2DEvent event, caerPoint2DEventPacket packet) {
	if (caerPoint2DEventIsValid(event)) {
		CLEAR_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK);

		// Also decrease number of valid events. Number of total events doesn't change.
		// Only call this on valid events!
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) - 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Point2D Event", "Called caerPoint2DEventInvalidate() on already invalid event.");
	}
}

/**
 * Get the measurement event type. This is useful to distinguish
 * between different measurements, for example distance or weight.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 *
 * @return the Point2D measurement type.
 */
static inline uint8_t caerPoint2DEventGetType(caerPoint2DEvent event) {
	return U8T(GET_NUMBITS32(event->info, POINT2D_TYPE_SHIFT, POINT2D_TYPE_MASK));
}

/**
 * Set the measurement event type. This is useful to distinguish
 * between different measurements, for example distance or weight.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 * @param type the Point2D measurement type.
 */
static inline void caerPoint2DEventSetType(caerPoint2DEvent event, uint8_t type) {
	CLEAR_NUMBITS32(event->info, POINT2D_TYPE_SHIFT, POINT2D_TYPE_MASK);
	SET_NUMBITS32(event->info, POINT2D_TYPE_SHIFT, POINT2D_TYPE_MASK, type);
}

/**
 * Get the measurement scale. This allows order of magnitude shifts
 * on the measured value to be applied automatically, such as having
 * measurements of type Distance (meters) and storing the values as
 * centimeters (10^-2) for higher precision, but keeping that information
 * around to allow easy changes of unit.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 *
 * @return the Point2D measurement scale.
 */
static inline int8_t caerPoint2DEventGetScale(caerPoint2DEvent event) {
	return I8T(GET_NUMBITS32(event->info, POINT2D_SCALE_SHIFT, POINT2D_SCALE_MASK));
}

/**
 * Set the measurement scale. This allows order of magnitude shifts
 * on the measured value to be applied automatically, such as having
 * measurements of type Distance (meters) and storing the values as
 * centimeters (10^-2) for higher precision, but keeping that information
 * around to allow easy changes of unit.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 * @param scale the Point2D measurement scale.
 */
static inline void caerPoint2DEventSetScale(caerPoint2DEvent event, int8_t scale) {
	CLEAR_NUMBITS32(event->info, POINT2D_SCALE_SHIFT, POINT2D_SCALE_MASK);
	SET_NUMBITS32(event->info, POINT2D_SCALE_SHIFT, POINT2D_SCALE_MASK, U8T(scale));
}

/**
 * Get the X axis measurement.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 *
 * @return X axis measurement.
 */
static inline float caerPoint2DEventGetX(caerPoint2DEvent event) {
	return (le32toh(event->x));
}

/**
 * Set the X axis measurement.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 * @param x X axis measurement.
 */
static inline void caerPoint2DEventSetX(caerPoint2DEvent event, float x) {
	event->x = htole32(x);
}

/**
 * Get the Y axis measurement.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 *
 * @return Y axis measurement.
 */
static inline float caerPoint2DEventGetY(caerPoint2DEvent event) {
	return (le32toh(event->y));
}

/**
 * Set the Y axis measurement.
 *
 * @param event a valid Point2DEvent pointer. Cannot be NULL.
 * @param y Y axis measurement.
 */
static inline void caerPoint2DEventSetY(caerPoint2DEvent event, float y) {
	event->y = htole32(y);
}

/**
 * Iterator over all Point2D events in a packet.
 * Returns the current index in the 'caerPoint2DIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerPoint2DIteratorElement' variable
 * of type caerPoint2DEvent.
 *
 * POINT2D_PACKET: a valid Point2DEventPacket pointer. Cannot be NULL.
 */
#define CAER_POINT2D_ITERATOR_ALL_START(POINT2D_PACKET) \
	for (int32_t caerPoint2DIteratorCounter = 0; \
		caerPoint2DIteratorCounter < caerEventPacketHeaderGetEventNumber(&(POINT2D_PACKET)->packetHeader); \
		caerPoint2DIteratorCounter++) { \
		caerPoint2DEvent caerPoint2DIteratorElement = caerPoint2DEventPacketGetEvent(POINT2D_PACKET, caerPoint2DIteratorCounter);

/**
 * Iterator close statement.
 */
#define CAER_POINT2D_ITERATOR_ALL_END }

/**
 * Iterator over only the valid Point2D events in a packet.
 * Returns the current index in the 'caerPoint2DIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerPoint2DIteratorElement' variable
 * of type caerPoint2DEvent.
 *
 * POINT2D_PACKET: a valid Point2DEventPacket pointer. Cannot be NULL.
 */
#define CAER_POINT2D_ITERATOR_VALID_START(POINT2D_PACKET) \
	for (int32_t caerPoint2DIteratorCounter = 0; \
		caerPoint2DIteratorCounter < caerEventPacketHeaderGetEventNumber(&(POINT2D_PACKET)->packetHeader); \
		caerPoint2DIteratorCounter++) { \
		caerPoint2DEvent caerPoint2DIteratorElement = caerPoint2DEventPacketGetEvent(POINT2D_PACKET, caerPoint2DIteratorCounter); \
		if (!caerPoint2DEventIsValid(caerPoint2DIteratorElement)) { continue; } // Skip invalid Point2D events.

/**
 * Iterator close statement.
 */
#define CAER_POINT2D_ITERATOR_VALID_END }

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_EVENTS_POINT2D_H_ */
