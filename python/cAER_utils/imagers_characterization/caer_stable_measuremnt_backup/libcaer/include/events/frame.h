/**
 * @file frame.h
 *
 * Frame Events format definition and handling functions.
 * This event type encodes intensity frames, like you would
 * get from a normal APS camera. It supports multiple channels
 * for color, color filter information, as well as multiple
 * Regions of Interest (ROI).
 * The (0, 0) pixel is in the upper left corner of the screen,
 * like in OpenCV/computer graphics. The pixel array is laid out row by row
 * (increasing X axis), going from top to bottom (increasing Y axis).
 */

#ifndef LIBCAER_EVENTS_FRAME_H_
#define LIBCAER_EVENTS_FRAME_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "common.h"

/**
 * Shift and mask values for the color channels number, the color
 * filter arrangement and the ROI identifier contained in the
 * 'info' field of the frame event.
 * Multiple channels (RGB for example) are possible, see the
 * 'enum caer_frame_event_color_channels'. To understand the original
 * color filter arrangement to interpolate color images, see
 * the 'enum caer_frame_event_color_filter'.
 * Also, up to 128 different Regions of Interest (ROI) can be tracked.
 * Bit 0 is the valid mark, see 'common.h' for more details.
 */
//@{
#define COLOR_CHANNELS_SHIFT 1
#define COLOR_CHANNELS_MASK 0x00000007
#define COLOR_FILTER_SHIFT 4
#define COLOR_FILTER_MASK 0x00000007
#define ROI_IDENTIFIER_SHIFT 7
#define ROI_IDENTIFIER_MASK 0x0000007F
//@}

/**
 * List of all frame event color channel identifiers.
 * Used to interpret the frame event color channel field.
 */
enum caer_frame_event_color_channels {
	GRAYSCALE = 1, //!< Grayscale, one channel only.
	RGB = 3,       //!< Red Green Blue, 3 color channels.
	RGBA = 4,      //!< Red Green Blue Alpha, 3 color channels plus transparency.
};

/**
 * List of all frame event color filter identifiers.
 * Used to interpret the frame event color filter field.
 */
enum caer_frame_event_color_filter {
	MONO = 0,    //!< No color filter present, all light passes.
	RGBG = 1,    //!< Standard Bayer color filter, 1 red 2 green 1 blue. Variation 1.
	GRGB = 2,    //!< Standard Bayer color filter, 1 red 2 green 1 blue. Variation 2.
	GBGR = 3,    //!< Standard Bayer color filter, 1 red 2 green 1 blue. Variation 3.
	BGRG = 4,    //!< Standard Bayer color filter, 1 red 2 green 1 blue. Variation 4.
	RGBW = 5,    //!< Modified Bayer color filter, with white (pass all light) instead of extra green. Variation 1.
	GRWB = 6,    //!< Modified Bayer color filter, with white (pass all light) instead of extra green. Variation 2.
	WBGR = 7,    //!< Modified Bayer color filter, with white (pass all light) instead of extra green. Variation 3.
	BWRG = 8,    //!< Modified Bayer color filter, with white (pass all light) instead of extra green. Variation 4.
};

/**
 * Frame event data structure definition.
 * This contains the actual information on the frame (ROI, color channels,
 * color filter), several timestamps to signal start and end of capture and
 * of exposure, as well as the actual pixels, in a 16 bit normalized format.
 * The (0, 0) address is in the upper left corner, like in OpenCV/computer graphics.
 * The pixel array is laid out row by row (increasing X axis), going from
 * top to bottom (increasing Y axis).
 * Signed integers are used for fields that are to be interpreted
 * directly, for compatibility with languages that do not have
 * unsigned integer types, such as Java.
 */
struct caer_frame_event {
	/// Event information (ROI region, color channels, color filter). First because of valid mark.
	uint32_t info;
	/// Start of Frame (SOF) timestamp.
	int32_t ts_startframe;
	/// End of Frame (EOF) timestamp.
	int32_t ts_endframe;
	/// Start of Exposure (SOE) timestamp.
	int32_t ts_startexposure;
	/// End of Exposure (EOE) timestamp.
	int32_t ts_endexposure;
	/// X axis length in pixels.
	int32_t lengthX;
	/// Y axis length in pixels.
	int32_t lengthY;
	/// X axis position (upper left offset) in pixels.
	int32_t positionX;
	/// Y axis position (upper left offset) in pixels.
	int32_t positionY;
	/// Pixel array, 16 bit unsigned integers, normalized to 16 bit depth.
	/// The pixel array is laid out row by row (increasing X axis), going
	/// from top to bottom (increasing Y axis).
	uint16_t pixels[];
}__attribute__((__packed__));

