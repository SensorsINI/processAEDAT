/**
 * @file point3d.h
 *
 * THIS EVENT DEFINITIONS IS STILL TO BE CONSIDERED EXPERIMENTAL
 * AND IS SUBJECT TO FUTURE CHANGES AND REVISIONS!
 *
 * Point3D Events format definition and handling functions.
 * This contains three dimensional data points as floats,
 * together with support for distinguishing type and scale.
 */

#ifndef LIBCAER_EVENTS_POINT3D_H_
#define LIBCAER_EVENTS_POINT3D_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "common.h"

/**
 * Shift and mask values for type and scale information
 * associated with a Point3D event.
 * Up to 128 types are supported. The scale is given as orders
 * of magnitude, from 10^-128 to 10^127.
 * Bit 0 is the valid mark, see 'common.h' for more details.
 */
//@{
#define POINT3D_TYPE_SHIFT 1
#define POINT3D_TYPE_MASK 0x0000007F
#define POINT3D_SCALE_SHIFT 8
#define POINT3D_SCALE_MASK 0x000000FF
//@}

/**
 * Point3D event data structure definition.
 * This contains information about the measurement, such as a type
 * and a scale field, together with the usual validity mark.
 * The three measurements (x, y, z) are stored as floats.
 * Floats are in IEEE 754-2008 binary32 format.
 * Signed integers are used for fields that are to be interpreted
 * directly, for compatibility with languages that do not have
 * unsigned integer types, such as Java.
 */
struct caer_point3d_event {
	/// Event information. First because of valid mark.
	uint32_t info;
	/// Event timestamp.
	int32_t timestamp;
	/// X axis measurement.
	float x;
	/// Y axis measurement.
	float y;
	/// Z axis measurement.
	float z;
}__attribute__((__packed__));

/**
 * Type for pointer to Point3D event data structure.
 */
typedef struct caer_point3d_event *caerPoint3DEvent;

/**
 * Point3D event packet data structure definition.
 * EventPackets are always made up of the common packet header,
 * followed by 'eventCapacity' events. Everything has to
 * be in one contiguous memory block.
 */
struct caer_point3d_event_packet {
	/// The common event packet header.
	struct caer_event_packet_header packetHeader;
	/// The events array.
	struct caer_point3d_event events[];
}__attribute__((__packed__));

/**
 * Type for pointer to Point3D event packet data structure.
 */
typedef struct caer_point3d_event_packet *caerPoint3DEventPacket;

/**
 * Allocate a new Point3D events packet.
 * Use free() to reclaim this memory.
 *
 * @param eventCapacity the maximum number of events this packet will hold.
 * @param eventSource the unique ID representing the source/generator of this packet.
 * @param tsOverflow the current timestamp overflow counter value for this packet.
 *
 * @return a valid Point3DEventPacket handle or NULL on error.
 */
caerPoint3DEventPacket caerPoint3DEventPacketAllocate(int32_t eventCapacity, int16_t eventSource, int32_t tsOverflow);

/**
 * Get the Point3D event at the given index from the event packet.
 *
 * @param packet a valid Point3DEventPacket pointer. Cannot be NULL.
 * @param n the index of the returned event. Must be within [0,eventCapacity[ bounds.
 *
 * @return the requested Point3D event. NULL on error.
 */
