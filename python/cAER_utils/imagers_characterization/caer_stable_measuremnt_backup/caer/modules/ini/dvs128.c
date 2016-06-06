/*
 * dvs128.c
 *
 *  Created on: Nov 26, 2013
 *      Author: chtekk
 */

#include "dvs128.h"
#include "base/mainloop.h"
#include "base/module.h"

#include <libcaer/devices/dvs128.h>

static bool caerInputDVS128Init(caerModuleData moduleData);
static void caerInputDVS128Run(caerModuleData moduleData, size_t argsNumber, va_list args);
// CONFIG: Nothing to do here in the main thread!
// All configuration is asynchronous through SSHS listeners.
static void caerInputDVS128Exit(caerModuleData moduleData);

static struct caer_module_functions caerInputDVS128Functions = { .moduleInit = &caerInputDVS128Init, .moduleRun =
	&caerInputDVS128Run, .moduleConfig = NULL, .moduleExit = &caerInputDVS128Exit };

caerEventPacketContainer caerInputDVS128(uint16_t moduleID) {
	caerModuleData moduleData = caerMainloopFindModule(moduleID, "DVS128");

	caerEventPacketContainer result = NULL;

	caerModuleSM(&caerInputDVS128Functions, moduleData, 0, 1, &result);

	return (result);
}

static void createDefaultConfiguration(caerModuleData moduleData);
static void sendDefaultConfiguration(caerModuleData moduleData);
static void mainloopDataNotifyIncrease(void *p);
static void mainloopDataNotifyDecrease(void *p);
static void moduleShutdownNotify(void *p);
static void biasConfigSend(sshsNode node, caerModuleData moduleData);
static void biasConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue);
static void dvsConfigSend(sshsNode node, caerModuleData moduleData);
static void dvsConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue);
static void usbConfigSend(sshsNode node, caerModuleData moduleData);
static void usbConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue);
static void systemConfigSend(sshsNode node, caerModuleData moduleData);
static void systemConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue);

static bool caerInputDVS128Init(caerModuleData moduleData) {
	caerLog(CAER_LOG_DEBUG, moduleData->moduleSubSystemString, "Initializing module ...");

	// USB port/bus/SN settings/restrictions.
	// These can be used to force connection to one specific device at startup.
	sshsNodePutShortIfAbsent(moduleData->moduleNode, "BusNumber", 0);
	sshsNodePutShortIfAbsent(moduleData->moduleNode, "DevAddress", 0);
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "SerialNumber", "");

	// Add auto-restart setting.
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "Auto-Restart", true);

	// Start data acquisition, and correctly notify mainloop of new data and module of exceptional
	// shutdown cases (device pulled, ...).
	char *serialNumber = sshsNodeGetString(moduleData->moduleNode, "SerialNumber");
	moduleData->moduleState = caerDeviceOpen(moduleData->moduleID, CAER_DEVICE_DVS128,
		U8T(sshsNodeGetShort(moduleData->moduleNode, "BusNumber")),
		U8T(sshsNodeGetShort(moduleData->moduleNode, "DevAddress")), serialNumber);
	free(serialNumber);

	if (moduleData->moduleState == NULL) {
		// Failed to open device.
		return (false);
	}

	// Put global source information into SSHS.
	struct caer_dvs128_info devInfo = caerDVS128InfoGet(moduleData->moduleState);

	sshsNode sourceInfoNode = sshsGetRelativeNode(moduleData->moduleNode, "sourceInfo/");

	sshsNodePutShort(sourceInfoNode, "logicVersion", devInfo.logicVersion);
	sshsNodePutBool(sourceInfoNode, "deviceIsMaster", devInfo.deviceIsMaster);

	sshsNodePutShort(sourceInfoNode, "dvsSizeX", devInfo.dvsSizeX);
	sshsNodePutShort(sourceInfoNode, "dvsSizeY", devInfo.dvsSizeY);

	// Put source information for "virtual" APS frame that can be used to display and debug filter information.
	sshsNodePutShort(sourceInfoNode, "apsSizeX", devInfo.dvsSizeX);
	sshsNodePutShort(sourceInfoNode, "apsSizeY", devInfo.dvsSizeY);

	caerModuleSetSubSystemString(moduleData, devInfo.deviceString);

	// Ensure good defaults for data acquisition settings.
	// No blocking behavior due to mainloop notification, and no auto-start of
	// all producers to ensure cAER settings are respected.
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_DATAEXCHANGE,
	CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING, false);
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_DATAEXCHANGE,
	CAER_HOST_CONFIG_DATAEXCHANGE_START_PRODUCERS, false);
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_DATAEXCHANGE,
	CAER_HOST_CONFIG_DATAEXCHANGE_STOP_PRODUCERS, true);

	// Create default settings and send them to the device.
	createDefaultConfiguration(moduleData);
	sendDefaultConfiguration(moduleData);

	// Start data acquisition.
	bool ret = caerDeviceDataStart(moduleData->moduleState, &mainloopDataNotifyIncrease, &mainloopDataNotifyDecrease,
		caerMainloopGetReference(), &moduleShutdownNotify, moduleData->moduleNode);

	if (!ret) {
		// Failed to start data acquisition, close device and exit.
		caerDeviceClose((caerDeviceHandle *) &moduleData->moduleState);

		return (false);
	}

	// Add config listeners last, to avoid having them dangling if Init doesn't succeed.
	sshsNode biasNode = sshsGetRelativeNode(moduleData->moduleNode, "bias/");
	sshsNodeAddAttributeListener(biasNode, moduleData, &biasConfigListener);

	sshsNode dvsNode = sshsGetRelativeNode(moduleData->moduleNode, "dvs/");
	sshsNodeAddAttributeListener(dvsNode, moduleData, &dvsConfigListener);

	sshsNode usbNode = sshsGetRelativeNode(moduleData->moduleNode, "usb/");
	sshsNodeAddAttributeListener(usbNode, moduleData, &usbConfigListener);

	sshsNode sysNode = sshsGetRelativeNode(moduleData->moduleNode, "system/");
	sshsNodeAddAttributeListener(sysNode, moduleData, &systemConfigListener);

	return (true);
}