/**
 * Type for pointer to frame event data structure.
 */
typedef struct caer_frame_event *caerFrameEvent;

/**
 * Frame event packet data structure definition.
 * EventPackets are always made up of the common packet header,
 * followed by 'eventCapacity' events. Everything has to
 * be in one contiguous memory block. Direct access to the events
 * array is not possible for Frame events. To calculate position
 * offsets, use the 'eventSize' field in the packet header.
 */
struct caer_frame_event_packet {
	/// The common event packet header.
	struct caer_event_packet_header packetHeader;
/// All events follow here. Direct access to the events
/// array is not possible. To calculate position, use the
/// 'eventSize' field in the packetHeader.
}__attribute__((__packed__));

/**
 * Type for pointer to frame event packet data structure.
 */
typedef struct caer_frame_event_packet *caerFrameEventPacket;

/**
 * Allocate a new frame events packet.
 * Use free() to reclaim this memory.
 * The frame events allocate memory for a maximum sized pixels array, depending
 * on the parameters passed to this function, so that every event occupies the
 * same amount of memory (constant size). The actual frames inside of it
 * might be smaller than that, for example when using ROI, and their actual size
 * is stored inside the frame event and should always be queried from there.
 * The unused part of a pixels array is guaranteed to be zeros.
 *
 * @param eventCapacity the maximum number of events this packet will hold.
 * @param eventSource the unique ID representing the source/generator of this packet.
 * @param tsOverflow the current timestamp overflow counter value for this packet.
 * @param maxLengthX the maximum expected X axis size for frames in this packet.
 * @param maxLengthY the maximum expected Y axis size for frames in this packet.
 * @param maxChannelNumber the maximum expected number of channels for frames in this packet.
 *
 * @return a valid FrameEventPacket handle or NULL on error.
 */
caerFrameEventPacket caerFrameEventPacketAllocate(int32_t eventCapacity, int16_t eventSource, int32_t tsOverflow,
	int32_t maxLengthX, int32_t maxLengthY, int16_t maxChannelNumber);

/**
 * Get the frame event at the given index from the event packet.
 *
 * @param packet a valid FrameEventPacket pointer. Cannot be NULL.
 * @param n the index of the returned event. Must be within [0,eventCapacity[ bounds.
 *
 * @return the requested frame event. NULL on error.
 */
static inline caerFrameEvent caerFrameEventPacketGetEvent(caerFrameEventPacket packet, int32_t n) {
	// Check that we're not out of bounds.
	if (n < 0 || n >= caerEventPacketHeaderGetEventCapacity(&packet->packetHeader)) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventPacketGetEvent() with invalid event offset %" PRIi32 ", while maximum allowed value is %" PRIi32 ".",
			n, caerEventPacketHeaderGetEventCapacity(&packet->packetHeader) - 1);
		return (NULL);
	}

	// Return a pointer to the specified event.
	return ((caerFrameEvent) (((uint8_t *) &packet->packetHeader)
		+ (CAER_EVENT_PACKET_HEADER_SIZE + U64T(n * caerEventPacketHeaderGetEventSize(&packet->packetHeader)))));
}

/**
 * Get the 32bit start of frame capture timestamp, in microseconds.
 * Be aware that this wraps around! You can either ignore this fact,
 * or handle the special 'TIMESTAMP_WRAP' event that is generated when
 * this happens, or use the 64bit timestamp which never wraps around.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return this event's 32bit microsecond start of frame timestamp.
 */
static inline int32_t caerFrameEventGetTSStartOfFrame(caerFrameEvent event) {
	return (le32toh(event->ts_startframe));
}

/**
 * Get the 64bit start of frame capture timestamp, in microseconds.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param packet the FrameEventPacket pointer for the packet containing this event. Cannot be NULL.
 *
 * @return this event's 64bit microsecond start of frame timestamp.
 */
static inline int64_t caerFrameEventGetTSStartOfFrame64(caerFrameEvent event, caerFrameEventPacket packet) {
	// Even if frames have multiple time-stamps, it's not possible for later time-stamps to
	// be in a different TSOverflow period, since in those rare cases the event is dropped.
	return (I64T(
		(U64T(caerEventPacketHeaderGetEventTSOverflow(&packet->packetHeader)) << TS_OVERFLOW_SHIFT) | U64T(caerFrameEventGetTSStartOfFrame(event))));
}

/**
 * Set the 32bit start of frame capture timestamp, the value has to be in microseconds.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param startFrame a positive 32bit microsecond timestamp.
 */
