#include "dvs128.h"

static libusb_device_handle *dvs128DeviceOpen(libusb_context *devContext, uint16_t devVID, uint16_t devPID,
	uint8_t devType, uint8_t busNumber, uint8_t devAddress, const char *serialNumber, uint16_t requiredFirmwareVersion);
static void dvs128DeviceClose(libusb_device_handle *devHandle);
static void dvs128AllocateTransfers(dvs128Handle handle, uint32_t bufferNum, uint32_t bufferSize);
static void dvs128DeallocateTransfers(dvs128Handle handle);
static void LIBUSB_CALL dvs128LibUsbCallback(struct libusb_transfer *transfer);
static void dvs128EventTranslator(dvs128Handle handle, uint8_t *buffer, size_t bytesSent);
static bool dvs128SendBiases(dvs128State state);
static int dvs128DataAcquisitionThread(void *inPtr);
static void dvs128DataAcquisitionThreadConfig(dvs128Handle handle);

static inline void checkMonotonicTimestamp(dvs128Handle handle) {
	if (handle->state.currentTimestamp < handle->state.lastTimestamp) {
		caerLog(CAER_LOG_ALERT, handle->info.deviceString,
			"Timestamps: non monotonic timestamp detected: lastTimestamp=%" PRIi32 ", currentTimestamp=%" PRIi32 ", difference=%" PRIi32 ".",
			handle->state.lastTimestamp, handle->state.currentTimestamp,
			(handle->state.lastTimestamp - handle->state.currentTimestamp));
	}
}

static inline void freeAllDataMemory(dvs128State state) {
	if (state->dataExchangeBuffer != NULL) {
		ringBufferFree(state->dataExchangeBuffer);
		state->dataExchangeBuffer = NULL;
	}

	// Since the current event packets aren't necessarily
	// already assigned to the current packet container, we
	// free them separately from it.
	if (state->currentPolarityPacket != NULL) {
		free(&state->currentPolarityPacket->packetHeader);
		state->currentPolarityPacket = NULL;

		if (state->currentPacketContainer != NULL) {
			caerEventPacketContainerSetEventPacket(state->currentPacketContainer, POLARITY_EVENT, NULL);
		}
	}

	if (state->currentSpecialPacket != NULL) {
		free(&state->currentSpecialPacket->packetHeader);
		state->currentSpecialPacket = NULL;

		if (state->currentPacketContainer != NULL) {
			caerEventPacketContainerSetEventPacket(state->currentPacketContainer, SPECIAL_EVENT, NULL);
		}
	}

	if (state->currentPacketContainer != NULL) {
		caerEventPacketContainerFree(state->currentPacketContainer);
		state->currentPacketContainer = NULL;
	}
}

caerDeviceHandle dvs128Open(uint16_t deviceID, uint8_t busNumberRestrict, uint8_t devAddressRestrict,
	const char *serialNumberRestrict) {
	caerLog(CAER_LOG_DEBUG, __func__, "Initializing %s.", DVS_DEVICE_NAME);

	dvs128Handle handle = calloc(1, sizeof(*handle));
	if (handle == NULL) {
		// Failed to allocate memory for device handle!
		caerLog(CAER_LOG_CRITICAL, __func__, "Failed to allocate memory for device handle.");
		return (NULL);
	}

	// Set main deviceType correctly right away.
	handle->deviceType = CAER_DEVICE_DVS128;

	dvs128State state = &handle->state;

	// Initialize state variables to default values (if not zero, taken care of by calloc above).
	atomic_store_explicit(&state->dataExchangeBufferSize, 64, memory_order_relaxed);
	atomic_store_explicit(&state->dataExchangeBlocking, false, memory_order_relaxed);
	atomic_store_explicit(&state->dataExchangeStartProducers, true, memory_order_relaxed);
	atomic_store_explicit(&state->dataExchangeStopProducers, true, memory_order_relaxed);
	atomic_store_explicit(&state->usbBufferNumber, 8, memory_order_relaxed);
	atomic_store_explicit(&state->usbBufferSize, 4096, memory_order_relaxed);

	// Packet settings (size (in events) and time interval (in µs)).
	atomic_store_explicit(&state->maxPacketContainerSize, 4096 + 128, memory_order_relaxed);
	atomic_store_explicit(&state->maxPacketContainerInterval, 5000, memory_order_relaxed);
	atomic_store_explicit(&state->maxPolarityPacketSize, 4096, memory_order_relaxed);
	atomic_store_explicit(&state->maxPolarityPacketInterval, 5000, memory_order_relaxed);
	atomic_store_explicit(&state->maxSpecialPacketSize, 128, memory_order_relaxed);
	atomic_store_explicit(&state->maxSpecialPacketInterval, 1000, memory_order_relaxed);

	atomic_store_explicit(&state->dvsIsMaster, true, memory_order_relaxed); // Always master by default.

	atomic_thread_fence(memory_order_release);

	// Search for device and open it.
	// Initialize libusb using a separate context for each device.
	// This is to correctly support one thread per device.
	if ((errno = libusb_init(&state->deviceContext)) != LIBUSB_SUCCESS) {
		free(handle);

		caerLog(CAER_LOG_CRITICAL, __func__, "Failed to initialize libusb context. Error: %d.", errno);
		return (NULL);
	}

	// Try to open a DVS128 device on a specific USB port.
	state->deviceHandle = dvs128DeviceOpen(state->deviceContext, DVS_DEVICE_VID, DVS_DEVICE_PID, DVS_DEVICE_DID_TYPE,
		busNumberRestrict, devAddressRestrict, serialNumberRestrict,
		DVS_REQUIRED_FIRMWARE_VERSION);
	if (state->deviceHandle == NULL) {
		libusb_exit(state->deviceContext);
		free(handle);

		caerLog(CAER_LOG_CRITICAL, __func__, "Failed to open %s device.", DVS_DEVICE_NAME);
		return (NULL);
	}

	// At this point we can get some more precise data on the device and update
	// the logging string to reflect that and be more informative.
	uint8_t busNumber = libusb_get_bus_number(libusb_get_device(state->deviceHandle));
	uint8_t devAddress = libusb_get_device_address(libusb_get_device(state->deviceHandle));

	char serialNumber[8 + 1] = { 0 };
	int getStringDescResult = libusb_get_string_descriptor_ascii(state->deviceHandle, 3, (unsigned char *) serialNumber,
		8);

	// Check serial number success and length.
	if (getStringDescResult < 0 || getStringDescResult > 8) {
		dvs128DeviceClose(state->deviceHandle);
		libusb_exit(state->deviceContext);
		free(handle);

		caerLog(CAER_LOG_CRITICAL, __func__, "Unable to get serial number for %s device.", DVS_DEVICE_NAME);
		return (NULL);
	}

	size_t fullLogStringLength = (size_t) snprintf(NULL, 0, "%s ID-%" PRIu16 " SN-%s [%" PRIu8 ":%" PRIu8 "]",
	DVS_DEVICE_NAME, deviceID, serialNumber, busNumber, devAddress);

	char *fullLogString = malloc(fullLogStringLength + 1);
	if (fullLogString == NULL) {
		dvs128DeviceClose(state->deviceHandle);
		libusb_exit(state->deviceContext);
		free(handle);

		caerLog(CAER_LOG_CRITICAL, __func__, "Unable to allocate memory for %s device info string.", DVS_DEVICE_NAME);
		return (NULL);
	}

	snprintf(fullLogString, fullLogStringLength + 1, "%s ID-%" PRIu16 " SN-%s [%" PRIu8 ":%" PRIu8 "]", DVS_DEVICE_NAME,
		deviceID, serialNumber, busNumber, devAddress);

	// Populate info variables based on data from device.
	handle->info.deviceID = I16T(deviceID);
	strncpy(handle->info.deviceSerialNumber, serialNumber, 8 + 1);
	handle->info.deviceUSBBusNumber = busNumber;
	handle->info.deviceUSBDeviceAddress = devAddress;
	handle->info.deviceString = fullLogString;
	handle->info.logicVersion = 1; // TODO: real logic revision, once that information is exposed by new logic.
	handle->info.deviceIsMaster = true; // TODO: master/slave support.
	handle->info.dvsSizeX = DVS_ARRAY_SIZE_X;
	handle->info.dvsSizeY = DVS_ARRAY_SIZE_Y;

	caerLog(CAER_LOG_DEBUG, fullLogString, "Initialized device successfully with USB Bus=%" PRIu8 ":Addr=%" PRIu8 ".",
		busNumber, devAddress);

	return ((caerDeviceHandle) handle);
}

