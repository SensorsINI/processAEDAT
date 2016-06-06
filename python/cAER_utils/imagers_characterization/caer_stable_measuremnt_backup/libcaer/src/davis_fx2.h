#ifndef LIBCAER_SRC_DAVIS_FX2_H_
#define LIBCAER_SRC_DAVIS_FX2_H_

#include "davis_common.h"

#define DAVIS_FX2_DEVICE_NAME "DAVIS FX2"

#define DAVIS_FX2_DEVICE_VID 0x152A
#define DAVIS_FX2_DEVICE_PID 0x841B
#define DAVIS_FX2_DEVICE_DID_TYPE 0x00

#define DAVIS_FX2_REQUIRED_LOGIC_REVISION 7449
#define DAVIS_FX2_REQUIRED_FIRMWARE_VERSION 3

#define VENDOR_REQUEST_CHIP_BIAS 0xC0
#define VENDOR_REQUEST_CHIP_DIAG 0xC1

struct davis_fx2_handle {
	// Common info and state structure (handle).
	struct davis_handle h;
};

typedef struct davis_fx2_handle *davisFX2Handle;

caerDeviceHandle davisFX2Open(uint16_t deviceID, uint8_t busNumberRestrict, uint8_t devAddressRestrict,
	const char *serialNumberRestrict);
bool davisFX2Close(caerDeviceHandle handle);

bool davisFX2SendDefaultConfig(caerDeviceHandle handle);
// Negative addresses are used for host-side configuration.
// Positive addresses (including zero) are used for device-side configuration.
bool davisFX2ConfigSet(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr, uint32_t param);
bool davisFX2ConfigGet(caerDeviceHandle handle, int8_t modAddr, uint8_t paramAddr, uint32_t *param);

#endif /* LIBCAER_SRC_DAVIS_FX2_H_ */