static inline void caerFrameEventSetTSStartOfFrame(caerFrameEvent event, int32_t startFrame) {
	if (startFrame < 0) {
		// Negative means using the 31st bit!
		caerLog(CAER_LOG_CRITICAL, "Frame Event", "Called caerFrameEventSetTSStartOfFrame() with negative value!");
		return;
	}

	event->ts_startframe = htole32(startFrame);
}

/**
 * Get the 32bit end of frame capture timestamp, in microseconds.
 * Be aware that this wraps around! You can either ignore this fact,
 * or handle the special 'TIMESTAMP_WRAP' event that is generated when
 * this happens, or use the 64bit timestamp which never wraps around.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return this event's 32bit microsecond end of frame timestamp.
 */
static inline int32_t caerFrameEventGetTSEndOfFrame(caerFrameEvent event) {
	return (le32toh(event->ts_endframe));
}

/**
 * Get the 64bit end of frame capture timestamp, in microseconds.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param packet the FrameEventPacket pointer for the packet containing this event. Cannot be NULL.
 *
 * @return this event's 64bit microsecond end of frame timestamp.
 */
static inline int64_t caerFrameEventGetTSEndOfFrame64(caerFrameEvent event, caerFrameEventPacket packet) {
	// Even if frames have multiple time-stamps, it's not possible for later time-stamps to
	// be in a different TSOverflow period, since in those rare cases the event is dropped.
	return (I64T(
		(U64T(caerEventPacketHeaderGetEventTSOverflow(&packet->packetHeader)) << TS_OVERFLOW_SHIFT) | U64T(caerFrameEventGetTSEndOfFrame(event))));
}

/**
 * Set the 32bit end of frame capture timestamp, the value has to be in microseconds.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param endFrame a positive 32bit microsecond timestamp.
 */
static inline void caerFrameEventSetTSEndOfFrame(caerFrameEvent event, int32_t endFrame) {
	if (endFrame < 0) {
		// Negative means using the 31st bit!
		caerLog(CAER_LOG_CRITICAL, "Frame Event", "Called caerFrameEventSetTSEndOfFrame() with negative value!");
		return;
	}

	event->ts_endframe = htole32(endFrame);
}

/**
 * Get the 32bit start of exposure timestamp, in microseconds.
 * Be aware that this wraps around! You can either ignore this fact,
 * or handle the special 'TIMESTAMP_WRAP' event that is generated when
 * this happens, or use the 64bit timestamp which never wraps around.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return this event's 32bit microsecond start of exposure timestamp.
 */
static inline int32_t caerFrameEventGetTSStartOfExposure(caerFrameEvent event) {
	return (le32toh(event->ts_startexposure));
}

/**
 * Get the 64bit start of exposure timestamp, in microseconds.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param packet the FrameEventPacket pointer for the packet containing this event. Cannot be NULL.
 *
 * @return this event's 64bit microsecond start of exposure timestamp.
 */
static inline int64_t caerFrameEventGetTSStartOfExposure64(caerFrameEvent event, caerFrameEventPacket packet) {
	// Even if frames have multiple time-stamps, it's not possible for later time-stamps to
	// be in a different TSOverflow period, since in those rare cases the event is dropped.
	return (I64T(
		(U64T(caerEventPacketHeaderGetEventTSOverflow(&packet->packetHeader)) << TS_OVERFLOW_SHIFT) | U64T(caerFrameEventGetTSStartOfExposure(event))));
}

/**
 * Set the 32bit start of exposure timestamp, the value has to be in microseconds.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param startExposure a positive 32bit microsecond timestamp.
 */
static inline void caerFrameEventSetTSStartOfExposure(caerFrameEvent event, int32_t startExposure) {
	if (startExposure < 0) {
		// Negative means using the 31st bit!
		caerLog(CAER_LOG_CRITICAL, "Frame Event", "Called caerFrameEventSetTSStartOfExposure() with negative value!");
		return;
	}

	event->ts_startexposure = htole32(startExposure);
}

/**
 * Get the 32bit end of exposure timestamp, in microseconds.
 * Be aware that this wraps around! You can either ignore this fact,
 * or handle the special 'TIMESTAMP_WRAP' event that is generated when
 * this happens, or use the 64bit timestamp which never wraps around.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return this event's 32bit microsecond end of exposure timestamp.
 */
static inline int32_t caerFrameEventGetTSEndOfExposure(caerFrameEvent event) {
	return (le32toh(event->ts_endexposure));
}

/**
 * Get the 64bit end of exposure timestamp, in microseconds.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param packet the FrameEventPacket pointer for the packet containing this event. Cannot be NULL.
 *
 * @return this event's 64bit microsecond end of exposure timestamp.
 */
