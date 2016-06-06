#ifndef LIBCAER_SRC_DAVIS_FX3_H_
#define LIBCAER_SRC_DAVIS_FX3_H_

#include "davis_common.h"

#define DAVIS_FX3_DEVICE_NAME "DAVIS FX3"

#define DAVIS_FX3_DEVICE_VID 0x152A
#define DAVIS_FX3_DEVICE_PID 0x841A
#define DAVIS_FX3_DEVICE_DID_TYPE 0x01

#define DAVIS_FX3_REQUIRED_LOGIC_REVISION 7449
#define DAVIS_FX3_REQUIRED_FIRMWARE_VERSION 2

#define DEBUG_ENDPOINT 0x81
#define DEBUG_TRANSFER_NUM 4
#define DEBUG_TRANSFER_SIZE 64

struct davis_fx3_handle {
	// Common info and state structure (handle).
	struct davis_handle h;
	// Debug transfer support (FX3 only).
	struct libusb_transfer *debugTransfers[DEBUG_TRANSFER_NUM];
	size_t activeDebugTransfers;
};

typedef struct davis_fx3_handle *davisFX3Handle;

caerDeviceHandle davisFX3Open(uint16_t deviceID, uint8_t busNumberRestrict, uint8_t devAddressRestrict,
	const char *serialNumberRestrict);
bool davisFX3Close(caerDeviceHandle handle);

bool davisFX3SendDefaultConfig(caerDeviceHandle handle);
// Negative addresses are used for host-side configuration.
// Positive addresses (including zero) are used for device-side configuration.
bool davisFX3ConfigSet(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr, uint32_t param);
bool davisFX3ConfigGet(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr, uint32_t *param);

#endif /* LIBCAER_SRC_DAVIS_FX3_H_ */
