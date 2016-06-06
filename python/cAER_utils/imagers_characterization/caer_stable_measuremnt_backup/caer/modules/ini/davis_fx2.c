#include "davis_common.h"
#include "davis_fx2.h"

static bool caerInputDAVISFX2Init(caerModuleData moduleData);
// RUN: common to all DAVIS systems.
// CONFIG: Nothing to do here in the main thread!
// All configuration is asynchronous through SSHS listeners.
// EXIT: common to all DAVIS systems.

static struct caer_module_functions caerInputDAVISFX2Functions = { .moduleInit = &caerInputDAVISFX2Init, .moduleRun =
	&caerInputDAVISRun, .moduleConfig = NULL, .moduleExit = &caerInputDAVISExit };

caerEventPacketContainer caerInputDAVISFX2(uint16_t moduleID) {
	caerModuleData moduleData = caerMainloopFindModule(moduleID, "DAVISFX2");

	caerEventPacketContainer result = NULL;

	caerModuleSM(&caerInputDAVISFX2Functions, moduleData, 0, 1, &result);

	return (result);
}

static bool caerInputDAVISFX2Init(caerModuleData moduleData) {
	return (caerInputDAVISInit(moduleData, CAER_DEVICE_DAVIS_FX2));
}