static void caerInputDVS128Exit(caerModuleData moduleData) {
	// Remove listener, which can reference invalid memory in userData.
	sshsNode biasNode = sshsGetRelativeNode(moduleData->moduleNode, "bias/");
	sshsNodeRemoveAttributeListener(biasNode, moduleData, &biasConfigListener);

	sshsNode dvsNode = sshsGetRelativeNode(moduleData->moduleNode, "dvs/");
	sshsNodeRemoveAttributeListener(dvsNode, moduleData, &dvsConfigListener);

	sshsNode usbNode = sshsGetRelativeNode(moduleData->moduleNode, "usb/");
	sshsNodeRemoveAttributeListener(usbNode, moduleData, &usbConfigListener);

	sshsNode sysNode = sshsGetRelativeNode(moduleData->moduleNode, "system/");
	sshsNodeRemoveAttributeListener(sysNode, moduleData, &systemConfigListener);

	caerDeviceDataStop(moduleData->moduleState);

	caerDeviceClose((caerDeviceHandle *) &moduleData->moduleState);

	if (sshsNodeGetBool(moduleData->moduleNode, "Auto-Restart")) {
		// Prime input module again so that it will try to restart if new devices detected.
		sshsNodePutBool(moduleData->moduleNode, "shutdown", false);
	}
}

static void caerInputDVS128Run(caerModuleData moduleData, size_t argsNumber, va_list args) {
	UNUSED_ARGUMENT(argsNumber);

	// Interpret variable arguments (same as above in main function).
	caerEventPacketContainer *container = va_arg(args, caerEventPacketContainer *);

	*container = caerDeviceDataGet(moduleData->moduleState);

	if (*container != NULL) {
		caerMainloopFreeAfterLoop((void (*)(void *)) &caerEventPacketContainerFree, *container);
	}
}