bool dvs128Close(caerDeviceHandle cdh) {
	dvs128Handle handle = (dvs128Handle) cdh;
	dvs128State state = &handle->state;

	caerLog(CAER_LOG_DEBUG, handle->info.deviceString, "Shutting down ...");

	// Finally, close the device fully.
	dvs128DeviceClose(state->deviceHandle);

	// Destroy libusb context.
	libusb_exit(state->deviceContext);

	caerLog(CAER_LOG_DEBUG, handle->info.deviceString, "Shutdown successful.");

	// Free memory.
	free(handle->info.deviceString);
	free(handle);

	return (true);
}

struct caer_dvs128_info caerDVS128InfoGet(caerDeviceHandle cdh) {
	dvs128Handle handle = (dvs128Handle) cdh;

	// Check if the pointer is valid.
	if (handle == NULL) {
		struct caer_dvs128_info emptyInfo = { 0, .deviceString = NULL };
		return (emptyInfo);
	}

	// Check if device type is supported.
	if (handle->deviceType != CAER_DEVICE_DVS128) {
		struct caer_dvs128_info emptyInfo = { 0, .deviceString = NULL };
		return (emptyInfo);
	}

	// Return a copy of the device information.
	return (handle->info);
}

bool dvs128SendDefaultConfig(caerDeviceHandle cdh) {
	dvs128Handle handle = (dvs128Handle) cdh;
	dvs128State state = &handle->state;

	// Set all biases to default value. Based on DVS128 Fast biases.
	caerIntegerToByteArray(1992, state->biases[DVS128_CONFIG_BIAS_CAS], BIAS_LENGTH);
	caerIntegerToByteArray(1108364, state->biases[DVS128_CONFIG_BIAS_INJGND], BIAS_LENGTH);
	caerIntegerToByteArray(16777215, state->biases[DVS128_CONFIG_BIAS_REQPD], BIAS_LENGTH);
	caerIntegerToByteArray(8159221, state->biases[DVS128_CONFIG_BIAS_PUX], BIAS_LENGTH);
	caerIntegerToByteArray(132, state->biases[DVS128_CONFIG_BIAS_DIFFOFF], BIAS_LENGTH);
	caerIntegerToByteArray(309590, state->biases[DVS128_CONFIG_BIAS_REQ], BIAS_LENGTH);
	caerIntegerToByteArray(969, state->biases[DVS128_CONFIG_BIAS_REFR], BIAS_LENGTH);
	caerIntegerToByteArray(16777215, state->biases[DVS128_CONFIG_BIAS_PUY], BIAS_LENGTH);
	caerIntegerToByteArray(209996, state->biases[DVS128_CONFIG_BIAS_DIFFON], BIAS_LENGTH);
	caerIntegerToByteArray(13125, state->biases[DVS128_CONFIG_BIAS_DIFF], BIAS_LENGTH);
	caerIntegerToByteArray(271, state->biases[DVS128_CONFIG_BIAS_FOLL], BIAS_LENGTH);
	caerIntegerToByteArray(217, state->biases[DVS128_CONFIG_BIAS_PR], BIAS_LENGTH);

	// Send biases to device.
	return (dvs128SendBiases(state));
}