static inline caerPoint3DEvent caerPoint3DEventPacketGetEvent(caerPoint3DEventPacket packet, int32_t n) {
	// Check that we're not out of bounds.
	if (n < 0 || n >= caerEventPacketHeaderGetEventCapacity(&packet->packetHeader)) {
		caerLog(CAER_LOG_CRITICAL, "Point3D Event",
			"Called caerPoint3DEventPacketGetEvent() with invalid event offset %" PRIi32 ", while maximum allowed value is %" PRIi32 ".",
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
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 *
 * @return this event's 32bit microsecond timestamp.
 */
static inline int32_t caerPoint3DEventGetTimestamp(caerPoint3DEvent event) {
	return (le32toh(event->timestamp));
}

/**
 * Get the 64bit event timestamp, in microseconds.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 * @param packet the Point3DEventPacket pointer for the packet containing this event. Cannot be NULL.
 *
 * @return this event's 64bit microsecond timestamp.
 */
static inline int64_t caerPoint3DEventGetTimestamp64(caerPoint3DEvent event, caerPoint3DEventPacket packet) {
	return (I64T(
		(U64T(caerEventPacketHeaderGetEventTSOverflow(&packet->packetHeader)) << TS_OVERFLOW_SHIFT) | U64T(caerPoint3DEventGetTimestamp(event))));
}

/**
 * Set the 32bit event timestamp, the value has to be in microseconds.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 * @param timestamp a positive 32bit microsecond timestamp.
 */
static inline void caerPoint3DEventSetTimestamp(caerPoint3DEvent event, int32_t timestamp) {
	if (timestamp < 0) {
		// Negative means using the 31st bit!
		caerLog(CAER_LOG_CRITICAL, "Point3D Event", "Called caerPoint3DEventSetTimestamp() with negative value!");
		return;
	}

	event->timestamp = htole32(timestamp);
}

/**
 * Check if this Point3D event is valid.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 *
 * @return true if valid, false if not.
 */
static inline bool caerPoint3DEventIsValid(caerPoint3DEvent event) {
	return (GET_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK));
}

/**
 * Validate the current event by setting its valid bit to true
 * and increasing the event packet's event count and valid
 * event count. Only works on events that are invalid.
 * DO NOT CALL THIS AFTER HAVING PREVIOUSLY ALREADY
 * INVALIDATED THIS EVENT, the total count will be incorrect.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 * @param packet the Point3DEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerPoint3DEventValidate(caerPoint3DEvent event, caerPoint3DEventPacket packet) {
	if (!caerPoint3DEventIsValid(event)) {
		SET_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK, 1);

		// Also increase number of events and valid events.
		// Only call this on (still) invalid events!
		caerEventPacketHeaderSetEventNumber(&packet->packetHeader,
			caerEventPacketHeaderGetEventNumber(&packet->packetHeader) + 1);
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) + 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Point3D Event", "Called caerPoint3DEventValidate() on already valid event.");
	}
}

/**
 * Invalidate the current event by setting its valid bit
 * to false and decreasing the number of valid events held
 * in the packet. Only works with events that are already
 * valid!
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 * @param packet the Point3DEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerPoint3DEventInvalidate(caerPoint3DEvent event, caerPoint3DEventPacket packet) {
	if (caerPoint3DEventIsValid(event)) {
		CLEAR_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK);

		// Also decrease number of valid events. Number of total events doesn't change.
		// Only call this on valid events!
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) - 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Point3D Event", "Called caerPoint3DEventInvalidate() on already invalid event.");
	}
}

/**
 * Get the measurement event type. This is useful to distinguish
 * between different measurements, for example distance or weight.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 *
 * @return the Point3D measurement type.
 */
static inline uint8_t caerPoint3DEventGetType(caerPoint3DEvent event) {
	return U8T(GET_NUMBITS32(event->info, POINT3D_TYPE_SHIFT, POINT3D_TYPE_MASK));
}

/**
 * Set the measurement event type. This is useful to distinguish
 * between different measurements, for example distance or weight.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 * @param type the Point3D measurement type.
 */
static inline void caerPoint3DEventSetType(caerPoint3DEvent event, uint8_t type) {
	CLEAR_NUMBITS32(event->info, POINT3D_TYPE_SHIFT, POINT3D_TYPE_MASK);
	SET_NUMBITS32(event->info, POINT3D_TYPE_SHIFT, POINT3D_TYPE_MASK, type);
}

/**
 * Get the measurement scale. This allows order of magnitude shifts
 * on the measured value to be applied automatically, such as having
 * measurements of type Distance (meters) and storing the values as
 * centimeters (10^-2) for higher precision, but keeping that information
 * around to allow easy changes of unit.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 *
 * @return the Point3D measurement scale.
 */
static inline int8_t caerPoint3DEventGetScale(caerPoint3DEvent event) {
	return I8T(GET_NUMBITS32(event->info, POINT3D_SCALE_SHIFT, POINT3D_SCALE_MASK));
}

/**
 * Set the measurement scale. This allows order of magnitude shifts
 * on the measured value to be applied automatically, such as having
 * measurements of type Distance (meters) and storing the values as
 * centimeters (10^-2) for higher precision, but keeping that information
 * around to allow easy changes of unit.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 * @param scale the Point3D measurement scale.
 */
static inline void caerPoint3DEventSetScale(caerPoint3DEvent event, int8_t scale) {
	CLEAR_NUMBITS32(event->info, POINT3D_SCALE_SHIFT, POINT3D_SCALE_MASK);
	SET_NUMBITS32(event->info, POINT3D_SCALE_SHIFT, POINT3D_SCALE_MASK, U8T(scale));
}

/**
 * Get the X axis measurement.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 *
 * @return X axis measurement.
 */
static inline float caerPoint3DEventGetX(caerPoint3DEvent event) {
	return (le32toh(event->x));
}

/**
 * Set the X axis measurement.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 * @param x X axis measurement.
 */
static inline void caerPoint3DEventSetX(caerPoint3DEvent event, float x) {
	event->x = htole32(x);
}

/**
 * Get the Y axis measurement.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 *
 * @return Y axis measurement.
 */
static inline float caerPoint3DEventGetY(caerPoint3DEvent event) {
	return (le32toh(event->y));
}

/**
 * Set the Y axis measurement.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 * @param y Y axis measurement.
 */
static inline void caerPoint3DEventSetY(caerPoint3DEvent event, float y) {
	event->y = htole32(y);
}

/**
 * Get the Z axis measurement.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 *
 * @return Z axis measurement.
 */
static inline float caerPoint3DEventGetZ(caerPoint3DEvent event) {
	return (le32toh(event->z));
}

/**
 * Set the Z axis measurement.
 *
 * @param event a valid Point3DEvent pointer. Cannot be NULL.
 * @param z Z axis measurement.
 */
static inline void caerPoint3DEventSetZ(caerPoint3DEvent event, float z) {
	event->z = htole32(z);
}

/**
 * Iterator over all Point3D events in a packet.
 * Returns the current index in the 'caerPoint3DIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerPoint3DIteratorElement' variable
 * of type caerPoint3DEvent.
 *
 * POINT3D_PACKET: a valid Point3DEventPacket pointer. Cannot be NULL.
 */
#define CAER_POINT3D_ITERATOR_ALL_START(POINT3D_PACKET) \
	for (int32_t caerPoint3DIteratorCounter = 0; \
		caerPoint3DIteratorCounter < caerEventPacketHeaderGetEventNumber(&(POINT3D_PACKET)->packetHeader); \
		caerPoint3DIteratorCounter++) { \
		caerPoint3DEvent caerPoint3DIteratorElement = caerPoint3DEventPacketGetEvent(POINT3D_PACKET, caerPoint3DIteratorCounter);

/**
 * Iterator close statement.
 */
#define CAER_POINT3D_ITERATOR_ALL_END }

/**
 * Iterator over only the valid Point3D events in a packet.
 * Returns the current index in the 'caerPoint3DIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerPoint3DIteratorElement' variable
 * of type caerPoint3DEvent.
 *
 * POINT3D_PACKET: a valid Point3DEventPacket pointer. Cannot be NULL.
 */
#define CAER_POINT3D_ITERATOR_VALID_START(POINT3D_PACKET) \
	for (int32_t caerPoint3DIteratorCounter = 0; \
		caerPoint3DIteratorCounter < caerEventPacketHeaderGetEventNumber(&(POINT3D_PACKET)->packetHeader); \
		caerPoint3DIteratorCounter++) { \
		caerPoint3DEvent caerPoint3DIteratorElement = caerPoint3DEventPacketGetEvent(POINT3D_PACKET, caerPoint3DIteratorCounter); \
		if (!caerPoint3DEventIsValid(caerPoint3DIteratorElement)) { continue; } // Skip invalid Point3D events.

/**
 * Iterator close statement.
 */
#define CAER_POINT3D_ITERATOR_VALID_END }

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_EVENTS_POINT3D_H_ */
