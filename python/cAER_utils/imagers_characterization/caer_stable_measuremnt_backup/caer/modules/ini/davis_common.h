#ifndef DAVIS_COMMON_H_
#define DAVIS_COMMON_H_

#include "main.h"
#include "base/mainloop.h"
#include "base/module.h"

#include <libcaer/devices/davis.h>

bool caerInputDAVISInit(caerModuleData moduleData, uint16_t deviceType);
void caerInputDAVISExit(caerModuleData moduleData);
void caerInputDAVISRun(caerModuleData moduleData, size_t argsNumber, va_list args);

#endif /* DAVIS_COMMON_H_ */
