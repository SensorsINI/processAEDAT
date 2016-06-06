#include "net_udp.h"
#include "base/mainloop.h"
#include "base/module.h"
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

struct netUDP_state {
	int netUDPDescriptor;
	bool validOnly;
	bool excludeHeader;
	size_t maxBytesPerPacket;
	struct iovec *sgioMemory;
};

typedef struct netUDP_state *netUDPState;

static bool caerOutputNetUDPInit(caerModuleData moduleData);
static void caerOutputNetUDPRun(caerModuleData moduleData, size_t argsNumber, va_list args);
static void caerOutputNetUDPConfig(caerModuleData moduleData);
static void caerOutputNetUDPExit(caerModuleData moduleData);

static struct caer_module_functions caerOutputNetUDPFunctions = { .moduleInit = &caerOutputNetUDPInit, .moduleRun =
	&caerOutputNetUDPRun, .moduleConfig = &caerOutputNetUDPConfig, .moduleExit = &caerOutputNetUDPExit };

void caerOutputNetUDP(uint16_t moduleID, size_t outputTypesNumber, ...) {
	caerModuleData moduleData = caerMainloopFindModule(moduleID, "NetUDPOutput");

	va_list args;
	va_start(args, outputTypesNumber);
	caerModuleSMv(&caerOutputNetUDPFunctions, moduleData, sizeof(struct netUDP_state), outputTypesNumber, args);
	va_end(args);
}

static void caerOutputNetUDPConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue);

static bool caerOutputNetUDPInit(caerModuleData moduleData) {
	netUDPState state = moduleData->moduleState;

	// First, always create all needed setting nodes, set their default values
	// and add their listeners.
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "ipAddress", "127.0.0.1");
	sshsNodePutShortIfAbsent(moduleData->moduleNode, "portNumber", 8888);
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "validEventsOnly", false);
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "excludeHeader", false);
	sshsNodePutIntIfAbsent(moduleData->moduleNode, "maxBytesPerPacket", 0);

	// Open a UDP socket to the remote client, to which we'll send data packets.
	state->netUDPDescriptor = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (state->netUDPDescriptor < 0) {
		caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString, "Could not create UDP socket. Error: %d.", errno);
		return (false);
	}

	struct sockaddr_in udpClient;
	memset(&udpClient, 0, sizeof(struct sockaddr_in));

	udpClient.sin_family = AF_INET;
	udpClient.sin_port = htons(sshsNodeGetShort(moduleData->moduleNode, "portNumber"));
	char *ipAddress = sshsNodeGetString(moduleData->moduleNode, "ipAddress");
	inet_aton(ipAddress, &udpClient.sin_addr); // htonl() is implicit here.
	free(ipAddress);

	if (connect(state->netUDPDescriptor, (struct sockaddr *) &udpClient, sizeof(struct sockaddr_in)) != 0) {
		caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
			"Could not connect to remote UDP client %s:%" PRIu16 ". Error: %d.", inet_ntoa(udpClient.sin_addr),
			ntohs(udpClient.sin_port), errno);
		close(state->netUDPDescriptor);
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
	sshsNodeAddAttributeListener(moduleData->moduleNode, moduleData, &caerOutputNetUDPConfigListener);

	caerLog(CAER_LOG_INFO, moduleData->moduleSubSystemString, "UDP socket connected to %s:%" PRIu16 ".",
		inet_ntoa(udpClient.sin_addr), ntohs(udpClient.sin_port));

	return (true);
}

static void caerOutputNetUDPRun(caerModuleData moduleData, size_t argsNumber, va_list args) {
	netUDPState state = moduleData->moduleState;

	// For each output argument, write it to the UDP socket.
	// Each type has a header first thing, that gives us the length, so we can
	// cast it to that and use this information to correctly interpret it.
	for (size_t i = 0; i < argsNumber; i++) {
		caerEventPacketHeader packetHeader = va_arg(args, caerEventPacketHeader);

		// Only work if there is any content.
		if (packetHeader != NULL) {
			if ((state->validOnly && caerEventPacketHeaderGetEventValid(packetHeader) > 0)
				|| (!state->validOnly && caerEventPacketHeaderGetEventNumber(packetHeader) > 0)) {
				caerOutputCommonSend(moduleData->moduleSubSystemString, packetHeader, state->netUDPDescriptor,
					state->sgioMemory, state->validOnly, state->excludeHeader, state->maxBytesPerPacket, false);
			}
		}
	}
}

static void caerOutputNetUDPConfig(caerModuleData moduleData) {
	netUDPState state = moduleData->moduleState;

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
		// UDP client address related changes.
		// Open a UDP socket to the new remote client, to which we'll send data packets.
		int newNetUDPDescriptor = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
		if (newNetUDPDescriptor < 0) {
			caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString, "Could not create UDP socket. Error: %d.",
			errno);
			return;
		}

		struct sockaddr_in udpClient;
		memset(&udpClient, 0, sizeof(struct sockaddr_in));

		udpClient.sin_family = AF_INET;
		udpClient.sin_port = htons(sshsNodeGetShort(moduleData->moduleNode, "portNumber"));
		char *ipAddress = sshsNodeGetString(moduleData->moduleNode, "ipAddress");
		inet_aton(ipAddress, &udpClient.sin_addr); // htonl() is implicit here.
		free(ipAddress);

		if (connect(newNetUDPDescriptor, (struct sockaddr *) &udpClient, sizeof(struct sockaddr_in)) != 0) {
			caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
				"Could not connect to remote UDP client %s:%" PRIu16 ". Error: %d.", inet_ntoa(udpClient.sin_addr),
				ntohs(udpClient.sin_port), errno);
			close(newNetUDPDescriptor);
			return;
		}

		// New fd ready and connected, close old and set new.
		close(state->netUDPDescriptor);
		state->netUDPDescriptor = newNetUDPDescriptor;
	}
}

static void caerOutputNetUDPExit(caerModuleData moduleData) {
	// Remove listener, which can reference invalid memory in userData.
	sshsNodeRemoveAttributeListener(moduleData->moduleNode, moduleData, &caerOutputNetUDPConfigListener);

	netUDPState state = moduleData->moduleState;

	// Close open UDP socket.
	close(state->netUDPDescriptor);

	// Make sure to free scatter/gather IO memory.
	free(state->sgioMemory);
	state->sgioMemory = NULL;
}

static void caerOutputNetUDPConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue) {
	UNUSED_ARGUMENT(node);
	UNUSED_ARGUMENT(changeValue);

	caerModuleData data = userData;

	// Distinguish changes to the validOnly flag or to the UDP client, by setting
	// configUpdate appropriately like a bit-field.
	if (event == ATTRIBUTE_MODIFIED) {
		if (changeType == BOOL && caerStrEquals(changeKey, "validEventsOnly")) {
			atomic_fetch_or(&data->configUpdate, (0x01 << 0));
		}

		if ((changeType == STRING && caerStrEquals(changeKey, "ipAddress"))
			|| (changeType == SHORT && caerStrEquals(changeKey, "portNumber"))) {
			atomic_fetch_or(&data->configUpdate, (0x01 << 1));
		}

		if ((changeType == BOOL && caerStrEquals(changeKey, "excludeHeader"))
			|| (changeType == INT && caerStrEquals(changeKey, "maxBytesPerPacket"))) {
			atomic_fetch_or(&data->configUpdate, (0x01 << 2));
		}
	}
}
