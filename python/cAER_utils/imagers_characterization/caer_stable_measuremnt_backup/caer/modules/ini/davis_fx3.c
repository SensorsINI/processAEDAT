#include "davis_common.h"
#include "davis_fx3.h"

static bool caerInputDAVISFX3Init(caerModuleData moduleData);
// RUN: common to all DAVIS systems.
// CONFIG: Nothing to do here in the main thread!
// All configuration is asynchronous through SSHS listeners.
// EXIT: common to all DAVIS systems.

static struct caer_module_functions caerInputDAVISFX3Functions = { .moduleInit = &caerInputDAVISFX3Init, .moduleRun =
	&caerInputDAVISRun, .moduleConfig = NULL, .moduleExit = &caerInputDAVISExit };

caerEventPacketContainer caerInputDAVISFX3(uint16_t moduleID) {
	caerModuleData moduleData = caerMainloopFindModule(moduleID, "DAVISFX3");

	caerEventPacketContainer result = NULL;

	caerModuleSM(&caerInputDAVISFX3Functions, moduleData, 0, 1, &result);

	return (result);
}

static bool caerInputDAVISFX3Init(caerModuleData moduleData) {
	return (caerInputDAVISInit(moduleData, CAER_DEVICE_DAVIS_FX3));
}
