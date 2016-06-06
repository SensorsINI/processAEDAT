/*
 * in_net_tcp_server.c
 *
 *  Created on: Nov 6, 2015
 *      Author: brandli, insightness
 */

#include "in_net_tcp_server.h"
#include "base/module.h"
#include <poll.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include "ext/nets.h"

struct in_netTCP_state {
	int serverDescriptor;
	struct pollfd *clientDescriptor;
	struct iovec *sgioMemory;
	bool connected;
	atomic_bool stop; // stop flag for input module
	atomic_bool stopInput; // stop flag for input thread - can be toggled multiple times during the lifetime of the input module
	thrd_t inputReadThread;
	bool keepLatestContainer; //if true: every time the main loop is executed, the network input module "publishes" the latest container it received
	bool waitForFullContainer; //if true: the input module waits with publishing a container until it received two packets of the same type (= buffer depth 1)
	bool notifyMainLoop; //if true: every time a packet is received the mainloop gets notified to be executed (useful if network input module the main event source)
	void (*dataNotifyIncrease)(void *ptr);
	void (*dataNotifyDecrease)(void *ptr);
	void *dataNotifyUserPtr;
	caerEventPacketContainer currentContainer;
};

typedef struct in_netTCP_state *netTCPState;

static bool caerInputNetTCPServerInit(caerModuleData moduleData);
static void caerInputNetTCPServerRun(caerModuleData moduleData, size_t argsNumber, va_list args);
static void caerInputNetTCPServerConfig(caerModuleData moduleData);
static void caerInputNetTCPServerExit(caerModuleData moduleData);
static int inputFromSocketThread(void* ptr);
static bool createTcpInputServer(caerModuleData moduleData);
static bool checkTcpInputConnections(caerModuleData moduleData);

static struct caer_module_functions caerInputNetTCPServerFunctions = { .moduleInit = &caerInputNetTCPServerInit,
	.moduleRun = &caerInputNetTCPServerRun, .moduleConfig = &caerInputNetTCPServerConfig, .moduleExit =
		&caerInputNetTCPServerExit };

caerEventPacketContainer caerInputNetTCPServer(uint16_t moduleID) {
	caerModuleData moduleData = caerMainloopFindModule(moduleID, "NetTCPServerInput");

	caerEventPacketContainer result = NULL;

	caerModuleSM(&caerInputNetTCPServerFunctions, moduleData, sizeof(struct in_netTCP_state), 1, &result);

	return ((caerEventPacketContainer) result);
}

static void caerInputNetTCPServerConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue) {
	UNUSED_ARGUMENT(node);
	UNUSED_ARGUMENT(changeValue);

	caerModuleData data = userData;

	// Distinguish changes to the validOnly flag or to the TCP server, by setting
	// configUpdate appropriately like a bit-field.
	if (event == ATTRIBUTE_MODIFIED) {
		if (changeType == BOOL && caerStrEquals(changeKey, "validEventsOnly")) {
			atomic_fetch_or(&data->configUpdate, (0x01 << 0));
		}

		if ((changeType == STRING && caerStrEquals(changeKey, "ipAddress"))
			|| (changeType == SHORT && caerStrEquals(changeKey, "portNumber"))) {
			atomic_fetch_or(&data->configUpdate, (0x01 << 1));
		}

		if (changeType == SHORT && caerStrEquals(changeKey, "concurrentConnections")) {
			atomic_fetch_or(&data->configUpdate, (0x01 << 2));
		}

		if ((changeType == BOOL && caerStrEquals(changeKey, "excludeHeader"))
			|| (changeType == INT && caerStrEquals(changeKey, "maxBytesPerPacket"))) {
			atomic_fetch_or(&data->configUpdate, (0x01 << 3));
		}
	}
}