bool dvs128ConfigSet(caerDeviceHandle cdh, int8_t modAddr, uint8_t paramAddr, uint32_t param) {
	dvs128Handle handle = (dvs128Handle) cdh;
	dvs128State state = &handle->state;

	switch (modAddr) {
		case CAER_HOST_CONFIG_USB:
			switch (paramAddr) {
				case CAER_HOST_CONFIG_USB_BUFFER_NUMBER:
					atomic_store(&state->usbBufferNumber, param);

					// Notify data acquisition thread to change buffers.
					atomic_fetch_or(&state->dataAcquisitionThreadConfigUpdate, 1 << 0);
					break;

				case CAER_HOST_CONFIG_USB_BUFFER_SIZE:
					atomic_store(&state->usbBufferSize, param);

					// Notify data acquisition thread to change buffers.
					atomic_fetch_or(&state->dataAcquisitionThreadConfigUpdate, 1 << 0);
					break;

				default:
					return (false);
					break;
			}
			break;

		case CAER_HOST_CONFIG_DATAEXCHANGE:
			switch (paramAddr) {
				case CAER_HOST_CONFIG_DATAEXCHANGE_BUFFER_SIZE:
					atomic_store(&state->dataExchangeBufferSize, param);
					break;

				case CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING:
					atomic_store(&state->dataExchangeBlocking, param);
					break;

				case CAER_HOST_CONFIG_DATAEXCHANGE_START_PRODUCERS:
					atomic_store(&state->dataExchangeStartProducers, param);
					break;

				case CAER_HOST_CONFIG_DATAEXCHANGE_STOP_PRODUCERS:
					atomic_store(&state->dataExchangeStopProducers, param);
					break;

				default:
					return (false);
					break;
			}
			break;

		case CAER_HOST_CONFIG_PACKETS:
			switch (paramAddr) {
				case CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_SIZE:
					atomic_store(&state->maxPacketContainerSize, param);
					break;

				case CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_INTERVAL:
					atomic_store(&state->maxPacketContainerInterval, param);
					break;

				case CAER_HOST_CONFIG_PACKETS_MAX_POLARITY_SIZE:
					atomic_store(&state->maxPolarityPacketSize, param);
					break;

				case CAER_HOST_CONFIG_PACKETS_MAX_POLARITY_INTERVAL:
					atomic_store(&state->maxPolarityPacketInterval, param);
					break;

				case CAER_HOST_CONFIG_PACKETS_MAX_SPECIAL_SIZE:
					atomic_store(&state->maxSpecialPacketSize, param);
					break;

				case CAER_HOST_CONFIG_PACKETS_MAX_SPECIAL_INTERVAL:
					atomic_store(&state->maxSpecialPacketInterval, param);
					break;

				default:
					return (false);
					break;
			}
			break;

		case DVS128_CONFIG_DVS:
			switch (paramAddr) {
				case DVS128_CONFIG_DVS_RUN:
					if (param && !atomic_load(&state->dvsRunning)) {
						if (libusb_control_transfer(state->deviceHandle,
							LIBUSB_ENDPOINT_OUT | LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE,
							VENDOR_REQUEST_START_TRANSFER, 0, 0, NULL, 0, 0) != 0) {
							return (false);
						}

						atomic_store(&state->dvsRunning, true);
					}
					else if (!param && atomic_load(&state->dvsRunning)) {
						if (libusb_control_transfer(state->deviceHandle,
							LIBUSB_ENDPOINT_OUT | LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE,
							VENDOR_REQUEST_STOP_TRANSFER, 0, 0, NULL, 0, 0) != 0) {
							return (false);
						}

						atomic_store(&state->dvsRunning, false);
					}
					break;

				case DVS128_CONFIG_DVS_TIMESTAMP_RESET:
					if (param) {
						if (libusb_control_transfer(state->deviceHandle,
							LIBUSB_ENDPOINT_OUT | LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE,
							VENDOR_REQUEST_RESET_TS, 0, 0, NULL, 0, 0) != 0) {
							return (false);
						}
					}
					break;

				case DVS128_CONFIG_DVS_ARRAY_RESET:
					if (param) {
						if (libusb_control_transfer(state->deviceHandle,
							LIBUSB_ENDPOINT_OUT | LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE,
							VENDOR_REQUEST_RESET_ARRAY, 0, 0, NULL, 0, 0) != 0) {
							return (false);
						}
					}
					break;

				case DVS128_CONFIG_DVS_TS_MASTER:
					if (libusb_control_transfer(state->deviceHandle,
						LIBUSB_ENDPOINT_OUT | LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE,
						VENDOR_REQUEST_TS_MASTER, (param & 0x01), 0, NULL, 0, 0) != 0) {
						return (false);
					}
					atomic_store(&state->dvsIsMaster, (param & 0x01));

					// Ensure info struct also gets this update.
					atomic_thread_fence(memory_order_seq_cst);
					handle->info.deviceIsMaster = atomic_load(&state->dvsIsMaster);
					atomic_thread_fence(memory_order_seq_cst);
					break;

				default:
					return (false);
					break;
			}
			break;

		case DVS128_CONFIG_BIAS:
			switch (paramAddr) {
				case DVS128_CONFIG_BIAS_CAS:
				case DVS128_CONFIG_BIAS_INJGND:
				case DVS128_CONFIG_BIAS_PUX:
				case DVS128_CONFIG_BIAS_PUY:
				case DVS128_CONFIG_BIAS_REQPD:
				case DVS128_CONFIG_BIAS_REQ:
				case DVS128_CONFIG_BIAS_FOLL:
				case DVS128_CONFIG_BIAS_PR:
				case DVS128_CONFIG_BIAS_REFR:
				case DVS128_CONFIG_BIAS_DIFF:
				case DVS128_CONFIG_BIAS_DIFFON:
				case DVS128_CONFIG_BIAS_DIFFOFF:
					caerIntegerToByteArray(param, state->biases[paramAddr], BIAS_LENGTH);
					return (dvs128SendBiases(state));
					break;

				default:
					return (false);
					break;
			}
			break;

		default:
			return (false);
			break;
	}

	return (true);
}

bool dvs128ConfigGet(caerDeviceHandle cdh, int8_t modAddr, uint8_t paramAddr, uint32_t *param) {
	dvs128Handle handle = (dvs128Handle) cdh;
	dvs128State state = &handle->state;

	switch (modAddr) {
		case CAER_HOST_CONFIG_USB:
			switch (paramAddr) {
				case CAER_HOST_CONFIG_USB_BUFFER_NUMBER:
					*param = U32T(atomic_load(&state->usbBufferNumber));
					break;

				case CAER_HOST_CONFIG_USB_BUFFER_SIZE:
					*param = U32T(atomic_load(&state->usbBufferSize));
					break;

				default:
					return (false);
					break;
			}
			break;

		case CAER_HOST_CONFIG_DATAEXCHANGE:
			switch (paramAddr) {
				case CAER_HOST_CONFIG_DATAEXCHANGE_BUFFER_SIZE:
					*param = U32T(atomic_load(&state->dataExchangeBufferSize));
					break;

				case CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING:
					*param = atomic_load(&state->dataExchangeBlocking);
					break;

				case CAER_HOST_CONFIG_DATAEXCHANGE_START_PRODUCERS:
					*param = atomic_load(&state->dataExchangeStartProducers);
					break;

				case CAER_HOST_CONFIG_DATAEXCHANGE_STOP_PRODUCERS:
					*param = atomic_load(&state->dataExchangeStopProducers);
					break;

				default:
					return (false);
					break;
			}
			break;

		case CAER_HOST_CONFIG_PACKETS:
			switch (paramAddr) {
				case CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_SIZE:
					*param = U32T(atomic_load(&state->maxPacketContainerSize));
					break;

				case CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_INTERVAL:
					*param = U32T(atomic_load(&state->maxPacketContainerInterval));
					break;

				case CAER_HOST_CONFIG_PACKETS_MAX_POLARITY_SIZE:
					*param = U32T(atomic_load(&state->maxPolarityPacketSize));
					break;

				case CAER_HOST_CONFIG_PACKETS_MAX_POLARITY_INTERVAL:
					*param = U32T(atomic_load(&state->maxPolarityPacketInterval));
					break;

				case CAER_HOST_CONFIG_PACKETS_MAX_SPECIAL_SIZE:
					*param = U32T(atomic_load(&state->maxSpecialPacketSize));
					break;

				case CAER_HOST_CONFIG_PACKETS_MAX_SPECIAL_INTERVAL:
					*param = U32T(atomic_load(&state->maxSpecialPacketInterval));
					break;

				default:
					return (false);
					break;
			}
			break;

		case DVS128_CONFIG_DVS:
			switch (paramAddr) {
				case DVS128_CONFIG_DVS_RUN:
					*param = atomic_load(&state->dvsRunning);
					break;

				case DVS128_CONFIG_DVS_TIMESTAMP_RESET:
				case DVS128_CONFIG_DVS_ARRAY_RESET:
					// Always false because it's an impulse, it resets itself automatically.
					*param = false;
					break;

				case DVS128_CONFIG_DVS_TS_MASTER:
					*param = atomic_load(&state->dvsIsMaster);
					break;

				default:
					return (false);
					break;
			}
			break;

		case DVS128_CONFIG_BIAS:
			switch (paramAddr) {
				case DVS128_CONFIG_BIAS_CAS:
				case DVS128_CONFIG_BIAS_INJGND:
				case DVS128_CONFIG_BIAS_PUX:
				case DVS128_CONFIG_BIAS_PUY:
				case DVS128_CONFIG_BIAS_REQPD:
				case DVS128_CONFIG_BIAS_REQ:
				case DVS128_CONFIG_BIAS_FOLL:
				case DVS128_CONFIG_BIAS_PR:
				case DVS128_CONFIG_BIAS_REFR:
				case DVS128_CONFIG_BIAS_DIFF:
				case DVS128_CONFIG_BIAS_DIFFON:
				case DVS128_CONFIG_BIAS_DIFFOFF:
					*param = caerByteArrayToInteger(state->biases[paramAddr], BIAS_LENGTH);
					break;

				default:
					return (false);
					break;
			}
			break;

		default:
			return (false);
			break;
	}

	return (true);
}

