/**
 * @file usb.h
 *
 * Common functions to access, configure and exchange data with
 * supported USB devices. Also contains defines for host/USB
 * related configuration options.
 */

#ifndef LIBCAER_DEVICES_USB_H_
#define LIBCAER_DEVICES_USB_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "../libcaer.h"
#include "../events/packetContainer.h"

/**
 * Reference to an open device on which to operate.
 */
typedef struct caer_device_handle *caerDeviceHandle;

/**
 * Module address: host-side USB configuration.
 */
#define CAER_HOST_CONFIG_USB -1
/**
 * Module address: host-side data exchange (ring-buffer) configuration.
 */
#define CAER_HOST_CONFIG_DATAEXCHANGE -2
/**
 * Module address: host-side event packets generation configuration.
 */
#define CAER_HOST_CONFIG_PACKETS -3

/**
 * Parameter address for module CAER_HOST_CONFIG_USB:
 * set number of buffers used by libusb for asynchronous data transfers
 * with the USB device. The default values are usually fine, only change
 * them if you're running into I/O limits.
 */
#define CAER_HOST_CONFIG_USB_BUFFER_NUMBER 0
/**
 * Parameter address for module CAER_HOST_CONFIG_USB:
 * set size of each buffer used by libusb for asynchronous data transfers
 * with the USB device. The default values are usually fine, only change
 * them if you're running into I/O limits.
 */
#define CAER_HOST_CONFIG_USB_BUFFER_SIZE   1

/**
 * Parameter address for module CAER_HOST_CONFIG_DATAEXCHANGE:
 * set size of elements that can be held by the thread-safe FIFO
 * buffer between the USB data transfer thread and the main thread.
 * The default values are usually fine, only change them if you're
 * running into lots of dropped/missing packets; you can turn on
 * the INFO log level to see when this is the case.
 */
#define CAER_HOST_CONFIG_DATAEXCHANGE_BUFFER_SIZE     0
/**
 * Parameter address for module CAER_HOST_CONFIG_DATAEXCHANGE:
 * when calling caerDeviceDataGet(), the function can either be
 * blocking, meaning it waits until it has a valid
 * EventPacketContainer to return, or not, meaning it returns
 * right away. This behavior can be set with this flag.
 * Please see the caerDeviceDataGet() documentation for more
 * information on its return values.
 */
#define CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING        1
/**
 * Parameter address for module CAER_HOST_CONFIG_DATAEXCHANGE:
 * whether to start all the data producer modules on the device
 * (DVS, APS, Mux, ...) automatically when starting the USB
 * data transfer thread with caerDeviceDataStart() or not.
 * If disabled, be aware you will have to start the right modules
 * manually, which can be useful if you need precise control
 * over which ones are running at any time.
 */
 #define CAER_HOST_CONFIG_DATAEXCHANGE_START_PRODUCERS 2
/**
 * Parameter address for module CAER_HOST_CONFIG_DATAEXCHANGE:
 * whether to stop all the data producer modules on the device
 * (DVS, APS, Mux, ...) automatically when stopping the USB
 * data transfer thread with caerDeviceDataStop() or not.
 * If disabled, be aware you will have to stop the right modules
 * manually, to halt the data flow, which can be useful if you
 * need precise control over which ones are running at any time.
 */
 #define CAER_HOST_CONFIG_DATAEXCHANGE_STOP_PRODUCERS  3

/**
 * Parameter address for module CAER_HOST_CONFIG_PACKETS:
 * set the maximum number of events a packet container may
 * hold before it's made available to the user via caerDeviceDataGet().
 * This is a sum of the number of events held in each typed
 * EventPacket that is a part of the EventPacketContainer.
 */
#define CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_SIZE     0
/**
 * Parameter address for module CAER_HOST_CONFIG_PACKETS:
 * set the maximum interval between the earliest and the latest
 * event in a packet container before it's made available to
 * the user via caerDeviceDataGet(). The value is in
 * microseconds, and is checked across all types of events
 * contained in the EventPacketContainer.
 */
#define CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_INTERVAL 1
/**
 * Parameter address for module CAER_HOST_CONFIG_PACKETS:
 * set the maximum number of events a PolarityEventPacket may
 * hold before it's made available to the user via caerDeviceDataGet().
 * This will trigger the commit of the full EventPacketContainer.
 */