static inline int64_t caerFrameEventGetTSEndOfExposure64(caerFrameEvent event, caerFrameEventPacket packet) {
	// Even if frames have multiple time-stamps, it's not possible for later time-stamps to
	// be in a different TSOverflow period, since in those rare cases the event is dropped.
	return (I64T(
		(U64T(caerEventPacketHeaderGetEventTSOverflow(&packet->packetHeader)) << TS_OVERFLOW_SHIFT) | U64T(caerFrameEventGetTSEndOfExposure(event))));
}

/**
 * Set the 32bit end of exposure timestamp, the value has to be in microseconds.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param endExposure a positive 32bit microsecond timestamp.
 */
static inline void caerFrameEventSetTSEndOfExposure(caerFrameEvent event, int32_t endExposure) {
	if (endExposure < 0) {
		// Negative means using the 31st bit!
		caerLog(CAER_LOG_CRITICAL, "Frame Event", "Called caerFrameEventSetTSEndOfExposure() with negative value!");
		return;
	}

	event->ts_endexposure = htole32(endExposure);
}

/**
 * The total length, in microseconds, of the frame exposure time.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return the exposure time in microseconds.
 */
static inline int32_t caerFrameEventGetExposureLength(caerFrameEvent event) {
	return (caerFrameEventGetTSEndOfExposure(event) - caerFrameEventGetTSStartOfExposure(event));
}

/**
 * Get the 32bit event timestamp, in microseconds.
 * This is a median of the exposure timestamps.
 * Be aware that this wraps around! You can either ignore this fact,
 * or handle the special 'TIMESTAMP_WRAP' event that is generated when
 * this happens, or use the 64bit timestamp which never wraps around.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return this event's 32bit microsecond timestamp.
 */
static inline int32_t caerFrameEventGetTimestamp(caerFrameEvent event) {
	return (caerFrameEventGetTSStartOfExposure(event) + (caerFrameEventGetExposureLength(event) / 2));
}

/**
 * Get the 64bit event timestamp, in microseconds.
 * This is a median of the exposure timestamps.
 * See 'caerEventPacketHeaderGetEventTSOverflow()' documentation
 * for more details on the 64bit timestamp.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param packet the FrameEventPacket pointer for the packet containing this event. Cannot be NULL.
 *
 * @return this event's 64bit microsecond timestamp.
 */
static inline int64_t caerFrameEventGetTimestamp64(caerFrameEvent event, caerFrameEventPacket packet) {
	// Even if frames have multiple time-stamps, it's not possible for later time-stamps to
	// be in a different TSOverflow period, since in those rare cases the event is dropped.
	return (caerFrameEventGetTSStartOfExposure64(event, packet) + (caerFrameEventGetExposureLength(event) / 2));
}

/**
 * Check if this frame event is valid.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return true if valid, false if not.
 */
static inline bool caerFrameEventIsValid(caerFrameEvent event) {
	return (GET_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK));
}

/**
 * Validate the current event by setting its valid bit to true
 * and increasing the event packet's event count and valid
 * event count. Only works on events that are invalid.
 * DO NOT CALL THIS AFTER HAVING PREVIOUSLY ALREADY
 * INVALIDATED THIS EVENT, the total count will be incorrect.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param packet the FrameEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerFrameEventValidate(caerFrameEvent event, caerFrameEventPacket packet) {
	if (!caerFrameEventIsValid(event)) {
		SET_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK, 1);

		// Also increase number of events and valid events.
		// Only call this on (still) invalid events!
		caerEventPacketHeaderSetEventNumber(&packet->packetHeader,
			caerEventPacketHeaderGetEventNumber(&packet->packetHeader) + 1);
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) + 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Frame Event", "Called caerFrameEventValidate() on already valid event.");
	}
}

/**
 * Invalidate the current event by setting its valid bit
 * to false and decreasing the number of valid events held
 * in the packet. Only works with events that are already
 * valid!
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param packet the FrameEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerFrameEventInvalidate(caerFrameEvent event, caerFrameEventPacket packet) {
	if (caerFrameEventIsValid(event)) {
		CLEAR_NUMBITS32(event->info, VALID_MARK_SHIFT, VALID_MARK_MASK);

		// Also decrease number of valid events. Number of total events doesn't change.
		// Only call this on valid events!
		caerEventPacketHeaderSetEventValid(&packet->packetHeader,
			caerEventPacketHeaderGetEventValid(&packet->packetHeader) - 1);
	}
	else {
		caerLog(CAER_LOG_CRITICAL, "Frame Event", "Called caerFrameEventInvalidate() on already invalid event.");
	}
}

/**
 * Get the maximum size of the pixels array in bytes, based upon how
 * much memory was allocated to it by 'caerFrameEventPacketAllocate()'.
 *
 * @param packet a valid FrameEventPacket pointer. Cannot be NULL.
 *
 * @return maximum pixels array size in bytes.
 */