static bool caerInputNetTCPServerInit(caerModuleData moduleData) {
	netTCPState state = moduleData->moduleState;

	// First, always create all needed setting nodes, set their default values
	// and add their listeners.
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "ipAddress", "127.0.0.1");
	sshsNodePutShortIfAbsent(moduleData->moduleNode, "portNumber", 7778);
	sshsNodePutShortIfAbsent(moduleData->moduleNode, "backlogSize", 5);
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "notifyMainLoop", true);
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "keepLatestContainer", false);
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "waitForFullContainer", false);

	state->stop = false;
	state->connected = false;
	state->stopInput = false;

	state->notifyMainLoop = sshsNodeGetBool(moduleData->moduleNode, "notifyMainLoop");
	state->keepLatestContainer = sshsNodeGetBool(moduleData->moduleNode, "keepLatestContainer");
	state->waitForFullContainer = sshsNodeGetBool(moduleData->moduleNode, "waitForFullContainer");
	// set notifier
	state->dataNotifyDecrease = &mainloopDataNotifyDecrease;
	state->dataNotifyIncrease = &mainloopDataNotifyIncrease;
	state->dataNotifyUserPtr = caerMainloopGetReference();
	// start thread
	if ((errno = thrd_create(&state->inputReadThread, &inputFromSocketThread, moduleData)) != thrd_success) {
		free(state->currentContainer);
		caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
			"Failed to start data acquisition thread. Error: %d.",
			errno);
	}

	// Add config listeners last, to avoid having them dangling if Init doesn't succeed.
	sshsNodeAddAttributeListener(moduleData->moduleNode, moduleData, &caerInputNetTCPServerConfigListener);

	return (true);
}

static void caerInputNetTCPServerRun(caerModuleData moduleData, size_t argsNumber, va_list args) {
	UNUSED_ARGUMENT(argsNumber);

//	caerLog(CAER_LOG_INFO, moduleData->moduleSubSystemString, "in caerInputNetTCPServerRun");

	// Update the current connections on which to receive data.
	netTCPState state = moduleData->moduleState;

	//check whether the thread is stopped because the connection is broken and restart thread if this is the case
	if (atomic_load(&state->stopInput) && !atomic_load(&state->stop)) {
		if (state->connected) {
			caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
				"TCP input interface in strange state with connected socket but stopped data acquisition thread");
		}
		else {
			caerLog(CAER_LOG_INFO, moduleData->moduleSubSystemString, "Reconnecting");
			atomic_store(&state->stopInput, false);
			if ((errno = thrd_create(&state->inputReadThread, &inputFromSocketThread, moduleData)) != thrd_success) {
				free(state->currentContainer);
				caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
					"Failed to start data acquisition thread. Error: %d.",
					errno);
			}
		}
	}

	// Interpret variable arguments (same as above in main function).
	caerEventPacketContainer* container = va_arg(args, caerEventPacketContainer*);

	*container = state->currentContainer;

	if (*container != NULL) {
		if (state->notifyMainLoop) {
			state->dataNotifyDecrease(state->dataNotifyUserPtr);
		}
		if (!state->keepLatestContainer) {
			state->currentContainer = NULL;
			caerMainloopFreeAfterLoop((void (*)(void*)) &caerEventPacketContainerFree, *container);
		}
	}
	return;
}

static void caerInputNetTCPServerConfig(caerModuleData moduleData) {
	netTCPState state = moduleData->moduleState;

	// Get the current value to examine by atomic exchange, since we don't
	// want there to be any possible store between a load/store pair.
	uintptr_t configUpdate = atomic_exchange(&moduleData->configUpdate, 0);

	if (configUpdate & (0x01 << 1)) {
		// TCP server address related changes.
		// Changes to the backlogSize parameter are only ever considered when
		// fully opening a new socket, which happens only on changes to either
		// the server IP address or its port.

		// Tell the input thread to stop. Main thread waits until it stopped
		atomic_store(&state->stopInput, true);
		int* res = malloc(sizeof(int));
		thrd_join(state->inputReadThread, res);
		atomic_store(&state->stopInput, false);

		close(state->serverDescriptor);

		// start thread
		if ((errno = thrd_create(&state->inputReadThread, &inputFromSocketThread, moduleData)) != thrd_success) {
			free(state->currentContainer);
			caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
				"Failed to start data acquisition thread. Error: %d.",
				errno);
		}
	}
}

