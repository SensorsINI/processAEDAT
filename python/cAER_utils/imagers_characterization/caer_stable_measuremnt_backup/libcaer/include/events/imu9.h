/**
 * @file imu9.h
 *
 * IMU9 (9 axes) Events format definition and handling functions.
 * This contains data coming from the Inertial Measurement Unit
 * chip, with the 3-axes accelerometer and 3-axes gyroscope.
 * Temperature is also included.
 * Further, 3-axes from the magnetometer are included, which
 * can be used to get a compass-like heading.
 */

#ifndef LIBCAER_EVENTS_IMU9_H_
#define LIBCAER_EVENTS_IMU9_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "common.h"

/**
 * IMU 9-axes event data structure definition.
 * This contains accelerometer and gyroscope headings, plus
 * temperature, and magnetometer readings.
 * The X, Y and Z axes are referred to the camera plane.
 * X increases to the right, Y going up and Z towards where
 * the lens is pointing. Rotation for the gyroscope is
 * counter-clockwise along the increasing axis, for all three axes.
 * Floats are in IEEE 754-2008 binary32 format.
 * Signed integers are used for fields that are to be interpreted
 * directly, for compatibility with languages that do not have
 * unsigned integer types, such as Java.
 */
struct caer_imu9_event {
	/// Event information. First because of valid mark.
	uint32_t info;
	/// Event timestamp.
	int32_t timestamp;
	/// Acceleration in the X axis, measured in g (9.81m/s²).
	float accel_x;
	/// Acceleration in the Y axis, measured in g (9.81m/s²).
	float accel_y;
	/// Acceleration in the Z axis, measured in g (9.81m/s²).
	float accel_z;
	/// Rotation in the X axis, measured in °/s.
	float gyro_x;
	/// Rotation in the Y axis, measured in °/s.
	float gyro_y;
	/// Rotation in the Z axis, measured in °/s.
	float gyro_z;
	/// Temperature, measured in °C.
	float temp;
	/// Magnetometer X axis, measured in µT (magnetic flux density).
	float comp_x;
	/// Magnetometer Y axis, measured in µT (magnetic flux density).
	float comp_y;
	/// Magnetometer Z axis, measured in µT (magnetic flux density).
	float comp_z;
}__attribute__((__packed__));

/**
 * Type for pointer to IMU 9-axes event data structure.
 */
typedef struct caer_imu9_event *caerIMU9Event;

/**
 * IMU 9-axes event packet data structure definition.
 * EventPackets are always made up of the common packet header,
 * followed by 'eventCapacity' events. Everything has to
 * be in one contiguous memory block.
 */
struct caer_imu9_event_packet {
	/// The common event packet header.
	struct caer_event_packet_header packetHeader;
	/// The events array.
	struct caer_imu9_event events[];
}__attribute__((__packed__));

/**
 * Type for pointer to IMU 9-axes event packet data structure.
 */
typedef struct caer_imu9_event_packet *caerIMU9EventPacket;

/**
 * Allocate a new IMU 9-axes events packet.
 * Use free() to reclaim this memory.
 *
 * @param eventCapacity the maximum number of events this packet will hold.
 * @param eventSource the unique ID representing the source/generator of this packet.
 * @param tsOverflow the current timestamp overflow counter value for this packet.
 *
 * @return a valid IMU9EventPacket handle or NULL on error.
 */
caerIMU9EventPacket caerIMU9EventPacketAllocate(int32_t eventCapacity, int16_t eventSource, int32_t tsOverflow);

/**
 * Get the IMU 9-axes event at the given index from the event packet.
 *
 * @param packet a valid IMU9EventPacket pointer. Cannot be NULL.
 * @param n the index of the returned event. Must be within [0,eventCapacity[ bounds.
 *
 * @return the requested IMU 9-axes event. NULL on error.
 */
