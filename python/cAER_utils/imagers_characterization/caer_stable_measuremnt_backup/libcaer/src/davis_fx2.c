#include "davis_fx2.h"

caerDeviceHandle davisFX2Open(uint16_t deviceID, uint8_t busNumberRestrict, uint8_t devAddressRestrict,
	const char *serialNumberRestrict) {
	caerLog(CAER_LOG_DEBUG, __func__, "Initializing %s.", DAVIS_FX2_DEVICE_NAME);

	davisFX2Handle handle = calloc(1, sizeof(*handle));
	if (handle == NULL) {
		// Failed to allocate memory for device handle!
		caerLog(CAER_LOG_CRITICAL, __func__, "Failed to allocate memory for device handle.");
		return (NULL);
	}

	// Set main deviceType correctly right away.
	handle->h.deviceType = CAER_DEVICE_DAVIS_FX2;

	bool openRetVal = davisCommonOpen((davisHandle) handle, DAVIS_FX2_DEVICE_VID, DAVIS_FX2_DEVICE_PID,
	DAVIS_FX2_DEVICE_DID_TYPE, DAVIS_FX2_DEVICE_NAME, deviceID, busNumberRestrict, devAddressRestrict,
		serialNumberRestrict, DAVIS_FX2_REQUIRED_LOGIC_REVISION,
		DAVIS_FX2_REQUIRED_FIRMWARE_VERSION);
	if (!openRetVal) {
		free(handle);

		// Failed to open device and grab basic information!
		return (NULL);
	}

	return ((caerDeviceHandle) handle);
}

bool davisFX2Close(caerDeviceHandle cdh) {
	caerLog(CAER_LOG_DEBUG, ((davisHandle) cdh)->info.deviceString, "Shutting down ...");

	return (davisCommonClose((davisHandle) cdh));
}

bool davisFX2SendDefaultConfig(caerDeviceHandle cdh) {
	// First send default chip/bias config.
	if (!davisCommonSendDefaultChipConfig(cdh, &davisFX2ConfigSet)) {
		return (false);
	}

	// Send default FPGA config.
	if (!davisCommonSendDefaultFPGAConfig(cdh, &davisFX2ConfigSet)) {
		return (false);
	}

	// FX2 specific FPGA configuration.
	if (!davisFX2ConfigSet(cdh, DAVIS_CONFIG_DVS, DAVIS_CONFIG_DVS_ACK_DELAY_ROW, 14)) {
		return (false);
	}

	if (!davisFX2ConfigSet(cdh, DAVIS_CONFIG_DVS, DAVIS_CONFIG_DVS_ACK_EXTENSION_ROW, 4)) {
		return (false);
	}

	return (true);
}

bool davisFX2ConfigSet(caerDeviceHandle cdh, int8_t modAddr, uint8_t paramAddr, uint32_t param) {
	davisHandle handle = (davisHandle) cdh;

	return (davisCommonConfigSet(handle, modAddr, paramAddr, param));
}

bool davisFX2ConfigGet(caerDeviceHandle cdh, int8_t modAddr, uint8_t paramAddr, uint32_t *param) {
	davisHandle handle = (davisHandle) cdh;

	return (davisCommonConfigGet(handle, modAddr, paramAddr, param));
}