static void caerInputNetTCPServerExit(caerModuleData moduleData) {
	// Remove listener, which can reference invalid memory in userData.
	sshsNodeRemoveAttributeListener(moduleData->moduleNode, moduleData, &caerInputNetTCPServerConfigListener);

	netTCPState state = moduleData->moduleState;

	// Tell the input thread to stop. Main thread waits until it stopped
	atomic_store(&state->stopInput, true);
	int* res = malloc(sizeof(int));
	thrd_join(state->inputReadThread, res);
	atomic_store(&state->stop, true);
	atomic_store(&state->stopInput, false);

	// Close all open connections to clients.
	if (state->clientDescriptor->fd >= 0) {
		close(state->clientDescriptor->fd);
		state->clientDescriptor->fd = -1;
	}

	// Free memory associated with the client descriptors.
	free(state->clientDescriptor);
	state->clientDescriptor = NULL;

	// Close open TCP server socket.
	close(state->serverDescriptor);

	// Make sure to free scatter/gather IO memory.
	free(state->sgioMemory);
	state->sgioMemory = NULL;

	// Clear current packet
	free(state->currentContainer);
	state->currentContainer = NULL;
}

static int inputFromSocketThread(void* ptr) {
	caerLog(CAER_LOG_INFO, "caerInputNetTCPServerThread", "Socket thread started");

	caerModuleData moduleData = ptr;
	netTCPState state = moduleData->moduleState;
	int16_t IDSource = (int16_t) moduleData->moduleID;
	bool notifyMain = sshsNodeGetBool(moduleData->moduleNode, "notifyMainLoop");

	if (!createTcpInputServer(moduleData)) {

	}
	caerLog(CAER_LOG_INFO, "caerInputNetTCPServerThread", "Socket created ... waiting for connection");
	while (!state->connected) {
		if (atomic_load(&state->stopInput)) {
			caerLog(CAER_LOG_INFO, "caerInputNetTCPServerThread", "Input thread stopped");
			close(state->serverDescriptor);
			state->connected = false;
			thrd_exit(thrd_success);
		}
		state->connected = checkTcpInputConnections(moduleData);
	}
	caerLog(CAER_LOG_INFO, "caerInputNetTCPServerThread", "Connected ... waiting for data");
	// remainder packet, used to identify the moment to send a container. Read in first packet.
	caerEventPacketHeader packetHeader = NULL;
	int16_t maxSizeContainer = 5;

	// allocate container
	caerEventPacketContainer inputContainer = caerEventPacketContainerAllocate(maxSizeContainer);
	// useful variables
	int16_t currType;

	while (1) {
		// read next packet
		// make sure thread should still be running
		if (atomic_load(&state->stopInput)) {
			free(packetHeader);
			caerEventPacketContainerFree(inputContainer);
			caerLog(CAER_LOG_INFO, "caerInputNetTCPServerThread", "Input thread stopped");
			close(state->serverDescriptor);
			state->connected = false;
			thrd_exit(thrd_success);
		}
		int fid = state->clientDescriptor->fd;
		packetHeader = caerInputCommonReadPacket(fid);
		if (packetHeader == NULL) {
			//connection broken -> kill thread and restart from run
			state->connected = false;
			caerEventPacketContainerFree(inputContainer);
			atomic_store(&state->stopInput, true);
			caerLog(CAER_LOG_INFO, "caerInputNetTCPServerThread", "Input thread stopped");
			close(state->serverDescriptor);
			state->connected = false;
			thrd_exit(thrd_success);
		}
		caerLog(CAER_LOG_INFO, "caerInputNetTCPServer", "Packet received. Size: %d", packetHeader->eventNumber);
		caerEventPacketHeaderSetEventSource(packetHeader, IDSource);

		currType = caerEventPacketHeaderGetEventType(packetHeader);

		//make sure container is big enough for packet type
		if (currType >= maxSizeContainer) {
			// new container and transfer the content, adding the new packet
			caerEventPacketContainer newContainer = caerEventPacketContainerAllocate(currType + 1);
			for (int16_t i = 0; i < maxSizeContainer; ++i) {
				caerEventPacketContainerSetEventPacket(newContainer, i,
					caerEventPacketContainerGetEventPacket(inputContainer, i));
			}
			free(inputContainer);
			inputContainer = newContainer;
			// update max size
			maxSizeContainer = I16T(currType + 1);
		}
		if (!state->waitForFullContainer) {
			caerEventPacketContainerSetEventPacket(inputContainer, currType, packetHeader);
			packetHeader = NULL;
		}
		if (!state->waitForFullContainer || caerEventPacketContainerGetEventPacket(inputContainer, currType) != NULL) {
			//container needs to be pushed to main loop
			//remove old container
			if (state->currentContainer != NULL) {
				free(state->currentContainer);
			}
			state->currentContainer = inputContainer;
			if (notifyMain) {
				state->dataNotifyIncrease(state->dataNotifyUserPtr);
			}
			// create new container
			inputContainer = caerEventPacketContainerAllocate(maxSizeContainer);
		}
		if (state->waitForFullContainer) {
			// if only full containers can be sent out, the packet can only be added once it is sure that it should not be sent out before
			caerEventPacketContainerSetEventPacket(inputContainer, currType, packetHeader);
			packetHeader = NULL;
		}
	}

	caerLog(CAER_LOG_INFO, "caerInputNetTCPServer", "Socket thread ended");

	// push the new container to the ringbuffer
	thrd_exit(thrd_success);
}

