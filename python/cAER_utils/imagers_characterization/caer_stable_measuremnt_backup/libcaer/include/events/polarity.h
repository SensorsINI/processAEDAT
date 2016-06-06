/**
 * @file polarity.h
 *
 * Polarity Events format definition and handling functions.
 * This event contains change information, with an X/Y address
 * and an ON/OFF polarity, plus a possible color.
 * The (0, 0) address is in the upper left corner of the screen,
 * like in OpenCV/computer graphics.
 */

#ifndef LIBCAER_EVENTS_POLARITY_H_
#define LIBCAER_EVENTS_POLARITY_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "common.h"

/**
 * Shift and mask values for the polarity, color, X and Y addresses
 * of a polarity event.
 * Addresses up to 14 bit are supported. Polarity is ON(=1) or OFF(=0).
 * 2 bits are reserved for color information (R, G, B, W).
 * Bit 0 is the valid mark, see 'common.h' for more details.
 */
//@{
#define POLARITY_SHIFT 1
#define POLARITY_MASK 0x00000001
#define COLOR_SHIFT 2
#define COLOR_MASK 0x00000003
#define Y_ADDR_SHIFT 4
#define Y_ADDR_MASK 0x00003FFF
#define X_ADDR_SHIFT 18
#define X_ADDR_MASK 0x00003FFF
//@}

/**
 * List of all polarity event color identifiers.
 * Used to interpret the polarity event color field.
 */
enum caer_polarity_event_color {
	W = 0, //!< White/Mono. No color.
	R = 1, //!< Red.
	G = 2, //!< Green.
	B = 3, //!< Blue.
};

/**
 * Polarity event data structure definition.
 * This contains the actual X/Y addresses, the polarity, the
 * color as well as the 32 bit event timestamp.
 * The (0, 0) address is in the upper left corner of the screen,
 * like in OpenCV/computer graphics.
 * Signed integers are used for fields that are to be interpreted
 * directly, for compatibility with languages that do not have
 * unsigned integer types, such as Java.
 */
struct caer_polarity_event {
	/// Event data. First because of valid mark.
	uint32_t data;
	/// Event timestamp.
	int32_t timestamp;
}__attribute__((__packed__));

/**
 * Type for pointer to polarity event data structure.
 */
typedef struct caer_polarity_event *caerPolarityEvent;

/**
 * Polarity event packet data structure definition.
 * EventPackets are always made up of the common packet header,
 * followed by 'eventCapacity' events. Everything has to
 * be in one contiguous memory block.
 */
struct caer_polarity_event_packet {
	/// The common event packet header.
	struct caer_event_packet_header packetHeader;
	/// The events array.
	struct caer_polarity_event events[];
}__attribute__((__packed__));

/**
 * Type for pointer to polarity event packet data structure.
 */
typedef struct caer_polarity_event_packet *caerPolarityEventPacket;

/**
 * Allocate a new polarity events packet.
 * Use free() to reclaim this memory.
 *
 * @param eventCapacity the maximum number of events this packet will hold.
 * @param eventSource the unique ID representing the source/generator of this packet.
 * @param tsOverflow the current timestamp overflow counter value for this packet.
 *
 * @return a valid PolarityEventPacket handle or NULL on error.
 */
caerPolarityEventPacket caerPolarityEventPacketAllocate(int32_t eventCapacity, int16_t eventSource, int32_t tsOverflow);

/**
 * Get the polarity event at the given index from the event packet.
 *
 * @param packet a valid PolarityEventPacket pointer. Cannot be NULL.
 * @param n the index of the returned event. Must be within [0,eventCapacity[ bounds.
 *
 * @return the requested polarity event. NULL on error.
 */
