#include "unixs.h"
#include "base/mainloop.h"
#include "base/module.h"
#include <sys/socket.h>
#include <sys/un.h>

struct unixs_state {
	int unixSocketDescriptor;
	bool validOnly;
	bool excludeHeader;
	size_t maxBytesPerPacket;
	struct iovec *sgioMemory;
};

typedef struct unixs_state *unixsState;

static bool caerOutputUnixSInit(caerModuleData moduleData);
static void caerOutputUnixSRun(caerModuleData moduleData, size_t argsNumber, va_list args);
static void caerOutputUnixSConfig(caerModuleData moduleData);
static void caerOutputUnixSExit(caerModuleData moduleData);

static struct caer_module_functions caerOutputUnixSFunctions = { .moduleInit = &caerOutputUnixSInit, .moduleRun =
	&caerOutputUnixSRun, .moduleConfig = &caerOutputUnixSConfig, .moduleExit = &caerOutputUnixSExit };

void caerOutputUnixS(uint16_t moduleID, size_t outputTypesNumber, ...) {
	caerModuleData moduleData = caerMainloopFindModule(moduleID, "UnixSocketOutput");

	va_list args;
	va_start(args, outputTypesNumber);
	caerModuleSMv(&caerOutputUnixSFunctions, moduleData, sizeof(struct unixs_state), outputTypesNumber, args);
	va_end(args);
}

static void caerOutputUnixSConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue);

static bool caerOutputUnixSInit(caerModuleData moduleData) {
	unixsState state = moduleData->moduleState;

	// First, always create all needed setting nodes, set their default values
	// and add their listeners.
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "socketPath", "/tmp/caer.sock");
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "validEventsOnly", false);
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "excludeHeader", false);
	sshsNodePutIntIfAbsent(moduleData->moduleNode, "maxBytesPerPacket", 0);

	// Open a Unix local socket on a known path, to be accessed by other processes.
	state->unixSocketDescriptor = socket(AF_UNIX, SOCK_DGRAM, 0);
	if (state->unixSocketDescriptor < 0) {
		caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString, "Could not create local Unix socket. Error: %d.",
		errno);
		return (false);
	}

	struct sockaddr_un unixSocketAddr;
	memset(&unixSocketAddr, 0, sizeof(struct sockaddr_un));

	unixSocketAddr.sun_family = AF_UNIX;
	char *socketPath = sshsNodeGetString(moduleData->moduleNode, "socketPath");
	strncpy(unixSocketAddr.sun_path, socketPath, sizeof(unixSocketAddr.sun_path) - 1);
	free(socketPath);

	// Connect socket to above address.
	if (connect(state->unixSocketDescriptor, (struct sockaddr *) &unixSocketAddr, sizeof(struct sockaddr_un)) < 0) {
		caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
			"Could not connect to local Unix socket. Error: %d.", errno);
		close(state->unixSocketDescriptor);
		return (false);
	}

	// Set valid events flag, and allocate memory for scatter/gather IO for it.
	state->validOnly = sshsNodeGetBool(moduleData->moduleNode, "validEventsOnly");
	state->excludeHeader = sshsNodeGetBool(moduleData->moduleNode, "excludeHeader");
	state->maxBytesPerPacket = (size_t) sshsNodeGetInt(moduleData->moduleNode, "maxBytesPerPacket");

	if (state->validOnly) {
		state->sgioMemory = calloc(IOVEC_SIZE, sizeof(struct iovec));
		if (state->sgioMemory == NULL) {
			caerLog(CAER_LOG_ALERT, moduleData->moduleSubSystemString,
				"Impossible to allocate memory for scatter/gather IO, using memory copy method.");
		}
		else {
			caerLog(CAER_LOG_INFO, moduleData->moduleSubSystemString,
				"Using scatter/gather IO for outputting valid events only.");
		}
	}
	else {
		state->sgioMemory = NULL;
	}

	// Add config listeners last, to avoid having them dangling if Init doesn't succeed.
	sshsNodeAddAttributeListener(moduleData->moduleNode, moduleData, &caerOutputUnixSConfigListener);

	caerLog(CAER_LOG_INFO, moduleData->moduleSubSystemString, "Local Unix socket ready at %s.",
		unixSocketAddr.sun_path);

	return (true);
}

static void caerOutputUnixSRun(caerModuleData moduleData, size_t argsNumber, va_list args) {
	unixsState state = moduleData->moduleState;

	// For each output argument, write it to the local Unix socket.
	// Each type has a header first thing, that gives us the length, so we can
	// cast it to that and use this information to correctly interpret it.
	for (size_t i = 0; i < argsNumber; i++) {
		caerEventPacketHeader packetHeader = va_arg(args, caerEventPacketHeader);

		// Only work if there is any content.
		if (packetHeader != NULL) {
			if ((state->validOnly && caerEventPacketHeaderGetEventValid(packetHeader) > 0)
				|| (!state->validOnly && caerEventPacketHeaderGetEventNumber(packetHeader) > 0)) {
				caerOutputCommonSend(moduleData->moduleSubSystemString, packetHeader, state->unixSocketDescriptor,
					state->sgioMemory, state->validOnly, state->excludeHeader, state->maxBytesPerPacket, false);
			}
		}
	}
}