static inline size_t caerFrameEventPacketGetPixelsSize(caerFrameEventPacket packet) {
	return ((size_t) caerEventPacketHeaderGetEventSize(&packet->packetHeader) - sizeof(struct caer_frame_event));
}

/**
 * Get the maximum index into the pixels array, based upon how
 * much memory was allocated to it by 'caerFrameEventPacketAllocate()'.
 *
 * @param packet a valid FrameEventPacket pointer. Cannot be NULL.
 *
 * @return maximum pixels array index.
 */
static inline size_t caerFrameEventPacketGetPixelsMaxIndex(caerFrameEventPacket packet) {
	return (caerFrameEventPacketGetPixelsSize(packet) / sizeof(uint16_t));
}

/**
 * Get the numerical identifier for the Region of Interest
 * (ROI) region, to distinguish between multiple of them.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return numerical ROI identifier.
 */
static inline uint8_t caerFrameEventGetROIIdentifier(caerFrameEvent event) {
	return U8T(GET_NUMBITS32(event->info, ROI_IDENTIFIER_SHIFT, ROI_IDENTIFIER_MASK));
}

/**
 * Set the numerical identifier for the Region of Interest
 * (ROI) region, to distinguish between multiple of them.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param roiIdentifier numerical ROI identifier.
 */
static inline void caerFrameEventSetROIIdentifier(caerFrameEvent event, uint8_t roiIdentifier) {
	CLEAR_NUMBITS32(event->info, ROI_IDENTIFIER_SHIFT, ROI_IDENTIFIER_MASK);
	SET_NUMBITS32(event->info, ROI_IDENTIFIER_SHIFT, ROI_IDENTIFIER_MASK, roiIdentifier);
}

/**
 * Get the identifier for the color filter used by the sensor.
 * Useful for interpolating color images.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return color filter identifier.
 */
static inline enum caer_frame_event_color_filter caerFrameEventGetColorFilter(caerFrameEvent event) {
	return ((enum caer_frame_event_color_filter) U8T(GET_NUMBITS32(event->info, COLOR_FILTER_SHIFT, COLOR_FILTER_MASK)));
}

/**
 * Set the identifier for the color filter used by the sensor.
 * Useful for interpolating color images.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param colorFilter color filter identifier.
 */
static inline void caerFrameEventSetColorFilter(caerFrameEvent event, enum caer_frame_event_color_filter colorFilter) {
	CLEAR_NUMBITS32(event->info, COLOR_FILTER_SHIFT, COLOR_FILTER_MASK);
	SET_NUMBITS32(event->info, COLOR_FILTER_SHIFT, COLOR_FILTER_MASK, colorFilter);
}

/**
 * Get the actual X axis length for the current frame.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return frame X axis length.
 */
static inline int32_t caerFrameEventGetLengthX(caerFrameEvent event) {
	return (le32toh(event->lengthX));
}

/**
 * Get the actual Y axis length for the current frame.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return frame Y axis length.
 */
static inline int32_t caerFrameEventGetLengthY(caerFrameEvent event) {
	return (le32toh(event->lengthY));
}

/**
 * Get the actual color channels number for the current frame.
 * This can be used to store RGB frames for example.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return frame color channels number.
 */
static inline enum caer_frame_event_color_channels caerFrameEventGetChannelNumber(caerFrameEvent event) {
	return ((enum caer_frame_event_color_channels) U8T(
		GET_NUMBITS32(event->info, COLOR_CHANNELS_SHIFT, COLOR_CHANNELS_MASK)));
}

/**
 * Set the X and Y axes length and the color channels number for a frame,
 * while taking into account the maximum amount of memory available
 * for the pixel array, as allocated in 'caerFrameEventPacketAllocate()'.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param lengthX the frame's X axis length.
 * @param lengthY the frame's Y axis length.
 * @param channelNumber the number of color channels for this frame.
 * @param packet the FrameEventPacket pointer for the packet containing this event. Cannot be NULL.
 */
static inline void caerFrameEventSetLengthXLengthYChannelNumber(caerFrameEvent event, int32_t lengthX, int32_t lengthY,
	enum caer_frame_event_color_channels channelNumber, caerFrameEventPacket packet) {
	// Verify lengths and color channels number don't exceed allocated space.
	size_t neededMemory = (sizeof(uint16_t) * (size_t) lengthX * (size_t) lengthY * channelNumber);

	if (neededMemory > caerFrameEventPacketGetPixelsSize(packet)) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventSetLengthXLengthYChannelNumber() with values that result in requiring %zu bytes, which exceeds the maximum allocated event size of %zu bytes.",
			neededMemory, (size_t) caerEventPacketHeaderGetEventSize(&packet->packetHeader));
		return;
	}

	event->lengthX = htole32(lengthX);
	event->lengthY = htole32(lengthY);
	CLEAR_NUMBITS32(event->info, COLOR_CHANNELS_SHIFT, COLOR_CHANNELS_MASK);
	SET_NUMBITS32(event->info, COLOR_CHANNELS_SHIFT, COLOR_CHANNELS_MASK, channelNumber);
}