static void createDefaultConfiguration(caerModuleData moduleData) {
	// First, always create all needed setting nodes, set their default values
	// and add their listeners.

	// Set default biases, from DVS128Fast.xml settings.
	sshsNode biasNode = sshsGetRelativeNode(moduleData->moduleNode, "bias/");
	sshsNodePutIntIfAbsent(biasNode, "cas", 1992);
	sshsNodePutIntIfAbsent(biasNode, "injGnd", 1108364);
	sshsNodePutIntIfAbsent(biasNode, "reqPd", 16777215);
	sshsNodePutIntIfAbsent(biasNode, "puX", 8159221);
	sshsNodePutIntIfAbsent(biasNode, "diffOff", 132);
	sshsNodePutIntIfAbsent(biasNode, "req", 309590);
	sshsNodePutIntIfAbsent(biasNode, "refr", 969);
	sshsNodePutIntIfAbsent(biasNode, "puY", 16777215);
	sshsNodePutIntIfAbsent(biasNode, "diffOn", 209996);
	sshsNodePutIntIfAbsent(biasNode, "diff", 13125);
	sshsNodePutIntIfAbsent(biasNode, "foll", 271);
	sshsNodePutIntIfAbsent(biasNode, "pr", 217);

	// DVS settings.
	sshsNode dvsNode = sshsGetRelativeNode(moduleData->moduleNode, "dvs/");
	sshsNodePutBoolIfAbsent(dvsNode, "Run", true);
	sshsNodePutBoolIfAbsent(dvsNode, "TimestampReset", false);
	sshsNodePutBoolIfAbsent(dvsNode, "ArrayReset", false);

	// USB buffer settings.
	sshsNode usbNode = sshsGetRelativeNode(moduleData->moduleNode, "usb/");
	sshsNodePutIntIfAbsent(usbNode, "BufferNumber", 8);
	sshsNodePutIntIfAbsent(usbNode, "BufferSize", 4096);

	sshsNode sysNode = sshsGetRelativeNode(moduleData->moduleNode, "system/");

	// Packet settings (size (in events) and time interval (in µs)).
	sshsNodePutIntIfAbsent(sysNode, "PacketContainerMaxSize", 4096 + 128);
	sshsNodePutIntIfAbsent(sysNode, "PacketContainerMaxInterval", 5000);
	sshsNodePutIntIfAbsent(sysNode, "PolarityPacketMaxSize", 4096);
	sshsNodePutIntIfAbsent(sysNode, "PolarityPacketMaxInterval", 5000);
	sshsNodePutIntIfAbsent(sysNode, "SpecialPacketMaxSize", 128);
	sshsNodePutIntIfAbsent(sysNode, "SpecialPacketMaxInterval", 1000);

	// Ring-buffer setting (only changes value on module init/shutdown cycles).
	sshsNodePutIntIfAbsent(sysNode, "DataExchangeBufferSize", 64);
}

static void sendDefaultConfiguration(caerModuleData moduleData) {
	// Send cAER configuration to libcaer and device.
	biasConfigSend(sshsGetRelativeNode(moduleData->moduleNode, "bias/"), moduleData);
	systemConfigSend(sshsGetRelativeNode(moduleData->moduleNode, "system/"), moduleData);
	usbConfigSend(sshsGetRelativeNode(moduleData->moduleNode, "usb/"), moduleData);
	dvsConfigSend(sshsGetRelativeNode(moduleData->moduleNode, "dvs/"), moduleData);
}

static void mainloopDataNotifyIncrease(void *p) {
	caerMainloopData mainloopData = p;

	atomic_fetch_add_explicit(&mainloopData->dataAvailable, 1, memory_order_release);
}

static void mainloopDataNotifyDecrease(void *p) {
	caerMainloopData mainloopData = p;

	// No special memory order for decrease, because the acquire load to even start running
	// through a mainloop already synchronizes with the release store above.
	atomic_fetch_sub_explicit(&mainloopData->dataAvailable, 1, memory_order_relaxed);
}

static void moduleShutdownNotify(void *p) {
	sshsNode moduleNode = p;

	// Ensure parent also shuts down (on disconnected device for example).
	sshsNodePutBool(moduleNode, "shutdown", true);
}

static void biasConfigSend(sshsNode node, caerModuleData moduleData) {
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_CAS,
		U32T(sshsNodeGetInt(node, "cas")));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_INJGND,
		U32T(sshsNodeGetInt(node, "injGnd")));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_REQPD,
		U32T(sshsNodeGetInt(node, "reqPd")));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_PUX,
		U32T(sshsNodeGetInt(node, "puX")));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_DIFFOFF,
		U32T(sshsNodeGetInt(node, "diffOff")));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_REQ,
		U32T(sshsNodeGetInt(node, "req")));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_REFR,
		U32T(sshsNodeGetInt(node, "refr")));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_PUY,
		U32T(sshsNodeGetInt(node, "puY")));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_DIFFON,
		U32T(sshsNodeGetInt(node, "diffOn")));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_DIFF,
		U32T(sshsNodeGetInt(node, "diff")));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_FOLL,
		U32T(sshsNodeGetInt(node, "foll")));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_PR,
		U32T(sshsNodeGetInt(node, "pr")));
}

static void biasConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue) {
	UNUSED_ARGUMENT(node);

	caerModuleData moduleData = userData;

	if (event == ATTRIBUTE_MODIFIED) {
		if (changeType == INT && caerStrEquals(changeKey, "cas")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_CAS,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "injGnd")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_INJGND,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "reqPd")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_REQPD,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "puX")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_PUX,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "diffOff")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_DIFFOFF,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "req")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_REQ,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "refr")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_REFR,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "puY")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_PUY,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "diffOn")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_DIFFON,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "diff")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_DIFF,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "foll")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_FOLL,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "pr")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_PR,
				U32T(changeValue.iint));
		}
	}
}