#define CAER_HOST_CONFIG_PACKETS_MAX_POLARITY_SIZE      2
/**
 * Parameter address for module CAER_HOST_CONFIG_PACKETS:
 * set the maximum interval between the earliest and the latest
 * event in a PolarityEventPacket before it's made available to
 * the user via caerDeviceDataGet(). The value is in
 * microseconds. This will trigger the commit of the
 * full EventPacketContainer.
 */
#define CAER_HOST_CONFIG_PACKETS_MAX_POLARITY_INTERVAL  3
/**
 * Parameter address for module CAER_HOST_CONFIG_PACKETS:
 * set the maximum number of events a SpecialEventPacket may
 * hold before it's made available to the user via caerDeviceDataGet().
 * This will trigger the commit of the full EventPacketContainer.
 */
#define CAER_HOST_CONFIG_PACKETS_MAX_SPECIAL_SIZE       4
/**
 * Parameter address for module CAER_HOST_CONFIG_PACKETS:
 * set the maximum interval between the earliest and the latest
 * event in a SpecialEventPacket before it's made available to
 * the user via caerDeviceDataGet(). The value is in
 * microseconds. This will trigger the commit of the
 * full EventPacketContainer.
 */
#define CAER_HOST_CONFIG_PACKETS_MAX_SPECIAL_INTERVAL   5
/**
 * Parameter address for module CAER_HOST_CONFIG_PACKETS:
 * set the maximum number of events a FrameEventPacket may
 * hold before it's made available to the user via caerDeviceDataGet().
 * This will trigger the commit of the full EventPacketContainer.
 */
#define CAER_HOST_CONFIG_PACKETS_MAX_FRAME_SIZE         6
/**
 * Parameter address for module CAER_HOST_CONFIG_PACKETS:
 * set the maximum interval between the earliest and the latest
 * event in a FrameEventPacket before it's made available to
 * the user via caerDeviceDataGet(). The value is in
 * microseconds. This will trigger the commit of the
 * full EventPacketContainer.
 */
#define CAER_HOST_CONFIG_PACKETS_MAX_FRAME_INTERVAL     7
/**
 * Parameter address for module CAER_HOST_CONFIG_PACKETS:
 * set the maximum number of events an IMU6EventPacket may
 * hold before it's made available to the user via caerDeviceDataGet().
 * This will trigger the commit of the full EventPacketContainer.
 */
#define CAER_HOST_CONFIG_PACKETS_MAX_IMU6_SIZE          8
/**
 * Parameter address for module CAER_HOST_CONFIG_PACKETS:
 * set the maximum interval between the earliest and the latest
 * event in an IMU6EventPacket before it's made available to
 * the user via caerDeviceDataGet(). The value is in
 * microseconds. This will trigger the commit of the
 * full EventPacketContainer.
 */
#define CAER_HOST_CONFIG_PACKETS_MAX_IMU6_INTERVAL      9

/**
 * Open a specified USB device, assign an ID to it and return a handle for further usage.
 * Various means can be employed to limit the selection of the device.
 *
 * @param deviceID a unique ID to identify the device from others. Will be used as the
 *                 source for EventPackets being generate from its data.
 * @param deviceType type of the device to open. Currently supported are:
 *                   CAER_DEVICE_DVS128, CAER_DEVICE_DAVIS_FX2, CAER_DEVICE_DAVIS_FX3
 * @param busNumberRestrict restrict the search for viable devices to only this USB bus number.
 * @param devAddressRestrict restrict the search for viable devices to only this USB device address.
 * @param serialNumberRestrict restrict the search for viable devices to only devices which do
 *                             possess the given Serial Number in their USB SerialNumber descriptor.
 *
 * @return a valid device handle that can be used with the other libcaer functions,
 *         or NULL on error. Always check for this!
 */
caerDeviceHandle caerDeviceOpen(uint16_t deviceID, uint16_t deviceType, uint8_t busNumberRestrict,
	uint8_t devAddressRestrict, const char *serialNumberRestrict);
/**
 * Close a previously opened USB device and invalidate its handle.
 *
 * @param handle pointer to a valid device handle. Will set handle to NULL if closing is
 *               successful, to prevent further usage of this handle for other operations.
 *
 * @return true if closing was successful, false on errors.
 */
bool caerDeviceClose(caerDeviceHandle *handle);