/**
 * Get the maximum valid index into the pixel array, at which
 * you can still get valid pixels.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return maximum valid pixels array index.
 */
static inline size_t caerFrameEventGetPixelsMaxIndex(caerFrameEvent event) {
	enum caer_frame_event_color_channels channels = caerFrameEventGetChannelNumber(event);
	return ((size_t) (caerFrameEventGetLengthX(event) * caerFrameEventGetLengthY(event) * I32T(channels)));
}

/**
 * Get the maximum size of the pixels array in bytes, in which
 * you can still get valid pixels.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return maximum valid pixels array size in bytes.
 */
static inline size_t caerFrameEventGetPixelsSize(caerFrameEvent event) {
	return (caerFrameEventGetPixelsMaxIndex(event) * sizeof(uint16_t));
}

/**
 * Get the X axis position offset.
 * This is used to place partial frames, like the ones gotten from
 * ROI readouts, in the visual space.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return X axis position offset.
 */
static inline int32_t caerFrameEventGetPositionX(caerFrameEvent event) {
	return (le32toh(event->positionX));
}

/**
 * Set the X axis position offset.
 * This is used to place partial frames, like the ones gotten from
 * ROI readouts, in the visual space.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param positionX X axis position offset.
 */
static inline void caerFrameEventSetPositionX(caerFrameEvent event, int32_t positionX) {
	event->positionX = htole32(positionX);
}

/**
 * Get the Y axis position offset.
 * This is used to place partial frames, like the ones gotten from
 * ROI readouts, in the visual space.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return Y axis position offset.
 */
static inline int32_t caerFrameEventGetPositionY(caerFrameEvent event) {
	return (le32toh(event->positionY));
}

/**
 * Set the Y axis position offset.
 * This is used to place partial frames, like the ones gotten from
 * ROI readouts, in the visual space.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param positionY Y axis position offset.
 */
static inline void caerFrameEventSetPositionY(caerFrameEvent event, int32_t positionY) {
	event->positionY = htole32(positionY);
}

/**
 * Get the pixel value at the specified (X, Y) address.
 * (X, Y) are checked against the actual possible values for this frame.
 * Different channels are not taken into account!
 * The (0, 0) pixel is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param xAddress X address value (checked).
 * @param yAddress Y address value (checked).
 *
 * @return pixel value (normalized to 16 bit depth).
 */
static inline uint16_t caerFrameEventGetPixel(caerFrameEvent event, int32_t xAddress, int32_t yAddress) {
	// Check frame bounds first.
	if (yAddress < 0 || yAddress >= caerFrameEventGetLengthY(event)) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventGetPixel() with invalid Y address of %" PRIi32 ", should be between 0 and %" PRIi32 ".",
			yAddress, caerFrameEventGetLengthY(event) - 1);
		return (0);
	}

	int32_t xLength = caerFrameEventGetLengthX(event);

	if (xAddress < 0 || xAddress >= xLength) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventGetPixel() with invalid X address of %" PRIi32 ", should be between 0 and %" PRIi32".",
			xAddress, xLength - 1);
		return (0);
	}

	// Get pixel value at specified position.
	return (le16toh(event->pixels[(yAddress * xLength) + xAddress]));
}

/**
 * Set the pixel value at the specified (X, Y) address.
 * (X, Y) are checked against the actual possible values for this frame.
 * Different channels are not taken into account!
 * The (0, 0) pixel is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param xAddress X address value (checked).
 * @param yAddress Y address value (checked).
 * @param pixelValue pixel value (normalized to 16 bit depth).
 */
static inline void caerFrameEventSetPixel(caerFrameEvent event, int32_t xAddress, int32_t yAddress, uint16_t pixelValue) {
	// Check frame bounds first.
	if (yAddress < 0 || yAddress >= caerFrameEventGetLengthY(event)) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventSetPixel() with invalid Y address of %" PRIi32 ", should be between 0 and %" PRIi32 ".",
			yAddress, caerFrameEventGetLengthY(event) - 1);
		return;
	}

	int32_t xLength = caerFrameEventGetLengthX(event);

	if (xAddress < 0 || xAddress >= xLength) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventSetPixel() with invalid X address of %" PRIi32 ", should be between 0 and %" PRIi32 ".",
			xAddress, xLength - 1);
		return;
	}

	// Set pixel value at specified position.
	event->pixels[(yAddress * xLength) + xAddress] = htole16(pixelValue);
}

