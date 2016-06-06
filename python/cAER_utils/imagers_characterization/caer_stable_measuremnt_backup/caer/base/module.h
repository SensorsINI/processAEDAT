/*
 * module.h
 *
 *  Created on: Dec 14, 2013
 *      Author: chtekk
 */

#ifndef MODULE_H_
#define MODULE_H_

#include "main.h"
#include "ext/uthash/uthash.h"
#include <stdarg.h>
#include <stdatomic.h>

// Module-related definitions.
enum caer_module_status {
	STOPPED = 0, RUNNING = 1,
};

struct caer_module_data {
	UT_hash_handle hh;
	uint16_t moduleID;
	sshsNode moduleNode;
	enum caer_module_status moduleStatus;
	atomic_bool running;
	atomic_uint_fast32_t configUpdate;
	void *moduleState;
	char *moduleSubSystemString;
};

typedef struct caer_module_data *caerModuleData;

struct caer_module_functions {
	bool (* const moduleInit)(caerModuleData moduleData); // Can be NULL.
	void (* const moduleRun)(caerModuleData moduleData, size_t argsNumber, va_list args);
	void (* const moduleConfig)(caerModuleData moduleData); // Can be NULL.
	void (* const moduleExit)(caerModuleData moduleData); // Can be NULL.
};

typedef struct caer_module_functions const * const caerModuleFunctions;

void caerModuleSM(caerModuleFunctions moduleFunctions, caerModuleData moduleData, size_t memSize, size_t argsNumber,
	...);
void caerModuleSMv(caerModuleFunctions moduleFunctions, caerModuleData moduleData, size_t memSize, size_t argsNumber,
	va_list args);
caerModuleData caerModuleInitialize(uint16_t moduleID, const char *moduleShortName, sshsNode mainloopNode);
bool caerModuleSetSubSystemString(caerModuleData moduleData, const char *subSystemString);
void caerModuleDestroy(caerModuleData moduleData);
void caerModuleConfigUpdateReset(caerModuleData moduleData);
void caerModuleConfigDefaultListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue);

#endif /* MODULE_H_ */