bool dvs128DataStart(caerDeviceHandle cdh, void (*dataNotifyIncrease)(void *ptr), void (*dataNotifyDecrease)(void *ptr),
	void *dataNotifyUserPtr, void (*dataShutdownNotify)(void *ptr), void *dataShutdownUserPtr) {
	dvs128Handle handle = (dvs128Handle) cdh;
	dvs128State state = &handle->state;

	// Store new data available/not available anymore call-backs.
	state->dataNotifyIncrease = dataNotifyIncrease;
	state->dataNotifyDecrease = dataNotifyDecrease;
	state->dataNotifyUserPtr = dataNotifyUserPtr;
	state->dataShutdownNotify = dataShutdownNotify;
	state->dataShutdownUserPtr = dataShutdownUserPtr;

	// Initialize RingBuffer.
	state->dataExchangeBuffer = ringBufferInit(atomic_load(&state->dataExchangeBufferSize));
	if (state->dataExchangeBuffer == NULL) {
		caerLog(CAER_LOG_CRITICAL, handle->info.deviceString, "Failed to initialize data exchange buffer.");
		return (false);
	}

	// Allocate packets.
	state->currentPacketContainer = caerEventPacketContainerAllocate(DVS_EVENT_TYPES);
	if (state->currentPacketContainer == NULL) {
		freeAllDataMemory(state);

		caerLog(CAER_LOG_CRITICAL, handle->info.deviceString, "Failed to allocate event packet container.");
		return (false);
	}

	state->currentPolarityPacket = caerPolarityEventPacketAllocate(I32T(atomic_load(&state->maxPolarityPacketSize)),
		I16T(handle->info.deviceID), 0);
	if (state->currentPolarityPacket == NULL) {
		freeAllDataMemory(state);

		caerLog(CAER_LOG_CRITICAL, handle->info.deviceString, "Failed to allocate polarity event packet.");
		return (false);
	}

	state->currentSpecialPacket = caerSpecialEventPacketAllocate(I32T(atomic_load(&state->maxSpecialPacketSize)),
		I16T(handle->info.deviceID), 0);
	if (state->currentSpecialPacket == NULL) {
		freeAllDataMemory(state);

		caerLog(CAER_LOG_CRITICAL, handle->info.deviceString, "Failed to allocate special event packet.");
		return (false);
	}

	if ((errno = thrd_create(&state->dataAcquisitionThread, &dvs128DataAcquisitionThread, handle)) != thrd_success) {
		freeAllDataMemory(state);

		caerLog(CAER_LOG_CRITICAL, handle->info.deviceString, "Failed to start data acquisition thread. Error: %d.",
		errno);
		return (false);
	}

	// Wait for the data acquisition thread to be ready.
	while (!atomic_load_explicit(&state->dataAcquisitionThreadRun, memory_order_relaxed)) {
		;
	}

	return (true);
}

bool dvs128DataStop(caerDeviceHandle cdh) {
	dvs128Handle handle = (dvs128Handle) cdh;
	dvs128State state = &handle->state;

	// Stop data acquisition thread.
	if (atomic_load(&state->dataExchangeStopProducers)) {
		// Disable data transfer on USB end-point 6.
		dvs128ConfigSet((caerDeviceHandle) handle, DVS128_CONFIG_DVS, DVS128_CONFIG_DVS_RUN, false);
	}

	atomic_store(&state->dataAcquisitionThreadRun, false);

	// Wait for data acquisition thread to terminate...
	if ((errno = thrd_join(state->dataAcquisitionThread, NULL)) != thrd_success) {
		// This should never happen!
		caerLog(CAER_LOG_CRITICAL, handle->info.deviceString, "Failed to join data acquisition thread. Error: %d.",
		errno);
		return (false);
	}

	// Empty ringbuffer.
	caerEventPacketContainer container;
	while ((container = ringBufferGet(state->dataExchangeBuffer)) != NULL) {
		// Notify data-not-available call-back.
		if (state->dataNotifyDecrease != NULL) {
			state->dataNotifyDecrease(state->dataNotifyUserPtr);
		}

		// Free container, which will free its subordinate packets too.
		caerEventPacketContainerFree(container);
	}

	// Free current, uncommitted packets and ringbuffer.
	freeAllDataMemory(state);

	// Reset packet positions.
	state->currentPolarityPacketPosition = 0;
	state->currentSpecialPacketPosition = 0;

	return (true);
}

