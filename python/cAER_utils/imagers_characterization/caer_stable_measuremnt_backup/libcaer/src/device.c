#include "devices/usb.h"

#include "dvs128.h"
#include "davis_common.h"
#include "davis_fx2.h"
#include "davis_fx3.h"

/**
 * Number of devices supported by this library.
 */
#define SUPPORTED_DEVICES_NUMBER 3

// Supported devices and their functions.
static caerDeviceHandle (*constructors[SUPPORTED_DEVICES_NUMBER])(uint16_t deviceID, uint8_t busNumberRestrict,
	uint8_t devAddressRestrict, const char *serialNumberRestrict) = {
		[CAER_DEVICE_DVS128] = &dvs128Open,
		[CAER_DEVICE_DAVIS_FX2] = &davisFX2Open,
		[CAER_DEVICE_DAVIS_FX3] = &davisFX3Open
};

static bool (*destructors[SUPPORTED_DEVICES_NUMBER])(caerDeviceHandle handle) = {
	[CAER_DEVICE_DVS128] = &dvs128Close,
	[CAER_DEVICE_DAVIS_FX2] = &davisFX2Close,
	[CAER_DEVICE_DAVIS_FX3] = &davisFX3Close
};

static bool (*defaultConfigSenders[SUPPORTED_DEVICES_NUMBER])(caerDeviceHandle handle) = {
	[CAER_DEVICE_DVS128] = &dvs128SendDefaultConfig,
	[CAER_DEVICE_DAVIS_FX2] = &davisFX2SendDefaultConfig,
	[CAER_DEVICE_DAVIS_FX3] = &davisFX3SendDefaultConfig
};

static bool (*configSetters[SUPPORTED_DEVICES_NUMBER])(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr,
	uint32_t param) = {
		[CAER_DEVICE_DVS128] = &dvs128ConfigSet,
		[CAER_DEVICE_DAVIS_FX2] = &davisFX2ConfigSet,
		[CAER_DEVICE_DAVIS_FX3] = &davisFX3ConfigSet
};

static bool (*configGetters[SUPPORTED_DEVICES_NUMBER])(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr,
	uint32_t *param) = {
		[CAER_DEVICE_DVS128] = &dvs128ConfigGet,
		[CAER_DEVICE_DAVIS_FX2] = &davisFX2ConfigGet,
		[CAER_DEVICE_DAVIS_FX3] = &davisFX3ConfigGet
};

static bool (*dataStarters[SUPPORTED_DEVICES_NUMBER])(caerDeviceHandle handle, void (*dataNotifyIncrease)(void *ptr),
	void (*dataNotifyDecrease)(void *ptr), void *dataNotifyUserPtr, void (*dataShutdownNotify)(void *ptr),
	void *dataShutdownUserPtr) = {
		[CAER_DEVICE_DVS128] = &dvs128DataStart,
		[CAER_DEVICE_DAVIS_FX2] = &davisCommonDataStart,
		[CAER_DEVICE_DAVIS_FX3] = &davisCommonDataStart
};

static bool (*dataStoppers[SUPPORTED_DEVICES_NUMBER])(caerDeviceHandle handle) = {
	[CAER_DEVICE_DVS128] = &dvs128DataStop,
	[CAER_DEVICE_DAVIS_FX2] = &davisCommonDataStop,
	[CAER_DEVICE_DAVIS_FX3] = &davisCommonDataStop
};

static caerEventPacketContainer (*dataGetters[SUPPORTED_DEVICES_NUMBER])(caerDeviceHandle handle) = {
	[CAER_DEVICE_DVS128] = &dvs128DataGet,
	[CAER_DEVICE_DAVIS_FX2] = &davisCommonDataGet,
	[CAER_DEVICE_DAVIS_FX3] = &davisCommonDataGet
};

struct caer_device_handle {
	uint16_t deviceType;
// This is compatible with all device handle structures.
// The first member is always 'uint16_t deviceType'.
};