static void dvsConfigSend(sshsNode node, caerModuleData moduleData) {
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_DVS, DVS128_CONFIG_DVS_ARRAY_RESET,
		sshsNodeGetBool(node, "ArrayReset"));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_DVS, DVS128_CONFIG_DVS_TIMESTAMP_RESET,
		sshsNodeGetBool(node, "TimestampReset"));
	caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_DVS, DVS128_CONFIG_DVS_RUN,
		sshsNodeGetBool(node, "Run"));
}

static void dvsConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue) {
	UNUSED_ARGUMENT(node);

	caerModuleData moduleData = userData;

	if (event == ATTRIBUTE_MODIFIED) {
		if (changeType == BOOL && caerStrEquals(changeKey, "ArrayReset")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_DVS, DVS128_CONFIG_DVS_ARRAY_RESET,
				changeValue.boolean);
		}
		else if (changeType == BOOL && caerStrEquals(changeKey, "TimestampReset")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_DVS, DVS128_CONFIG_DVS_TIMESTAMP_RESET,
				changeValue.boolean);
		}
		else if (changeType == BOOL && caerStrEquals(changeKey, "Run")) {
			caerDeviceConfigSet(moduleData->moduleState, DVS128_CONFIG_DVS, DVS128_CONFIG_DVS_RUN, changeValue.boolean);
		}
	}
}

static void usbConfigSend(sshsNode node, caerModuleData moduleData) {
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_USB, CAER_HOST_CONFIG_USB_BUFFER_NUMBER,
		U32T(sshsNodeGetInt(node, "BufferNumber")));
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_USB, CAER_HOST_CONFIG_USB_BUFFER_SIZE,
		U32T(sshsNodeGetInt(node, "BufferSize")));
}

static void usbConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue) {
	UNUSED_ARGUMENT(node);

	caerModuleData moduleData = userData;

	if (event == ATTRIBUTE_MODIFIED) {
		if (changeType == INT && caerStrEquals(changeKey, "BufferNumber")) {
			caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_USB, CAER_HOST_CONFIG_USB_BUFFER_NUMBER,
				U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "BufferSize")) {
			caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_USB, CAER_HOST_CONFIG_USB_BUFFER_SIZE,
				U32T(changeValue.iint));
		}
	}
}

static void systemConfigSend(sshsNode node, caerModuleData moduleData) {
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS, CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_SIZE,
		U32T(sshsNodeGetInt(node, "PacketContainerMaxSize")));
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS,
	CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_INTERVAL, U32T(sshsNodeGetInt(node, "PacketContainerMaxInterval")));
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS, CAER_HOST_CONFIG_PACKETS_MAX_POLARITY_SIZE,
		U32T(sshsNodeGetInt(node, "PolarityPacketMaxSize")));
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS,
	CAER_HOST_CONFIG_PACKETS_MAX_POLARITY_INTERVAL, U32T(sshsNodeGetInt(node, "PolarityPacketMaxInterval")));
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS, CAER_HOST_CONFIG_PACKETS_MAX_SPECIAL_SIZE,
		U32T(sshsNodeGetInt(node, "SpecialPacketMaxSize")));
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS,
	CAER_HOST_CONFIG_PACKETS_MAX_SPECIAL_INTERVAL, U32T(sshsNodeGetInt(node, "SpecialPacketMaxInterval")));

	// Changes only take effect on module start!
	caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_DATAEXCHANGE,
	CAER_HOST_CONFIG_DATAEXCHANGE_BUFFER_SIZE, U32T(sshsNodeGetInt(node, "DataExchangeBufferSize")));
}

static void systemConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue) {
	UNUSED_ARGUMENT(node);

	caerModuleData moduleData = userData;

	if (event == ATTRIBUTE_MODIFIED) {
		if (changeType == INT && caerStrEquals(changeKey, "PacketContainerMaxSize")) {
			caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS,
			CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_SIZE, U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "PacketContainerMaxInterval")) {
			caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS,
			CAER_HOST_CONFIG_PACKETS_MAX_CONTAINER_INTERVAL, U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "PolarityPacketMaxSize")) {
			caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS,
			CAER_HOST_CONFIG_PACKETS_MAX_POLARITY_SIZE, U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "PolarityPacketMaxInterval")) {
			caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS,
			CAER_HOST_CONFIG_PACKETS_MAX_POLARITY_INTERVAL, U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "SpecialPacketMaxSize")) {
			caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS,
			CAER_HOST_CONFIG_PACKETS_MAX_SPECIAL_SIZE, U32T(changeValue.iint));
		}
		else if (changeType == INT && caerStrEquals(changeKey, "SpecialPacketMaxInterval")) {
			caerDeviceConfigSet(moduleData->moduleState, CAER_HOST_CONFIG_PACKETS,
			CAER_HOST_CONFIG_PACKETS_MAX_SPECIAL_INTERVAL, U32T(changeValue.iint));
		}
	}
}