static inline caerPolarityEvent caerPolarityEventPacketGetEvent(caerPolarityEventPacket packet, int32_t n) {
	// Check that we're not out of bounds.
	if (n < 0 || n >= caerEventPacketHeaderGetEventCapacity(&packet->packetHeader)) {
		caerLog(CAER_LOG_CRITICAL, "Polarity Event",
			"Called caerPolarityEventPacketGetEvent() with invalid event offset %" PRIi32 ", while maximum allowed value is %" PRIi32 ".",
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
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 *
 * @return this event's 32bit microsecond timestamp.
 */
static inline int32_t caerPolarityEventGetTimestamp(caerPolarityEvent event) {
	return (le32toh(event->timestamp));
}

/**
 * Get the 64bit event timestamp, in microseconds.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 * @param packet the PolarityEventPacket pointer for the packet containing this event. Cannot be NULL.
 *
 * @return this event's 64bit microsecond timestamp.
 */
static inline int64_t caerPolarityEventGetTimestamp64(caerPolarityEvent event, caerPolarityEventPacket packet) {
	return (I64T(
		(U64T(caerEventPacketHeaderGetEventTSOverflow(&packet->packetHeader)) << TS_OVERFLOW_SHIFT) | U64T(caerPolarityEventGetTimestamp(event))));
}

/**
 * Set the 32bit event timestamp, the value has to be in microseconds.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 * @param timestamp a positive 32bit microsecond timestamp.
 */
static inline void caerPolarityEventSetTimestamp(caerPolarityEvent event, int32_t timestamp) {
	if (timestamp < 0) {
		// Negative means using the 31st bit!
		caerLog(CAER_LOG_CRITICAL, "Polarity Event", "Called caerPolarityEventSetTimestamp() with negative value!");
		return;
	}

	event->timestamp = htole32(timestamp);
}

/**
 * Check if this polarity event is valid.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 *
 * @return true if valid, false if not.
 */
static inline bool caerPolarityEventIsValid(caerPolarityEvent event) {
	return (GET_NUMBITS32(event->data, VALID_MARK_SHIFT, VALID_MARK_MASK));
}

/**
 * Validate the current event by setting its valid bit to true
 * and increasing the event packet's event count and valid
 * event count. Only works on events that are invalid.
 * DO NOT CALL THIS AFTER HAVING PREVIOUSLY ALREADY
 * INVALIDATED THIS EVENT, the total count will be incorrect.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 * @param packet the PolarityEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerPolarityEventValidate(caerPolarityEvent event, caerPolarityEventPacket packet) {
	if (!caerPolarityEventIsValid(event)) {
		SET_NUMBITS32(event->data, VALID_MARK_SHIFT, VALID_MARK_MASK, 1);

		// Also increase number of events and valid events.
		// Only call this on (still) invalid events!
		caerEventPacketHeaderSetEventNumber(&packet->packetHeader,
			caerEventPacketHeaderGetEventNumber(&packet->packetHeader) + 1);
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) + 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Polarity Event", "Called caerPolarityEventValidate() on already valid event.");
	}
}

/**
 * Invalidate the current event by setting its valid bit
 * to false and decreasing the number of valid events held
 * in the packet. Only works with events that are already
 * valid!
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 * @param packet the PolarityEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerPolarityEventInvalidate(caerPolarityEvent event, caerPolarityEventPacket packet) {
	if (caerPolarityEventIsValid(event)) {
		CLEAR_NUMBITS32(event->data, VALID_MARK_SHIFT, VALID_MARK_MASK);

		// Also decrease number of valid events. Number of total events doesn't change.
		// Only call this on valid events!
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) - 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Polarity Event", "Called caerPolarityEventInvalidate() on already invalid event.");
	}
}

/**
 * Get the change event polarity. 1 is ON, 0 is OFF.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 *
 * @return event polarity value.
 */
static inline bool caerPolarityEventGetPolarity(caerPolarityEvent event) {
	return (GET_NUMBITS32(event->data, POLARITY_SHIFT, POLARITY_MASK));
}

/**
 * Set the change event polarity. 1 is ON, 0 is OFF.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 * @param polarity event polarity value.
 */
static inline void caerPolarityEventSetPolarity(caerPolarityEvent event, bool polarity) {
	CLEAR_NUMBITS32(event->data, POLARITY_SHIFT, POLARITY_MASK);
	SET_NUMBITS32(event->data, POLARITY_SHIFT, POLARITY_MASK, polarity);
}

/**
 * Get the identifier for the pixel's color.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 *
 * @return color identifier.
 */
static inline enum caer_polarity_event_color caerPolarityEventGetColor(caerPolarityEvent event) {
	return ((enum caer_polarity_event_color) U8T(GET_NUMBITS32(event->data, COLOR_SHIFT, COLOR_MASK)));
}

/**
 * Set the identifier for the pixel's color.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 * @param color color identifier.
 */
static inline void caerPolarityEventSetColor(caerPolarityEvent event, enum caer_polarity_event_color color) {
	CLEAR_NUMBITS32(event->data, COLOR_SHIFT, COLOR_MASK);
	SET_NUMBITS32(event->data, COLOR_SHIFT, COLOR_MASK, color);
}

/**
 * Get the Y (row) address for a change event, in pixels.
 * The (0, 0) address is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 *
 * @return the event Y address.
 */
static inline uint16_t caerPolarityEventGetY(caerPolarityEvent event) {
	return U16T(GET_NUMBITS32(event->data, Y_ADDR_SHIFT, Y_ADDR_MASK));
}

/**
 * Set the Y (row) address for a change event, in pixels.
 * The (0, 0) address is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 * @param yAddress the event Y address.
 */
static inline void caerPolarityEventSetY(caerPolarityEvent event, uint16_t yAddress) {
	CLEAR_NUMBITS32(event->data, Y_ADDR_SHIFT, Y_ADDR_MASK);
	SET_NUMBITS32(event->data, Y_ADDR_SHIFT, Y_ADDR_MASK, yAddress);
}

/**
 * Get the X (column) address for a change event, in pixels.
 * The (0, 0) address is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 *
 * @return the event X address.
 */
static inline uint16_t caerPolarityEventGetX(caerPolarityEvent event) {
	return U16T(GET_NUMBITS32(event->data, X_ADDR_SHIFT, X_ADDR_MASK));
}

/**
 * Set the X (column) address for a change event, in pixels.
 * The (0, 0) address is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid PolarityEvent pointer. Cannot be NULL.
 * @param xAddress the event X address.
 */
static inline void caerPolarityEventSetX(caerPolarityEvent event, uint16_t xAddress) {
	CLEAR_NUMBITS32(event->data, X_ADDR_SHIFT, X_ADDR_MASK);
	SET_NUMBITS32(event->data, X_ADDR_SHIFT, X_ADDR_MASK, xAddress);
}

/**
 * Iterator over all polarity events in a packet.
 * Returns the current index in the 'caerPolarityIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerPolarityIteratorElement' variable
 * of type caerPolarityEvent.
 *
 * POLARITY_PACKET: a valid PolarityEventPacket pointer. Cannot be NULL.
 */
#define CAER_POLARITY_ITERATOR_ALL_START(POLARITY_PACKET) \
	for (int32_t caerPolarityIteratorCounter = 0; \
		caerPolarityIteratorCounter < caerEventPacketHeaderGetEventNumber(&(POLARITY_PACKET)->packetHeader); \
		caerPolarityIteratorCounter++) { \
		caerPolarityEvent caerPolarityIteratorElement = caerPolarityEventPacketGetEvent(POLARITY_PACKET, caerPolarityIteratorCounter);

/**
 * Iterator close statement.
 */
#define CAER_POLARITY_ITERATOR_ALL_END }

/**
 * Iterator over only the valid polarity events in a packet.
 * Returns the current index in the 'caerPolarityIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerPolarityIteratorElement' variable
 * of type caerPolarityEvent.
 *
 * POLARITY_PACKET: a valid PolarityEventPacket pointer. Cannot be NULL.
 */
#define CAER_POLARITY_ITERATOR_VALID_START(POLARITY_PACKET) \
	for (int32_t caerPolarityIteratorCounter = 0; \
		caerPolarityIteratorCounter < caerEventPacketHeaderGetEventNumber(&(POLARITY_PACKET)->packetHeader); \
		caerPolarityIteratorCounter++) { \
		caerPolarityEvent caerPolarityIteratorElement = caerPolarityEventPacketGetEvent(POLARITY_PACKET, caerPolarityIteratorCounter); \
		if (!caerPolarityEventIsValid(caerPolarityIteratorElement)) { continue; } // Skip invalid polarity events.

/**
 * Iterator close statement.
 */
#define CAER_POLARITY_ITERATOR_VALID_END }

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_EVENTS_POLARITY_H_ */