caerDeviceHandle caerDeviceOpen(uint16_t deviceID, uint16_t deviceType, uint8_t busNumberRestrict,
	uint8_t devAddressRestrict, const char *serialNumberRestrict) {
	// Check if device type is supported.
	if (deviceType >= SUPPORTED_DEVICES_NUMBER) {
		return (NULL);
	}

	// Execute main constructor function.
	return (constructors[deviceType](deviceID, busNumberRestrict, devAddressRestrict, serialNumberRestrict));
}

bool caerDeviceClose(caerDeviceHandle *handlePtr) {
	// We want a pointer here so we can ensure the reference is set to NULL.
	// Check if either it, or the memory pointed to, are NULL and abort
	// if that's the case.
	if (handlePtr == NULL) {
		return (false);
	}

	if (*handlePtr == NULL) {
		return (false);
	}

	// Check if device type is supported.
	if ((*handlePtr)->deviceType >= SUPPORTED_DEVICES_NUMBER) {
		return (false);
	}

	// Call appropriate destructor function.
	bool retVal = destructors[(*handlePtr)->deviceType](*handlePtr);

	// Done. Set reference to NULL if successful.
	if (retVal) {
		*handlePtr = NULL;
	}

	return (retVal);
}

bool caerDeviceSendDefaultConfig(caerDeviceHandle handle) {
	// Check if the pointer is valid.
	if (handle == NULL) {
		return (false);
	}

	// Check if device type is supported.
	if (handle->deviceType >= SUPPORTED_DEVICES_NUMBER) {
		return (false);
	}

	// Call appropriate function.
	return (defaultConfigSenders[handle->deviceType](handle));
}

bool caerDeviceConfigSet(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr, uint32_t param) {
	// Check if the pointer is valid.
	if (handle == NULL) {
		return (false);
	}

	// Check if device type is supported.
	if (handle->deviceType >= SUPPORTED_DEVICES_NUMBER) {
		return (false);
	}

	// Call appropriate function.
	return (configSetters[handle->deviceType](handle, modAddr, paramAddr, param));
}

bool caerDeviceConfigGet(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr, uint32_t *param) {
	// Check if the pointer is valid.
	if (handle == NULL) {
		return (false);
	}

	// Check if device type is supported.
	if (handle->deviceType >= SUPPORTED_DEVICES_NUMBER) {
		return (false);
	}

	// Ensure content of param is zeroed out.
	*param = 0;

	// Call appropriate function.
	return (configGetters[handle->deviceType](handle, modAddr, paramAddr, param));
}

bool caerDeviceDataStart(caerDeviceHandle handle, void (*dataNotifyIncrease)(void *ptr),
	void (*dataNotifyDecrease)(void *ptr), void *dataNotifyUserPtr, void (*dataShutdownNotify)(void *ptr),
	void *dataShutdownUserPtr) {
	// Check if the pointer is valid.
	if (handle == NULL) {
		return (false);
	}

	// Check if device type is supported.
	if (handle->deviceType >= SUPPORTED_DEVICES_NUMBER) {
		return (false);
	}

	// Call appropriate function.
	return (dataStarters[handle->deviceType](handle, dataNotifyIncrease, dataNotifyDecrease, dataNotifyUserPtr,
		dataShutdownNotify, dataShutdownUserPtr));
}

bool caerDeviceDataStop(caerDeviceHandle handle) {
	// Check if the pointer is valid.
	if (handle == NULL) {
		return (false);
	}

	// Check if device type is supported.
	if (handle->deviceType >= SUPPORTED_DEVICES_NUMBER) {
		return (false);
	}

	// Call appropriate function.
	return (dataStoppers[handle->deviceType](handle));
}

caerEventPacketContainer caerDeviceDataGet(caerDeviceHandle handle) {
	// Check if the pointer is valid.
	if (handle == NULL) {
		return (false);
	}

	// Check if device type is supported.
	if (handle->deviceType >= SUPPORTED_DEVICES_NUMBER) {
		return (false);
	}

	// Call appropriate function.
	return (dataGetters[handle->deviceType](handle));
}