static bool createTcpInputServer(caerModuleData moduleData) {
	netTCPState state = moduleData->moduleState;

	// Open a TCP server socket for others to connect to.
	state->serverDescriptor = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (state->serverDescriptor < 0) {
		caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString, "Could not create TCP server socket. Error: %d.",
		errno);
		return (false);
	}

	// Make socket address reusable right away.
	if (!socketReuseAddr(state->serverDescriptor, true)) {
		caerLog(CAER_LOG_CRITICAL, "caerInputNetTCPServerThread", "Could not set TCP server socket to reusable.");
		close(state->serverDescriptor);
		return (false);
	}

	// Set server socket, on which accept() is called, to non-blocking mode.
	if (!socketBlockingMode(state->serverDescriptor, false)) {
		caerLog(CAER_LOG_CRITICAL, "caerInputNetTCPServerThread",
			"Could not set TCP server socket to non-blocking mode.");
		close(state->serverDescriptor);
		return (false);
	}

	struct sockaddr_in tcpServer;
	memset(&tcpServer, 0, sizeof(struct sockaddr_in));

	tcpServer.sin_family = AF_INET;
	tcpServer.sin_port = htons(sshsNodeGetShort(moduleData->moduleNode, "portNumber"));
	char *ipAddress = sshsNodeGetString(moduleData->moduleNode, "ipAddress");
	inet_aton(ipAddress, &tcpServer.sin_addr); // htonl() is implicit here.
	free(ipAddress);

	// Bind socket to above address.
	if (bind(state->serverDescriptor, (struct sockaddr *) &tcpServer, sizeof(struct sockaddr_in)) < 0) {
		caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString, "Could not bind TCP server socket. Error: %d.",
		errno);
		close(state->serverDescriptor);
		return (false);
	}

	// Listen to new connections on the socket.
	if (listen(state->serverDescriptor, sshsNodeGetShort(moduleData->moduleNode, "backlogSize")) < 0) {
		caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
			"Could not listen on TCP server socket. Error: %d.", errno);
		close(state->serverDescriptor);
		return (false);
	}

	// Prepare memory to hold connected clients fds.
	state->clientDescriptor = malloc(sizeof(state->clientDescriptor));
	if (state->clientDescriptor == NULL) {
		caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
			"Could not allocate memory for TCP client descriptor. Error: %d.", errno);
		close(state->serverDescriptor);
		return (false);
	}

	// Initialize connected clients array to empty.
	state->clientDescriptor->fd = -1;

	caerLog(CAER_LOG_INFO, moduleData->moduleSubSystemString, "TCP input server socket connected to %s:%" PRIu16 ".",
		inet_ntoa(tcpServer.sin_addr), ntohs(tcpServer.sin_port));

	return (true);
}

static bool checkTcpInputConnections(caerModuleData moduleData) {
	netTCPState state = moduleData->moduleState;
	int pollResult = poll(state->clientDescriptor, 1, 0);
	if (pollResult < 0) {
		// Poll failure. Log and then continue.
		caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString, "TCP server poll() failed. Error: %d.", errno);
	}

	// let's see if any new connections are waiting on the listening socket to be accepted.
	int acceptResult = accept(state->serverDescriptor, NULL, NULL);
	if (acceptResult < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
		// Accept failure (but not would-block error). Log and then continue.
		caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString, "TCP server accept() failed. Error: %d.", errno);
	}

	// New connection present!
	if (acceptResult >= 0) {
		state->clientDescriptor->fd = acceptResult;
		caerLog(CAER_LOG_DEBUG, moduleData->moduleSubSystemString, "Accepted new TCP connection from client (fd %d).",
			acceptResult);
		return (true);
	}
	else {
		return (false);
	}
}