// Remember to properly free the returned memory after usage!
caerEventPacketContainer dvs128DataGet(caerDeviceHandle cdh) {
	dvs128Handle handle = (dvs128Handle) cdh;
	dvs128State state = &handle->state;
	caerEventPacketContainer container = NULL;

	retry: container = ringBufferGet(state->dataExchangeBuffer);

	if (container != NULL) {
		// Found an event container, return it and signal this piece of data
		// is no longer available for later acquisition.
		if (state->dataNotifyDecrease != NULL) {
			state->dataNotifyDecrease(state->dataNotifyUserPtr);
		}

		return (container);
	}

	// Didn't find any event container, either report this or retry, depending
	// on blocking setting.
	if (atomic_load_explicit(&state->dataExchangeBlocking, memory_order_relaxed)) {
		// Don't retry right away in a tight loop, back off and wait a little.
		// If no data is available, sleep for a millisecond to avoid wasting resources.
		struct timespec noDataSleep = { .tv_sec = 0, .tv_nsec = 1000000 };
		if (thrd_sleep(&noDataSleep, NULL) == 0) {
			goto retry;
		}
	}

	// Nothing.
	return (NULL);
}

static libusb_device_handle *dvs128DeviceOpen(libusb_context *devContext, uint16_t devVID, uint16_t devPID,
	uint8_t devType, uint8_t busNumber, uint8_t devAddress, const char *serialNumber, uint16_t requiredFirmwareVersion) {
	libusb_device_handle *devHandle = NULL;
	libusb_device **devicesList;

	ssize_t result = libusb_get_device_list(devContext, &devicesList);

	if (result >= 0) {
		// Cycle thorough all discovered devices and find a match.
		for (size_t i = 0; i < (size_t) result; i++) {
			struct libusb_device_descriptor devDesc;

			if (libusb_get_device_descriptor(devicesList[i], &devDesc) != LIBUSB_SUCCESS) {
				continue;
			}

			// Check if this is the device we want (VID/PID).
			if (devDesc.idVendor == devVID && devDesc.idProduct == devPID
				&& U8T((devDesc.bcdDevice & 0xFF00) >> 8) == devType) {
				// Verify device firmware version.
				if (U8T(devDesc.bcdDevice & 0x00FF) < requiredFirmwareVersion) {
					caerLog(CAER_LOG_CRITICAL, __func__,
						"Device firmware version too old. You have version %" PRIu8 "; but at least version %" PRIu16 " is required. Please updated by following the Flashy upgrade documentation at 'http://inilabs.com/support/reflashing/'.",
						U8T(devDesc.bcdDevice & 0x00FF), requiredFirmwareVersion);

					continue;
				}

				// If a USB port restriction is given, honor it.
				if (busNumber > 0 && libusb_get_bus_number(devicesList[i]) != busNumber) {
					caerLog(CAER_LOG_INFO, __func__,
						"USB bus number restriction is present (%" PRIu8 "), this device didn't match it (%" PRIu8 ").",
						busNumber, libusb_get_bus_number(devicesList[i]));

					continue;
				}

				if (devAddress > 0 && libusb_get_device_address(devicesList[i]) != devAddress) {
					caerLog(CAER_LOG_INFO, __func__,
						"USB device address restriction is present (%" PRIu8 "), this device didn't match it (%" PRIu8 ").",
						devAddress, libusb_get_device_address(devicesList[i]));

					continue;
				}

				if (libusb_open(devicesList[i], &devHandle) != LIBUSB_SUCCESS) {
					devHandle = NULL;

					continue;
				}

				// Check the serial number restriction, if any is present.
				if (serialNumber != NULL && !caerStrEquals(serialNumber, "")) {
					char deviceSerialNumber[8 + 1] = { 0 };
					int getStringDescResult = libusb_get_string_descriptor_ascii(devHandle, devDesc.iSerialNumber,
						(unsigned char *) deviceSerialNumber, 8);

					// Check serial number success and length.
					if (getStringDescResult < 0 || getStringDescResult > 8) {
						libusb_close(devHandle);
						devHandle = NULL;

						continue;
					}

					// Now check if the Serial Number matches.
					if (!caerStrEquals(serialNumber, deviceSerialNumber)) {
						libusb_close(devHandle);
						devHandle = NULL;

						caerLog(CAER_LOG_INFO, __func__,
							"USB serial number restriction is present (%s), this device didn't match it (%s).",
							serialNumber, deviceSerialNumber);

						continue;
					}
				}

				// Check that the active configuration is set to number 1. If not, do so.
				int activeConfiguration;
				if (libusb_get_configuration(devHandle, &activeConfiguration) != LIBUSB_SUCCESS) {
					libusb_close(devHandle);
					devHandle = NULL;

					continue;
				}

				if (activeConfiguration != 1) {
					if (libusb_set_configuration(devHandle, 1) != LIBUSB_SUCCESS) {
						libusb_close(devHandle);
						devHandle = NULL;

						continue;
					}
				}

				// Claim interface 0 (default).
				if (libusb_claim_interface(devHandle, 0) != LIBUSB_SUCCESS) {
					libusb_close(devHandle);
					devHandle = NULL;

					continue;
				}

				// TODO: check logic revision, once that information is exposed by new logic.

				// Found and configured it!
				break;
			}
		}

		libusb_free_device_list(devicesList, true);
	}

	return (devHandle);
}

static void dvs128DeviceClose(libusb_device_handle *devHandle) {
	// Release interface 0 (default).
	libusb_release_interface(devHandle, 0);

	libusb_close(devHandle);
}