/**
 * Get the pixel value at the specified (X, Y) address, taking into
 * account the specified channel.
 * (X, Y) and the channel number are checked against the actual
 * possible values for this frame.
 * The (0, 0) pixel is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param xAddress X address value (checked).
 * @param yAddress Y address value (checked).
 * @param channel the channel number (checked).
 *
 * @return pixel value (normalized to 16 bit depth).
 */
static inline uint16_t caerFrameEventGetPixelForChannel(caerFrameEvent event, int32_t xAddress, int32_t yAddress,
	uint8_t channel) {
	// Check frame bounds first.
	if (yAddress < 0 || yAddress >= caerFrameEventGetLengthY(event)) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventGetPixelForChannel() with invalid Y address of %" PRIi32 ", should be between 0 and %" PRIi32 ".",
			yAddress, caerFrameEventGetLengthY(event) - 1);
		return (0);
	}

	int32_t xLength = caerFrameEventGetLengthX(event);

	if (xAddress < 0 || xAddress >= xLength) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventGetPixelForChannel() with invalid X address of %" PRIi32 ", should be between 0 and %" PRIi32 ".",
			xAddress, xLength - 1);
		return (0);
	}

	uint8_t channelNumber = caerFrameEventGetChannelNumber(event);

	if (channel >= channelNumber) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventGetPixelForChannel() with invalid channel number of %" PRIu8 ", should be between 0 and %" PRIu8 ".",
			channel, (uint8_t) (channelNumber - 1));
		return (0);
	}

	// Get pixel value at specified position.
	return (le16toh(event->pixels[(((yAddress * xLength) + xAddress) * channelNumber) + channel]));
}

/**
 * Set the pixel value at the specified (X, Y) address, taking into
 * account the specified channel.
 * (X, Y) and the channel number are checked against the actual
 * possible values for this frame.
 * The (0, 0) pixel is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param xAddress X address value (checked).
 * @param yAddress Y address value (checked).
 * @param channel the channel number (checked).
 * @param pixelValue pixel value (normalized to 16 bit depth).
 */
static inline void caerFrameEventSetPixelForChannel(caerFrameEvent event, int32_t xAddress, int32_t yAddress,
	uint8_t channel, uint16_t pixelValue) {
	// Check frame bounds first.
	if (yAddress < 0 || yAddress >= caerFrameEventGetLengthY(event)) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventSetPixelForChannel() with invalid Y address of %" PRIi32 ", should be between 0 and %" PRIi32 ".",
			yAddress, caerFrameEventGetLengthY(event) - 1);
		return;
	}

	int32_t xLength = caerFrameEventGetLengthX(event);

	if (xAddress < 0 || xAddress >= xLength) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventSetPixelForChannel() with invalid X address of %" PRIi32 ", should be between 0 and %" PRIi32 ".",
			xAddress, xLength - 1);
		return;
	}

	uint8_t channelNumber = caerFrameEventGetChannelNumber(event);

	if (channel >= channelNumber) {
		caerLog(CAER_LOG_CRITICAL, "Frame Event",
			"Called caerFrameEventSetPixelForChannel() with invalid channel number of %" PRIu8 ", should be between 0 and %" PRIu8 ".",
			channel, (uint8_t) (channelNumber - 1));
		return;
	}

	// Set pixel value at specified position.
	event->pixels[(((yAddress * xLength) + xAddress) * channelNumber) + channel] = htole16(pixelValue);
}

/**
 * Get the pixel value at the specified (X, Y) address.
 * No checks on (X, Y) are performed!
 * The (0, 0) pixel is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param xAddress X address value (unchecked).
 * @param yAddress Y address value (unchecked).
 *
 * @return pixel value (normalized to 16 bit depth).
 */
static inline uint16_t caerFrameEventGetPixelUnsafe(caerFrameEvent event, int32_t xAddress, int32_t yAddress) {
	// Get pixel value at specified position.
	return (le16toh(event->pixels[(yAddress * caerFrameEventGetLengthX(event)) + xAddress]));
}

/**
 * Set the pixel value at the specified (X, Y) address.
 * No checks on (X, Y) are performed!
 * The (0, 0) pixel is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param xAddress X address value (unchecked).
 * @param yAddress Y address value (unchecked).
 * @param pixelValue pixel value (normalized to 16 bit depth).
 */