/**
 * Send a set of good default configuration settings to the device.
 * This avoids users having to set every configuration option each time,
 * especially when wanting to get going quickly or just needing to change
 * a few settings to get to the desired operating mode.
 *
 * @param handle a valid device handle.
 *
 * @return true if sending the configuration was successful, false on errors.
 */
bool caerDeviceSendDefaultConfig(caerDeviceHandle handle);

/**
 * Set a configuration parameter to a given value.
 *
 * @param handle a valid device handle.
 * @param modAddr a module address, used to specify which configuration module
 *                one wants to update. Negative addresses are used for host-side
 *                configuration, while positive addresses (including zero) are
 *                used for device-side configuration.
 * @param paramAddr a parameter address, to select a specific parameter to update
 *                  from this particular configuration module. Only positive numbers
 *                  (including zero) are allowed.
 * @param param a configuration parameter's new value.
 *
 * @return true if sending the configuration was successful, false on errors.
 */
bool caerDeviceConfigSet(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr, uint32_t param);

/**
 * Get the value of a configuration parameter.
 *
 * @param handle a valid device handle.
 * @param modAddr a module address, used to specify which configuration module
 *                one wants to query. Negative addresses are used for host-side
 *                configuration, while positive addresses (including zero) are
 *                used for device-side configuration.
 * @param paramAddr a parameter address, to select a specific parameter to query
 *                  from this particular configuration module. Only positive numbers
 *                  (including zero) are allowed.
 * @param param a pointer to an integer, in which to store the configuration
 *              parameter's current value. The integer will always be either set
 *              to zero (on failure), or to the current value (on success).
 *
 * @return true if sending the configuration was successful, false on errors.
 */
bool caerDeviceConfigGet(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr, uint32_t *param);

/**
 * Start getting data from the device, setting up the USB data transfer thread
 * and starting the data producers (see CAER_HOST_CONFIG_DATAEXCHANGE_START_PRODUCERS).
 * Supports notification of new data and shutdown events via user-defined call-backs.
 *
 * @param handle a valid device handle.
 * @param dataNotifyIncrease function pointer, called every time a new piece of data
 *                           available and has been put in the FIFO buffer for consumption.
 *                           dataNotifyUserPtr will be passed as parameter to the function.
 * @param dataNotifyDecrease function pointer, called every time a new piece of data
 *                           has been consumed from the FIFO buffer inside caerDeviceDataGet().
 *                           dataNotifyUserPtr will be passed as parameter to the function.
 * @param dataNotifyUserPtr pointer that will be passed to the dataNotifyIncrease and
 *                          dataNotifyDecrease functions. Can be NULL.
 * @param dataShutdownNotify function pointer, called on shut-down of the USB data transfer
 *                           thread. This can be used to detect exceptional shut-downs that
 *                           do not come from calling caerDeviceDataStop(), such as when the
 *                           device is disconnected or all USB transfers fail.
 * @param dataShutdownUserPtr pointer that will be passed to the dataShutdownNotify
 *                            function. Can be NULL.
 *
 * @return true if starting the data transfer was successful, false on errors.
 */
bool caerDeviceDataStart(caerDeviceHandle handle, void (*dataNotifyIncrease)(void *ptr),
	void (*dataNotifyDecrease)(void *ptr), void *dataNotifyUserPtr, void (*dataShutdownNotify)(void *ptr),
	void *dataShutdownUserPtr);

/**
 * Stop getting data from the device, shutting down the USB data transfer thread
 * and stopping the data producers (see CAER_HOST_CONFIG_DATAEXCHANGE_STOP_PRODUCERS).
 * This normal shut-down will also generate a notification (see caerDeviceDataStart()).
 *
 * @param handle a valid device handle.
 *
 * @return true if stopping the data transfer was successful, false on errors.
 */
bool caerDeviceDataStop(caerDeviceHandle handle);

/**
 * Get an event packet container, which contains events of various types generated by
 * the device, from the USB data transfer thread for further processing.
 * The returned data structures are allocated in memory and will need to be freed.
 * The caerEventPacketContainerFree() function can be used to correctly free the full
 * container memory. For single caerEventPackets, just use free().
 * This function can be made blocking with the CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING
 * configuration parameter. By default it is non-blocking.
 *
 * @param handle a valid device handle.
 *
 * @return a valid event packet container. NULL will be returned on errors, or when
 *         there is no container available in non-blocking mode. Always check for this!
 */
caerEventPacketContainer caerDeviceDataGet(caerDeviceHandle handle);

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_DEVICES_USB_H_ */