static void dvs128AllocateTransfers(dvs128Handle handle, uint32_t bufferNum, uint32_t bufferSize) {
	dvs128State state = &handle->state;

	// Set number of transfers and allocate memory for the main transfer array.
	state->dataTransfers = calloc(bufferNum, sizeof(struct libusb_transfer *));
	if (state->dataTransfers == NULL) {
		caerLog(CAER_LOG_CRITICAL, handle->info.deviceString,
			"Failed to allocate memory for %" PRIu32 " libusb transfers. Error: %d.", bufferNum, errno);
		return;
	}
	state->dataTransfersLength = bufferNum;

	// Allocate transfers and set them up.
	for (size_t i = 0; i < bufferNum; i++) {
		state->dataTransfers[i] = libusb_alloc_transfer(0);
		if (state->dataTransfers[i] == NULL) {
			caerLog(CAER_LOG_CRITICAL, handle->info.deviceString,
				"Unable to allocate further libusb transfers (%zu of %" PRIu32 ").", i, bufferNum);
			continue;
		}

		// Create data buffer.
		state->dataTransfers[i]->length = (int) bufferSize;
		state->dataTransfers[i]->buffer = malloc(bufferSize);
		if (state->dataTransfers[i]->buffer == NULL) {
			caerLog(CAER_LOG_CRITICAL, handle->info.deviceString,
				"Unable to allocate buffer for libusb transfer %zu. Error: %d.", i, errno);

			libusb_free_transfer(state->dataTransfers[i]);
			state->dataTransfers[i] = NULL;

			continue;
		}

		// Initialize Transfer.
		state->dataTransfers[i]->dev_handle = state->deviceHandle;
		state->dataTransfers[i]->endpoint = DVS_DATA_ENDPOINT;
		state->dataTransfers[i]->type = LIBUSB_TRANSFER_TYPE_BULK;
		state->dataTransfers[i]->callback = &dvs128LibUsbCallback;
		state->dataTransfers[i]->user_data = handle;
		state->dataTransfers[i]->timeout = 0;
		state->dataTransfers[i]->flags = LIBUSB_TRANSFER_FREE_BUFFER;

		if ((errno = libusb_submit_transfer(state->dataTransfers[i])) == LIBUSB_SUCCESS) {
			state->activeDataTransfers++;
		}
		else {
			caerLog(CAER_LOG_CRITICAL, handle->info.deviceString,
				"Unable to submit libusb transfer %zu. Error: %s (%d).", i, libusb_strerror(errno), errno);

			// The transfer buffer is freed automatically here thanks to
			// the LIBUSB_TRANSFER_FREE_BUFFER flag set above.
			libusb_free_transfer(state->dataTransfers[i]);
			state->dataTransfers[i] = NULL;

			continue;
		}
	}

	if (state->activeDataTransfers == 0) {
		// Didn't manage to allocate any USB transfers, free array memory and log failure.
		free(state->dataTransfers);
		state->dataTransfers = NULL;
		state->dataTransfersLength = 0;

		caerLog(CAER_LOG_CRITICAL, handle->info.deviceString, "Unable to allocate any libusb transfers.");
	}
}

static void dvs128DeallocateTransfers(dvs128Handle handle) {
	dvs128State state = &handle->state;

	// Cancel all current transfers first.
	for (size_t i = 0; i < state->dataTransfersLength; i++) {
		if (state->dataTransfers[i] != NULL) {
			errno = libusb_cancel_transfer(state->dataTransfers[i]);
			if (errno != LIBUSB_SUCCESS && errno != LIBUSB_ERROR_NOT_FOUND) {
				caerLog(CAER_LOG_CRITICAL, handle->info.deviceString,
					"Unable to cancel libusb transfer %zu. Error: %s (%d).", i, libusb_strerror(errno), errno);
				// Proceed with trying to cancel all transfers regardless of errors.
			}
		}
	}

	// Wait for all transfers to go away (0.1 seconds timeout).
	struct timeval te = { .tv_sec = 0, .tv_usec = 100000 };

	while (state->activeDataTransfers > 0) {
		libusb_handle_events_timeout(state->deviceContext, &te);
	}

	// The buffers and transfers have been deallocated in the callback.
	// Only the transfers array remains, which we free here.
	free(state->dataTransfers);
	state->dataTransfers = NULL;
	state->dataTransfersLength = 0;
}

static void LIBUSB_CALL dvs128LibUsbCallback(struct libusb_transfer *transfer) {
	dvs128Handle handle = transfer->user_data;
	dvs128State state = &handle->state;

	if (transfer->status == LIBUSB_TRANSFER_COMPLETED) {
		// Handle data.
		dvs128EventTranslator(handle, transfer->buffer, (size_t) transfer->actual_length);
	}

	if (transfer->status != LIBUSB_TRANSFER_CANCELLED && transfer->status != LIBUSB_TRANSFER_NO_DEVICE) {
		// Submit transfer again.
		if (libusb_submit_transfer(transfer) == LIBUSB_SUCCESS) {
			return;
		}
	}

	// Cannot recover (cancelled, no device, or other critical error).
	// Signal this by adjusting the counter, free and exit.
	state->activeDataTransfers--;
	for (size_t i = 0; i < state->dataTransfersLength; i++) {
		// Remove from list, so we don't try to cancel it later on.
		if (state->dataTransfers[i] == transfer) {
			state->dataTransfers[i] = NULL;
		}
	}
	libusb_free_transfer(transfer);
}

#define DVS128_TIMESTAMP_WRAP_MASK 0x80
#define DVS128_TIMESTAMP_RESET_MASK 0x40
#define DVS128_POLARITY_SHIFT 0
#define DVS128_POLARITY_MASK 0x0001
#define DVS128_Y_ADDR_SHIFT 8
#define DVS128_Y_ADDR_MASK 0x007F
#define DVS128_X_ADDR_SHIFT 1
#define DVS128_X_ADDR_MASK 0x007F
#define DVS128_SYNC_EVENT_MASK 0x8000
#define TS_WRAP_ADD 0x4000