static void caerOutputUnixSConfig(caerModuleData moduleData) {
	unixsState state = moduleData->moduleState;

	// Get the current value to examine by atomic exchange, since we don't
	// want there to be any possible store between a load/store pair.
	uintptr_t configUpdate = atomic_exchange(&moduleData->configUpdate, 0);

	if (configUpdate & (0x01 << 0)) {
		// validOnly flag changed.
		bool validOnlyFlag = sshsNodeGetBool(moduleData->moduleNode, "validEventsOnly");

		// Only react if the actual state differs from the wanted one.
		if (state->validOnly != validOnlyFlag) {
			// If we want it, turn it on.
			if (validOnlyFlag) {
				state->validOnly = true;

				state->sgioMemory = calloc(IOVEC_SIZE, sizeof(struct iovec));
				if (state->sgioMemory == NULL) {
					caerLog(CAER_LOG_ALERT, moduleData->moduleSubSystemString,
						"Impossible to allocate memory for scatter/gather IO, using memory copy method.");
				}
				else {
					caerLog(CAER_LOG_INFO, moduleData->moduleSubSystemString,
						"Using scatter/gather IO for outputting valid events only.");
				}
			}
			else {
				// Else disable it.
				state->validOnly = false;

				free(state->sgioMemory);
				state->sgioMemory = NULL;
			}
		}
	}

	if (configUpdate & (0x01 << 2)) {
		state->excludeHeader = sshsNodeGetBool(moduleData->moduleNode, "excludeHeader");
		state->maxBytesPerPacket = (size_t) sshsNodeGetInt(moduleData->moduleNode, "maxBytesPerPacket");
	}

	if (configUpdate & (0x01 << 1)) {
		// Local Unix socket path changed.
		// Open a local Unix socket on the new supplied path.
		int newUnixSocketDescriptor = socket(AF_UNIX, SOCK_DGRAM, 0);
		if (newUnixSocketDescriptor < 0) {
			caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
				"Could not create local Unix socket. Error: %d.", errno);
			return;
		}

		struct sockaddr_un unixSocketAddr;
		memset(&unixSocketAddr, 0, sizeof(struct sockaddr_un));

		unixSocketAddr.sun_family = AF_UNIX;
		char *socketPath = sshsNodeGetString(moduleData->moduleNode, "socketPath");
		strncpy(unixSocketAddr.sun_path, socketPath, sizeof(unixSocketAddr.sun_path) - 1);
		free(socketPath);

		// Connect socket to above address.
		if (connect(newUnixSocketDescriptor, (struct sockaddr *) &unixSocketAddr, sizeof(struct sockaddr_un)) < 0) {
			caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
				"Could not connect to local Unix socket. Error: %d.", errno);
			close(newUnixSocketDescriptor);
			return;
		}

		// New fd ready and connected, close old and set new.
		close(state->unixSocketDescriptor);
		state->unixSocketDescriptor = newUnixSocketDescriptor;
	}
}

static void caerOutputUnixSExit(caerModuleData moduleData) {
	// Remove listener, which can reference invalid memory in userData.
	sshsNodeRemoveAttributeListener(moduleData->moduleNode, moduleData, &caerOutputUnixSConfigListener);

	unixsState state = moduleData->moduleState;

	// Close open local Unix socket.
	close(state->unixSocketDescriptor);

	// Make sure to free scatter/gather IO memory.
	free(state->sgioMemory);
	state->sgioMemory = NULL;
}

static void caerOutputUnixSConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue) {
	UNUSED_ARGUMENT(node);
	UNUSED_ARGUMENT(changeValue);

	caerModuleData data = userData;

	// Distinguish changes to the validOnly flag or to Unix socket path, by setting
	// configUpdate appropriately like a bit-field.
	if (event == ATTRIBUTE_MODIFIED) {
		if (changeType == BOOL && caerStrEquals(changeKey, "validEventsOnly")) {
			atomic_fetch_or(&data->configUpdate, (0x01 << 0));
		}

		if (changeType == STRING && caerStrEquals(changeKey, "socketPath")) {
			atomic_fetch_or(&data->configUpdate, (0x01 << 1));
		}

		if ((changeType == BOOL && caerStrEquals(changeKey, "excludeHeader"))
			|| (changeType == INT && caerStrEquals(changeKey, "maxBytesPerPacket"))) {
			atomic_fetch_or(&data->configUpdate, (0x01 << 2));
		}
	}
}