static inline void caerFrameEventSetPixelUnsafe(caerFrameEvent event, int32_t xAddress, int32_t yAddress,
	uint16_t pixelValue) {
	// Set pixel value at specified position.
	event->pixels[(yAddress * caerFrameEventGetLengthX(event)) + xAddress] = htole16(pixelValue);
}

/**
 * Get the pixel value at the specified (X, Y) address, taking into
 * account the specified channel.
 * No checks on (X, Y) and the channel number are performed!
 * The (0, 0) pixel is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param xAddress X address value (unchecked).
 * @param yAddress Y address value (unchecked).
 * @param channel the channel number (unchecked).
 *
 * @return pixel value (normalized to 16 bit depth).
 */
static inline uint16_t caerFrameEventGetPixelForChannelUnsafe(caerFrameEvent event, int32_t xAddress, int32_t yAddress,
	uint8_t channel) {
	enum caer_frame_event_color_channels channels = caerFrameEventGetChannelNumber(event);
	// Get pixel value at specified position.
	return (le16toh(
		event->pixels[(((yAddress * caerFrameEventGetLengthX(event)) + xAddress) * I32T(channels))+ channel]));
}

/**
 * Set the pixel value at the specified (X, Y) address, taking into
 * account the specified channel.
 * No checks on (X, Y) and the channel number are performed!
 * The (0, 0) pixel is in the upper left corner, like in OpenCV/computer graphics.
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 * @param xAddress X address value (unchecked).
 * @param yAddress Y address value (unchecked).
 * @param channel the channel number (unchecked).
 * @param pixelValue pixel value (normalized to 16 bit depth).
 */
static inline void caerFrameEventSetPixelForChannelUnsafe(caerFrameEvent event, int32_t xAddress, int32_t yAddress,
	uint8_t channel, uint16_t pixelValue) {
	enum caer_frame_event_color_channels channels = caerFrameEventGetChannelNumber(event);
	// Set pixel value at specified position.
	event->pixels[(((yAddress * caerFrameEventGetLengthX(event)) + xAddress) * I32T(channels)) + channel] = htole16(
		pixelValue);
}

/**
 * Get a direct reference to the underlying pixels array.
 * This can be used to both get and set values.
 * No checks at all are performed at any point, nor any
 * conversions, use this at your own risk!
 * Remember that the 16 bit pixel values are in little-endian!
 * The pixel array is laid out row by row (increasing X axis),
 * going from top to bottom (increasing Y axis).
 *
 * @param event a valid FrameEvent pointer. Cannot be NULL.
 *
 * @return the pixels array (16 bit integers are little-endian).
 */
static inline uint16_t *caerFrameEventGetPixelArrayUnsafe(caerFrameEvent event) {
	// Get pixels array.
	return (event->pixels);
}

/**
 * Iterator over all frame events in a packet.
 * Returns the current index in the 'caerFrameIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerFrameIteratorElement' variable
 * of type caerFrameEvent.
 *
 * FRAME_PACKET: a valid FrameEventPacket pointer. Cannot be NULL.
 */
#define CAER_FRAME_ITERATOR_ALL_START(FRAME_PACKET) \
	for (int32_t caerFrameIteratorCounter = 0; \
		caerFrameIteratorCounter < caerEventPacketHeaderGetEventNumber(&(FRAME_PACKET)->packetHeader); \
		caerFrameIteratorCounter++) { \
		caerFrameEvent caerFrameIteratorElement = caerFrameEventPacketGetEvent(FRAME_PACKET, caerFrameIteratorCounter);

/**
 * Iterator close statement.
 */
#define CAER_FRAME_ITERATOR_ALL_END }

/**
 * Iterator over only the valid frame events in a packet.
 * Returns the current index in the 'caerFrameIteratorCounter' variable of type
 * 'int32_t' and the current event in the 'caerFrameIteratorElement' variable
 * of type caerFrameEvent.
 *
 * FRAME_PACKET: a valid FrameEventPacket pointer. Cannot be NULL.
 */
#define CAER_FRAME_ITERATOR_VALID_START(FRAME_PACKET) \
	for (int32_t caerFrameIteratorCounter = 0; \
		caerFrameIteratorCounter < caerEventPacketHeaderGetEventNumber(&(FRAME_PACKET)->packetHeader); \
		caerFrameIteratorCounter++) { \
		caerFrameEvent caerFrameIteratorElement = caerFrameEventPacketGetEvent(FRAME_PACKET, caerFrameIteratorCounter); \
		if (!caerFrameEventIsValid(caerFrameIteratorElement)) { continue; } // Skip invalid frame events.

/**
 * Iterator close statement.
 */
#define CAER_FRAME_ITERATOR_VALID_END }

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_EVENTS_FRAME_H_ */