static void dvs128EventTranslator(dvs128Handle handle, uint8_t *buffer, size_t bytesSent) {
	dvs128State state = &handle->state;

	// Truncate off any extra partial event.
	if ((bytesSent & 0x03) != 0) {
		caerLog(CAER_LOG_ALERT, handle->info.deviceString,
			"%zu bytes received via USB, which is not a multiple of four.", bytesSent);
		bytesSent &= (size_t) ~0x03;
	}

	for (size_t i = 0; i < bytesSent; i += 4) {
		// Allocate new packets for next iteration as needed.
		if (state->currentPacketContainer == NULL) {
			state->currentPacketContainer = caerEventPacketContainerAllocate(DVS_EVENT_TYPES);
			if (state->currentPacketContainer == NULL) {
				caerLog(CAER_LOG_CRITICAL, handle->info.deviceString, "Failed to allocate event packet container.");
				return;
			}
		}

		if (state->currentPolarityPacket == NULL) {
			state->currentPolarityPacket = caerPolarityEventPacketAllocate(
				I32T(atomic_load_explicit(&state->maxPolarityPacketSize, memory_order_relaxed)),
				I16T(handle->info.deviceID), state->wrapOverflow);
			if (state->currentPolarityPacket == NULL) {
				caerLog(CAER_LOG_CRITICAL, handle->info.deviceString, "Failed to allocate polarity event packet.");
				return;
			}
		}

		if (state->currentSpecialPacket == NULL) {
			state->currentSpecialPacket = caerSpecialEventPacketAllocate(
				I32T(atomic_load_explicit(&state->maxSpecialPacketSize, memory_order_relaxed)),
				I16T(handle->info.deviceID), state->wrapOverflow);
			if (state->currentSpecialPacket == NULL) {
				caerLog(CAER_LOG_CRITICAL, handle->info.deviceString, "Failed to allocate special event packet.");
				return;
			}
		}

		bool forceCommit = false;

		if ((buffer[i + 3] & DVS128_TIMESTAMP_WRAP_MASK) == DVS128_TIMESTAMP_WRAP_MASK) {
			// Detect big timestamp wrap-around.
			if (state->wrapAdd == (INT32_MAX - (TS_WRAP_ADD - 1))) {
				// Reset wrapAdd to zero at this point, so we can again
				// start detecting overruns of the 32bit value.
				state->wrapAdd = 0;

				state->lastTimestamp = 0;
				state->currentTimestamp = 0;

				// Increment TSOverflow counter.
				state->wrapOverflow++;

				caerSpecialEvent currentEvent = caerSpecialEventPacketGetEvent(state->currentSpecialPacket,
					state->currentSpecialPacketPosition++);
				caerSpecialEventSetTimestamp(currentEvent, INT32_MAX);
				caerSpecialEventSetType(currentEvent, TIMESTAMP_WRAP);
				caerSpecialEventValidate(currentEvent, state->currentSpecialPacket);

				// Commit packets to separate before wrap from after cleanly.
				forceCommit = true;
			}
			else {
				// timestamp bit 15 is one -> wrap: now we need to increment
				// the wrapAdd, uses only 14 bit timestamps. Each wrap is 2^14 µs (~16ms).
				state->wrapAdd += TS_WRAP_ADD;

				state->lastTimestamp = state->currentTimestamp;
				state->currentTimestamp = state->wrapAdd;

				// Check monotonicity of timestamps.
				checkMonotonicTimestamp(handle);
			}
		}
		else if ((buffer[i + 3] & DVS128_TIMESTAMP_RESET_MASK) == DVS128_TIMESTAMP_RESET_MASK) {
			// timestamp bit 14 is one -> wrapAdd reset: this firmware
			// version uses reset events to reset timestamps
			state->wrapOverflow = 0;
			state->wrapAdd = 0;
			state->lastTimestamp = 0;
			state->currentTimestamp = 0;

			// Create timestamp reset event.
			caerSpecialEvent currentEvent = caerSpecialEventPacketGetEvent(state->currentSpecialPacket,
				state->currentSpecialPacketPosition++);
			caerSpecialEventSetTimestamp(currentEvent, INT32_MAX);
			caerSpecialEventSetType(currentEvent, TIMESTAMP_RESET);
			caerSpecialEventValidate(currentEvent, state->currentSpecialPacket);

			// Commit packets when doing a reset to clearly separate them.
			forceCommit = true;
		}
		else {
			// address is LSB MSB (USB is LE)
			uint16_t addressUSB = le16toh(*((uint16_t * ) (&buffer[i])));

			// same for timestamp, LSB MSB (USB is LE)
			// 15 bit value of timestamp in 1 us tick
			uint16_t timestampUSB = le16toh(*((uint16_t * ) (&buffer[i + 2])));

			// Expand to 32 bits. (Tick is 1µs already.)
			state->lastTimestamp = state->currentTimestamp;
			state->currentTimestamp = state->wrapAdd + timestampUSB;

			// Check monotonicity of timestamps.
			checkMonotonicTimestamp(handle);

			if ((addressUSB & DVS128_SYNC_EVENT_MASK) != 0) {
				// Special Trigger Event (MSB is set)
				caerSpecialEvent currentEvent = caerSpecialEventPacketGetEvent(state->currentSpecialPacket,
					state->currentSpecialPacketPosition++);
				caerSpecialEventSetTimestamp(currentEvent, state->currentTimestamp);
				caerSpecialEventSetType(currentEvent, EXTERNAL_INPUT_RISING_EDGE);
				caerSpecialEventValidate(currentEvent, state->currentSpecialPacket);
			}
			else {
				// Invert X values (flip along X axis). To correct for flipped camera.
				uint16_t x = U16T((DVS_ARRAY_SIZE_X - 1) - U16T((addressUSB >> DVS128_X_ADDR_SHIFT) & DVS128_X_ADDR_MASK));
				// Invert Y values (flip along Y axis). To convert to CG format.
				uint16_t y = U16T((DVS_ARRAY_SIZE_Y - 1) - U16T((addressUSB >> DVS128_Y_ADDR_SHIFT) & DVS128_Y_ADDR_MASK));
				// Invert polarity bit. Hardware is like this.
				bool polarity = (((addressUSB >> DVS128_POLARITY_SHIFT) & DVS128_POLARITY_MASK) == 0) ? (1) : (0);

				// Check range conformity.
				if (x >= DVS_ARRAY_SIZE_X) {
					caerLog(CAER_LOG_ALERT, handle->info.deviceString, "X address out of range (0-%d): %" PRIu16 ".",
					DVS_ARRAY_SIZE_X - 1, x);
					continue; // Skip invalid event.
				}
				if (y >= DVS_ARRAY_SIZE_Y) {
					caerLog(CAER_LOG_ALERT, handle->info.deviceString, "Y address out of range (0-%d): %" PRIu16 ".",
					DVS_ARRAY_SIZE_Y - 1, y);
					continue; // Skip invalid event.
				}

				caerPolarityEvent currentEvent = caerPolarityEventPacketGetEvent(state->currentPolarityPacket,
					state->currentPolarityPacketPosition++);
				caerPolarityEventSetTimestamp(currentEvent, state->currentTimestamp);
				caerPolarityEventSetPolarity(currentEvent, polarity);
				caerPolarityEventSetColor(currentEvent, W);
				caerPolarityEventSetY(currentEvent, y);
				caerPolarityEventSetX(currentEvent, x);
				caerPolarityEventValidate(currentEvent, state->currentPolarityPacket);
			}
		}

		// Thresholds on which to trigger packet container commit.
		// forceCommit is already defined above.
		int32_t polaritySize = state->currentPolarityPacketPosition;
		int32_t polarityInterval =
			(polaritySize > 1) ?
				(caerPolarityEventGetTimestamp(
					caerPolarityEventPacketGetEvent(state->currentPolarityPacket, polaritySize - 1))
					- caerPolarityEventGetTimestamp(caerPolarityEventPacketGetEvent(state->currentPolarityPacket, 0))) :
				(0);

		int32_t specialSize = state->currentSpecialPacketPosition;
		int32_t specialInterval =
			(specialSize > 1) ?
				(caerSpecialEventGetTimestamp(
					caerSpecialEventPacketGetEvent(state->currentSpecialPacket, specialSize - 1))
					- caerSpecialEventGetTimestamp(caerSpecialEventPacketGetEvent(state->currentSpecialPacket, 0))) :
				(0);

		// Trigger if any of the global container-wide thresholds are met.
		bool containerCommit = (((polaritySize + specialSize)
			>= atomic_load_explicit(&state->maxPacketContainerSize, memory_order_relaxed))
			|| (polarityInterval >= atomic_load_explicit(&state->maxPacketContainerInterval, memory_order_relaxed))
			|| (specialInterval >= atomic_load_explicit(&state->maxPacketContainerInterval, memory_order_relaxed)));

		// Trigger if any of the packet-specific thresholds are met.
		bool polarityPacketCommit = ((polaritySize
			>= caerEventPacketHeaderGetEventCapacity(&state->currentPolarityPacket->packetHeader))
			|| (polarityInterval >= atomic_load_explicit(&state->maxPolarityPacketInterval, memory_order_relaxed)));

		// Trigger if any of the packet-specific thresholds are met.
		bool specialPacketCommit = ((specialSize
			>= caerEventPacketHeaderGetEventCapacity(&state->currentSpecialPacket->packetHeader))
			|| (specialInterval >= atomic_load_explicit(&state->maxSpecialPacketInterval, memory_order_relaxed)));

		// Commit packet containers to the ring-buffer, so they can be processed by the
		// main-loop, when any of the required conditions are met.
		if (forceCommit || containerCommit || polarityPacketCommit || specialPacketCommit) {
			// One or more of the commit triggers are hit. Set the packet container up to contain
			// any non-empty packets. Empty packets are not forwarded to save memory.
			if (polaritySize > 0) {
				caerEventPacketContainerSetEventPacket(state->currentPacketContainer, POLARITY_EVENT,
					(caerEventPacketHeader) state->currentPolarityPacket);

				state->currentPolarityPacket = NULL;
				state->currentPolarityPacketPosition = 0;
			}

			if (specialSize > 0) {
				caerEventPacketContainerSetEventPacket(state->currentPacketContainer, SPECIAL_EVENT,
					(caerEventPacketHeader) state->currentSpecialPacket);

				state->currentSpecialPacket = NULL;
				state->currentSpecialPacketPosition = 0;
			}

			retry_important: if (!ringBufferPut(state->dataExchangeBuffer, state->currentPacketContainer)) {
				// Failed to forward packet container, drop it, unless it contains a timestamp
				// related change, those are critical, so we just spin until we can
				// deliver that one. (Easily detected by forceCommit!)
				if (forceCommit) {
					goto retry_important;
				}
				else {
					// Failed to forward packet container, just drop it, it doesn't contain
					// any critical information anyway.
					caerLog(CAER_LOG_INFO, handle->info.deviceString,
						"Dropped EventPacket Container because ring-buffer full!");

					// Re-use the event-packet container to avoid having to reallocate it.
					// The contained event packets do have to be dropped first!
					free(caerEventPacketContainerGetEventPacket(state->currentPacketContainer, POLARITY_EVENT));
					free(caerEventPacketContainerGetEventPacket(state->currentPacketContainer, SPECIAL_EVENT));

					caerEventPacketContainerSetEventPacket(state->currentPacketContainer, POLARITY_EVENT, NULL);
					caerEventPacketContainerSetEventPacket(state->currentPacketContainer, SPECIAL_EVENT, NULL);
				}
			}
			else {
				if (state->dataNotifyIncrease != NULL) {
					state->dataNotifyIncrease(state->dataNotifyUserPtr);
				}

				state->currentPacketContainer = NULL;
			}
		}
	}
}

