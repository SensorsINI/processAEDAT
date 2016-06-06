#ifndef LIBCAER_SRC_DAVIS_COMMON_H_
#define LIBCAER_SRC_DAVIS_COMMON_H_

#include "devices/davis.h"
#include "ringbuffer/ringbuffer.h"
#include <stdatomic.h>
#include <libusb.h>

#ifdef HAVE_PTHREADS
	#include "c11threads_posix.h"
#endif

#define APS_READOUT_TYPES_NUM 2
#define APS_READOUT_RESET  0
#define APS_READOUT_SIGNAL 1

/**
 * Enable APS frame debugging by only looking at the reset or signal
 * frames, and not at the resulting correlated frame.
 * Supported values:
 * 0 - both/CDS (default)
 * 1 - reset read only
 * 2 - signal read only
 */
#define APS_DEBUG_FRAME 0

#define APS_ADC_DEPTH 10

#define APS_ADC_CHANNELS 1

#define APS_ROI_REGIONS_MAX 4

#define IMU6_COUNT 15
#define IMU9_COUNT 21

#define DAVIS_EVENT_TYPES 4

#define DAVIS_DATA_ENDPOINT 0x82

#define VENDOR_REQUEST_FPGA_CONFIG          0xBF
#define VENDOR_REQUEST_FPGA_CONFIG_MULTIPLE 0xC2

struct davis_state {
	// Data Acquisition Thread -> Mainloop Exchange
	RingBuffer dataExchangeBuffer;
	atomic_uint_fast32_t dataExchangeBufferSize; // Only takes effect on DataStart() calls!
	atomic_bool dataExchangeBlocking;
	atomic_bool dataExchangeStartProducers;
	atomic_bool dataExchangeStopProducers;
	void (*dataNotifyIncrease)(void *ptr);
	void (*dataNotifyDecrease)(void *ptr);
	void *dataNotifyUserPtr;
	void (*dataShutdownNotify)(void *ptr);
	void *dataShutdownUserPtr;
	// USB Device State
	libusb_context *deviceContext;
	libusb_device_handle *deviceHandle;
	// USB Transfer Settings
	atomic_uint_fast32_t usbBufferNumber;
	atomic_uint_fast32_t usbBufferSize;
	// Data Acquisition Thread
	thrd_t dataAcquisitionThread;
	atomic_bool dataAcquisitionThreadRun;
	atomic_uint_fast32_t dataAcquisitionThreadConfigUpdate;
	struct libusb_transfer **dataTransfers;
	size_t dataTransfersLength;
	size_t activeDataTransfers;
	// Timestamp fields
	int32_t wrapOverflow;
	int32_t wrapAdd;
	int32_t lastTimestamp;
	int32_t currentTimestamp;
	// DVS specific fields
	int32_t dvsTimestamp;
	uint16_t dvsLastY;
	bool dvsGotY;
	int16_t dvsSizeX;
	int16_t dvsSizeY;
	bool dvsInvertXY;
	// APS specific fields
	int16_t apsSizeX;
	int16_t apsSizeY;
	bool apsInvertXY;
	bool apsFlipX;
	bool apsFlipY;
	bool apsIgnoreEvents;
	bool apsGlobalShutter;
	bool apsResetRead;
	bool apsRGBPixelOffsetDirection; // 0 is increasing, 1 is decreasing.
	int16_t apsRGBPixelOffset;
	uint16_t apsCurrentReadoutType;
	uint16_t apsCountX[APS_READOUT_TYPES_NUM];
	uint16_t apsCountY[APS_READOUT_TYPES_NUM];
	uint16_t *apsCurrentResetFrame;
	uint16_t apsROIUpdate;
	uint16_t apsROITmpData;
	uint16_t apsROISizeX[APS_ROI_REGIONS_MAX];
	uint16_t apsROISizeY[APS_ROI_REGIONS_MAX];
	uint16_t apsROIPositionX[APS_ROI_REGIONS_MAX];
	uint16_t apsROIPositionY[APS_ROI_REGIONS_MAX];
	// IMU specific fields
	bool imuIgnoreEvents;
	uint8_t imuCount;
	uint8_t imuTmpData;
	float imuAccelScale;
	float imuGyroScale;
	// Packet Container state
	caerEventPacketContainer currentPacketContainer;
	atomic_int_fast32_t maxPacketContainerSize;
	atomic_int_fast32_t maxPacketContainerInterval;
	// Polarity Packet state
	caerPolarityEventPacket currentPolarityPacket;
	int32_t currentPolarityPacketPosition;
	atomic_int_fast32_t maxPolarityPacketSize;
	atomic_int_fast32_t maxPolarityPacketInterval;
	// Frame Packet state
	caerFrameEventPacket currentFramePacket;
	int32_t currentFramePacketPosition;
	atomic_int_fast32_t maxFramePacketSize;
	atomic_int_fast32_t maxFramePacketInterval;
	// IMU6 Packet state
	caerIMU6EventPacket currentIMU6Packet;
	int32_t currentIMU6PacketPosition;
	atomic_int_fast32_t maxIMU6PacketSize;
	atomic_int_fast32_t maxIMU6PacketInterval;
	// Special Packet state
	caerSpecialEventPacket currentSpecialPacket;
	int32_t currentSpecialPacketPosition;
	atomic_int_fast32_t maxSpecialPacketSize;
	atomic_int_fast32_t maxSpecialPacketInterval;
	// Current composite events, for later copy, to not loose them on commits.
	caerFrameEvent currentFrameEvent[APS_ROI_REGIONS_MAX];
	struct caer_imu6_event currentIMU6Event;
};

typedef struct davis_state *davisState;

struct davis_handle {
	uint16_t deviceType;
	// Information fields
	struct caer_davis_info info;
	// State for data management, common to all DAVIS.
	struct davis_state state;
};

typedef struct davis_handle *davisHandle;

bool davisCommonOpen(davisHandle handle, uint16_t VID, uint16_t PID, uint8_t DID_TYPE, const char *deviceName,
	uint16_t deviceID, uint8_t busNumberRestrict, uint8_t devAddressRestrict, const char *serialNumberRestrict,
	uint16_t requiredLogicRevision, uint16_t requiredFirmwareVersion);
bool davisCommonClose(davisHandle handle);

bool davisCommonSendDefaultFPGAConfig(caerDeviceHandle cdh,
	bool (*configSet)(caerDeviceHandle cdh, int8_t modAddr, uint8_t paramAddr, uint32_t param));
bool davisCommonSendDefaultChipConfig(caerDeviceHandle cdh,
	bool (*configSet)(caerDeviceHandle cdh, int8_t modAddr, uint8_t paramAddr, uint32_t param));

bool davisCommonConfigSet(davisHandle handle, int8_t modAddr, uint8_t paramAddr, uint32_t param);
bool davisCommonConfigGet(davisHandle handle, int8_t modAddr, uint8_t paramAddr, uint32_t *param);

bool davisCommonDataStart(caerDeviceHandle handle, void (*dataNotifyIncrease)(void *ptr),
	void (*dataNotifyDecrease)(void *ptr), void *dataNotifyUserPtr, void (*dataShutdownNotify)(void *ptr),
	void *dataShutdownUserPtr);
bool davisCommonDataStop(caerDeviceHandle handle);
caerEventPacketContainer davisCommonDataGet(caerDeviceHandle handle);

#endif /* LIBCAER_SRC_DAVIS_COMMON_H_ */