static inline caerIMU9Event caerIMU9EventPacketGetEvent(caerIMU9EventPacket packet, int32_t n) {
	// Check that we're not out of bounds.
	if (n < 0 || n >= caerEventPacketHeaderGetEventCapacity(&packet->packetHeader)) {
		caerLog(CAER_LOG_CRITICAL, "IMU9 Event",
			"Called caerIMU9EventPacketGetEvent() with invalid event offset %" PRIi32 ", while maximum allowed value is %" PRIi32 ".",
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
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return this event's 32bit microsecond timestamp.
 */
static inline int32_t caerIMU9EventGetTimestamp(caerIMU9Event event) {
	return (le32toh(event->timestamp));
}

/**
 * Get the 64bit event timestamp, in microseconds.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param packet the IMU9EventPacket pointer for the packet containing this event. Cannot be NULL.
 *
 * @return this event's 64bit microsecond timestamp.
 */
static inline int64_t caerIMU9EventGetTimestamp64(caerIMU9Event event, caerIMU9EventPacket packet) {
	return (I64T(
		(U64T(caerEventPacketHeaderGetEventTSOverflow(&packet->packetHeader)) << TS_OVERFLOW_SHIFT) | U64T(caerIMU9EventGetTimestamp(event))));
}

/**
 * Set the 32bit event timestamp, the value has to be in microseconds.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param timestamp a positive 32bit microsecond timestamp.
 */
static inline void caerIMU9EventSetTimestamp(caerIMU9Event event, int32_t timestamp) {
	if (timestamp < 0) {
		// Negative means using the 31st bit!
		caerLog(CAER_LOG_CRITICAL, "IMU9 Event", "Called caerIMU9EventSetTimestamp() with negative value!");
		return;
	}

	event->timestamp = htole32(timestamp);
}

/**
 * Check if this IMU 9-axes event is valid.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return true if valid, false if not.
 */
static inline bool caerIMU9EventIsValid(caerIMU9Event event) {
	return (GET_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK));
}

/**
 * Validate the current event by setting its valid bit to true
 * and increasing the event packet's event count and valid
 * event count. Only works on events that are invalid.
 * DO NOT CALL THIS AFTER HAVING PREVIOUSLY ALREADY
 * INVALIDATED THIS EVENT, the total count will be incorrect.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param packet the IMU9EventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerIMU9EventValidate(caerIMU9Event event, caerIMU9EventPacket packet) {
	if (!caerIMU9EventIsValid(event)) {
		SET_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK, 1);

		// Also increase number of events and valid events.
		// Only call this on (still) invalid events!
		caerEventPacketHeaderSetEventNumber(&packet->packetHeader,
			caerEventPacketHeaderGetEventNumber(&packet->packetHeader) + 1);
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) + 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "IMU9 Event", "Called caerIMU9EventValidate() on already valid event.");
	}
}

/**
 * Invalidate the current event by setting its valid bit
 * to false and decreasing the number of valid events held
 * in the packet. Only works with events that are already
 * valid!
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param packet the IMU9EventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerIMU9EventInvalidate(caerIMU9Event event, caerIMU9EventPacket packet) {
	if (caerIMU9EventIsValid(event)) {
		CLEAR_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK);

		// Also decrease number of valid events. Number of total events doesn't change.
		// Only call this on valid events!
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) - 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "IMU9 Event", "Called caerIMU9EventInvalidate() on already invalid event.");
	}
}

/**
 * Get the X axis acceleration reading (from accelerometer).
 * This is in g (1 g = 9.81 m/s²).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return acceleration on the X axis.
 */
static inline float caerIMU9EventGetAccelX(caerIMU9Event event) {
	return (le32toh(event->accel_x));
}

/**
 * Set the X axis acceleration reading (from accelerometer).
 * This is in g (1 g = 9.81 m/s²).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param accelX acceleration on the X axis.
 */
static inline void caerIMU9EventSetAccelX(caerIMU9Event event, float accelX) {
	event->accel_x = htole32(accelX);
}

/**
 * Get the Y axis acceleration reading (from accelerometer).
 * This is in g (1 g = 9.81 m/s²).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return acceleration on the Y axis.
 */
static inline float caerIMU9EventGetAccelY(caerIMU9Event event) {
	return (le32toh(event->accel_y));
}

/**
 * Set the Y axis acceleration reading (from accelerometer).
 * This is in g (1 g = 9.81 m/s²).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param accelY acceleration on the Y axis.
 */
static inline void caerIMU9EventSetAccelY(caerIMU9Event event, float accelY) {
	event->accel_y = htole32(accelY);
}

/**
 * Get the Z axis acceleration reading (from accelerometer).
 * This is in g (1 g = 9.81 m/s²).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return acceleration on the Z axis.
 */
static inline float caerIMU9EventGetAccelZ(caerIMU9Event event) {
	return (le32toh(event->accel_z));
}

/**
 * Set the Z axis acceleration reading (from accelerometer).
 * This is in g (1 g = 9.81 m/s²).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param accelZ acceleration on the Z axis.
 */
static inline void caerIMU9EventSetAccelZ(caerIMU9Event event, float accelZ) {
	event->accel_z = htole32(accelZ);
}

/**
 * Get the X axis (roll) angular velocity reading (from gyroscope).
 * This is in °/s (deg/sec).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return angular velocity on the X axis (roll).
 */
static inline float caerIMU9EventGetGyroX(caerIMU9Event event) {
	return (le32toh(event->gyro_x));
}

/**
 * Set the X axis (roll) angular velocity reading (from gyroscope).
 * This is in °/s (deg/sec).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param gyroX angular velocity on the X axis (roll).
 */
static inline void caerIMU9EventSetGyroX(caerIMU9Event event, float gyroX) {
	event->gyro_x = htole32(gyroX);
}

/**
 * Get the Y axis (pitch) angular velocity reading (from gyroscope).
 * This is in °/s (deg/sec).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return angular velocity on the Y axis (pitch).
 */
static inline float caerIMU9EventGetGyroY(caerIMU9Event event) {
	return (le32toh(event->gyro_y));
}

/**
 * Set the Y axis (pitch) angular velocity reading (from gyroscope).
 * This is in °/s (deg/sec).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param gyroY angular velocity on the Y axis (pitch).
 */
static inline void caerIMU9EventSetGyroY(caerIMU9Event event, float gyroY) {
	event->gyro_y = htole32(gyroY);
}

/**
 * Get the Z axis (yaw) angular velocity reading (from gyroscope).
 * This is in °/s (deg/sec).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return angular velocity on the Z axis (yaw).
 */
static inline float caerIMU9EventGetGyroZ(caerIMU9Event event) {
	return (le32toh(event->gyro_z));
}

/**
 * Set the Z axis (yaw) angular velocity reading (from gyroscope).
 * This is in °/s (deg/sec).
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param gyroZ angular velocity on the Z axis (yaw).
 */
static inline void caerIMU9EventSetGyroZ(caerIMU9Event event, float gyroZ) {
	event->gyro_z = htole32(gyroZ);
}

/**
 * Get the temperature reading.
 * This is in °C.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return temperature in °C.
 */
static inline float caerIMU9EventGetTemp(caerIMU9Event event) {
	return (le32toh(event->temp));
}

/**
 * Set the temperature reading.
 * This is in °C.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param temp temperature in °C.
 */
static inline void caerIMU9EventSetTemp(caerIMU9Event event, float temp) {
	event->temp = htole32(temp);
}

/**
 * Get the X axis compass heading (from magnetometer).
 * This is in µT.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return X axis compass heading.
 */
static inline float caerIMU9EventGetCompX(caerIMU9Event event) {
	return (le32toh(event->comp_x));
}

/**
 * Set the X axis compass heading (from magnetometer).
 * This is in µT.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param compX X axis compass heading.
 */
static inline void caerIMU9EventSetCompX(caerIMU9Event event, float compX) {
	event->comp_x = htole32(compX);
}

/**
 * Get the Y axis compass heading (from magnetometer).
 * This is in µT.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return Y axis compass heading.
 */
static inline float caerIMU9EventGetCompY(caerIMU9Event event) {
	return (le32toh(event->comp_y));
}

/**
 * Set the Y axis compass heading (from magnetometer).
 * This is in µT.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param compY Y axis compass heading.
 */
static inline void caerIMU9EventSetCompY(caerIMU9Event event, float compY) {
	event->comp_y = htole32(compY);
}

/**
 * Get the Z axis compass heading (from magnetometer).
 * This is in µT.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 *
 * @return Z axis compass heading.
 */
static inline float caerIMU9EventGetCompZ(caerIMU9Event event) {
	return (le32toh(event->comp_z));
}

/**
 * Set the Z axis compass heading (from magnetometer).
 * This is in µT.
 *
 * @param event a valid IMU9Event pointer. Cannot be NULL.
 * @param compZ Z axis compass heading.
 */
static inline void caerIMU9EventSetCompZ(caerIMU9Event event, float compZ) {
	event->comp_z = htole32(compZ);
}

/**
 * Iterator over all IMU9 events in a packet.
 * Returns the current index in the 'caerIMU9IteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerIMU9IteratorElement' variable
 * of type caerIMU9Event.
 *
 * IMU9_PACKET: a valid IMU9EventPacket pointer. Cannot be NULL.
 */
#define CAER_IMU9_ITERATOR_ALL_START(IMU9_PACKET) \
	for (int32_t caerIMU9IteratorCounter = 0; \
		caerIMU9IteratorCounter < caerEventPacketHeaderGetEventNumber(&(IMU9_PACKET)->packetHeader); \
		caerIMU9IteratorCounter++) { \
		caerIMU9Event caerIMU9IteratorElement = caerIMU9EventPacketGetEvent(IMU9_PACKET, caerIMU9IteratorCounter);

/**
 * Iterator close statement.
 */
#define CAER_IMU9_ITERATOR_ALL_END }

/**
 * Iterator over only the valid IMU9 events in a packet.
 * Returns the current index in the 'caerIMU9IteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerIMU9IteratorElement' variable
 * of type caerIMU9Event.
 *
 * IMU9_PACKET: a valid IMU9EventPacket pointer. Cannot be NULL.
 */
#define CAER_IMU9_ITERATOR_VALID_START(IMU9_PACKET) \
	for (int32_t caerIMU9IteratorCounter = 0; \
		caerIMU9IteratorCounter < caerEventPacketHeaderGetEventNumber(&(IMU9_PACKET)->packetHeader); \
		caerIMU9IteratorCounter++) { \
		caerIMU9Event caerIMU9IteratorElement = caerIMU9EventPacketGetEvent(IMU9_PACKET, caerIMU9IteratorCounter); \
		if (!caerIMU9EventIsValid(caerIMU9IteratorElement)) { continue; } // Skip invalid IMU9 events.

/**
 * Iterator close statement.
 */
#define CAER_IMU9_ITERATOR_VALID_END }

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_EVENTS_IMU9_H_ */