static bool dvs128SendBiases(dvs128State state) {
	// Biases are already stored in an array with the same format as expected by
	// the device, we can thus send it directly.
	return (libusb_control_transfer(state->deviceHandle,
		LIBUSB_ENDPOINT_OUT | LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE,
		VENDOR_REQUEST_SEND_BIASES, 0, 0, (uint8_t *) state->biases, (BIAS_NUMBER * BIAS_LENGTH), 0)
		== (BIAS_NUMBER * BIAS_LENGTH));
}

static int dvs128DataAcquisitionThread(void *inPtr) {
	// inPtr is a pointer to device handle.
	dvs128Handle handle = inPtr;
	dvs128State state = &handle->state;

	caerLog(CAER_LOG_DEBUG, handle->info.deviceString, "Initializing data acquisition thread ...");

	// Reset configuration update, so as to not re-do work afterwards.
	atomic_store(&state->dataAcquisitionThreadConfigUpdate, 0);

	if (atomic_load(&state->dataExchangeStartProducers)) {
		// Enable data transfer on USB end-point 6.
		dvs128ConfigSet((caerDeviceHandle) handle, DVS128_CONFIG_DVS, DVS128_CONFIG_DVS_RUN, true);
	}

	// Create buffers as specified in config file.
	dvs128AllocateTransfers(handle, U32T(atomic_load(&state->usbBufferNumber)),
		U32T(atomic_load(&state->usbBufferSize)));

	// Signal data thread ready back to start function.
	atomic_store(&state->dataAcquisitionThreadRun, true);

	caerLog(CAER_LOG_DEBUG, handle->info.deviceString, "data acquisition thread ready to process events.");

	// Handle USB events (1 second timeout).
	struct timeval te = { .tv_sec = 0, .tv_usec = 1000000 };

	while (atomic_load_explicit(&state->dataAcquisitionThreadRun, memory_order_relaxed)
		&& state->activeDataTransfers > 0) {
		// Check config refresh, in this case to adjust buffer sizes.
		if (atomic_load_explicit(&state->dataAcquisitionThreadConfigUpdate, memory_order_relaxed) != 0) {
			dvs128DataAcquisitionThreadConfig(handle);
		}

		libusb_handle_events_timeout(state->deviceContext, &te);
	}

	caerLog(CAER_LOG_DEBUG, handle->info.deviceString, "shutting down data acquisition thread ...");

	// Cancel all transfers and handle them.
	dvs128DeallocateTransfers(handle);

	// Ensure shutdown is stored and notified, could be because of all data transfers going away!
	atomic_store(&state->dataAcquisitionThreadRun, false);

	if (state->dataShutdownNotify != NULL) {
		state->dataShutdownNotify(state->dataShutdownUserPtr);
	}

	caerLog(CAER_LOG_DEBUG, handle->info.deviceString, "data acquisition thread shut down.");

	return (EXIT_SUCCESS);
}

static void dvs128DataAcquisitionThreadConfig(dvs128Handle handle) {
	dvs128State state = &handle->state;

	// Get the current value to examine by atomic exchange, since we don't
	// want there to be any possible store between a load/store pair.
	uint32_t configUpdate = U32T(atomic_exchange(&state->dataAcquisitionThreadConfigUpdate, 0));

	if ((configUpdate >> 0) & 0x01) {
		// Do buffer size change: cancel all and recreate them.
		dvs128DeallocateTransfers(handle);
		dvs128AllocateTransfers(handle, U32T(atomic_load(&state->usbBufferNumber)),
			U32T(atomic_load(&state->usbBufferSize)));
	}
}
