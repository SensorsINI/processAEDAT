#include "config_server.h"
#include <stdatomic.h>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include "ext/nets.h"

#ifdef HAVE_PTHREADS
	#include "ext/c11threads_posix.h"
#endif

static struct {
	atomic_bool running;
	thrd_t thread;
} configServerThread;

static int caerConfigServerRunner(void *inPtr);
static void caerConfigServerHandleRequest(int connectedClientSocket, uint8_t action, uint8_t type, const uint8_t *extra,
	size_t extraLength, const uint8_t *node, size_t nodeLength, const uint8_t *key, size_t keyLength,
	const uint8_t *value, size_t valueLength);

void caerConfigServerStart(void) {
	// Enable the configuration server thread.
	atomic_store(&configServerThread.running, true);

	// Start the thread.
	if ((errno = thrd_create(&configServerThread.thread, &caerConfigServerRunner, NULL)) == thrd_success) {
		// Successfully started thread.
		caerLog(CAER_LOG_DEBUG, "Config Server", "Thread created successfully.");
	}
	else {
		// Failed to create thread.
		caerLog(CAER_LOG_EMERGENCY, "Config Server", "Failed to create thread. Error: %d.", errno);
		exit(EXIT_FAILURE);
	}
}

void caerConfigServerStop(void) {
	// Only execute if the server thread was actually started.
	if (!atomic_load_explicit(&configServerThread.running, memory_order_relaxed)) {
		return;
	}

	// Disable the configuration server thread first.
	atomic_store(&configServerThread.running, false);

	// Then wait on it to finish.
	if ((errno = thrd_join(configServerThread.thread, NULL)) == thrd_success) {
		// Successfully joined thread.
		caerLog(CAER_LOG_DEBUG, "Config Server", "Thread terminated successfully.");
	}
	else {
		// Failed to join thread.
		caerLog(CAER_LOG_EMERGENCY, "Config Server", "Failed to terminate thread. Error: %d.", errno);
		exit(EXIT_FAILURE);
	}
}

static int caerConfigServerRunner(void *inPtr) {
	UNUSED_ARGUMENT(inPtr);

	// Get the right configuration node first.
	sshsNode serverNode = sshsGetNode(sshsGetGlobal(), "/server/");

	// Ensure default values are present.
	sshsNodePutStringIfAbsent(serverNode, "ipAddress", "127.0.0.1");
	sshsNodePutIntIfAbsent(serverNode, "portNumber", 4040);
	sshsNodePutShortIfAbsent(serverNode, "backlogSize", 5);
	sshsNodePutShortIfAbsent(serverNode, "concurrentConnections", 5);

	// Open a TCP server socket for configuration handling.
	// TCP chosen for reliability, which is more important here than speed.
	int configServerSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (configServerSocket < 0) {
		caerLog(CAER_LOG_CRITICAL, "Config Server", "Could not create server socket. Error: %d.", errno);
		return (EXIT_FAILURE);
	}

	// Make socket address reusable right away.
	socketReuseAddr(configServerSocket, true);

	struct sockaddr_in configServerAddress;
	memset(&configServerAddress, 0, sizeof(struct sockaddr_in));

	configServerAddress.sin_family = AF_INET;
	configServerAddress.sin_port = htons(U16T(sshsNodeGetInt(serverNode, "portNumber")));
	char *ipAddress = sshsNodeGetString(serverNode, "ipAddress");
	inet_aton(ipAddress, &configServerAddress.sin_addr); // htonl() is implicit here.
	free(ipAddress);

	// Bind socket to above address.
	if (bind(configServerSocket, (struct sockaddr *) &configServerAddress, sizeof(struct sockaddr_in)) < 0) {
		caerLog(CAER_LOG_CRITICAL, "Config Server", "Could not bind server socket. Error: %d.", errno);
		return (EXIT_FAILURE);
	}

	// Listen to new connections on the socket.
	if (listen(configServerSocket, sshsNodeGetShort(serverNode, "backlogSize")) < 0) {
		caerLog(CAER_LOG_CRITICAL, "Config Server", "Could not listen on server socket. Error: %d.", errno);
		return (EXIT_FAILURE);
	}

	// Control message format: 1 byte ACTION, 1 byte TYPE, 2 bytes EXTRA_LEN,
	// 2 bytes NODE_LEN, 2 bytes KEY_LEN, 2 bytes VALUE_LEN, then up to 4086
	// bytes split between EXTRA, NODE, KEY, VALUE (with 4 bytes for NUL).
	// Basically: (EXTRA_LEN + NODE_LEN + KEY_LEN + VALUE_LEN) <= 4086.
	// EXTRA, NODE, KEY, VALUE have to be NUL terminated, and their length
	// must include the NUL termination byte.
	// This results in a maximum message size of 4096 bytes (4KB).
	uint8_t configServerBuffer[4096];

	caerLog(CAER_LOG_NOTICE, "Config Server", "Ready and listening on %s:%" PRIu16 ".",
		inet_ntoa(configServerAddress.sin_addr), ntohs(configServerAddress.sin_port));

	size_t connections = (size_t) sshsNodeGetShort(serverNode, "concurrentConnections") + 1;// +1 for listening socket.

	struct pollfd pollSockets[connections];

	// Initially ignore all pollfds, and react only to POLLIN events.
	for (size_t i = 0; i < connections; i++) {
		pollSockets[i].fd = -1;
		pollSockets[i].events = POLLIN;
	}

	// First pollfd is the listening socket, always.
	pollSockets[0].fd = configServerSocket;

	while (atomic_load_explicit(&configServerThread.running, memory_order_relaxed)) {
		int pollResult = poll(pollSockets, (nfds_t) connections, 1000);

		if (pollResult > 0) {
			// First let's check if there's a new connection waiting to be accepted.
			if ((pollSockets[0].revents & POLLIN) != 0) {
				int newClientSocket = accept(pollSockets[0].fd, NULL, NULL);

				if (newClientSocket >= 0) {
					// Put it in the list of watched fds if possible, or close.
					bool putInFDList = false;

					for (size_t i = 1; i < connections; i++) {
						if (pollSockets[i].fd == -1) {
							// Empty place in watch list, add this one.
							pollSockets[i].fd = newClientSocket;
							putInFDList = true;
							break;
						}
					}

					// No space for new connection, just close it (client will exit).
					if (!putInFDList) {
						close(newClientSocket);
						caerLog(CAER_LOG_DEBUG, "Config Server", "Rejected client (fd %d), queue full.",
							newClientSocket);
					}
					else {
						caerLog(CAER_LOG_DEBUG, "Config Server", "Accepted new connection from client (fd %d).",
							newClientSocket);
					}
				}
			}

			for (size_t i = 1; i < connections; i++) {
				// Work on existing connections, valid and with read events.
				if (pollSockets[i].fd != -1 && (pollSockets[i].revents & POLLIN) != 0) {
					// Accepted client connection, let's get all the data we need: first
					// the 10 byte header, and then whatever remains based on that.
					if (!recvUntilDone(pollSockets[i].fd, configServerBuffer, 10)) {
						// Closed on other side or error. Let's just close here too.
						close(pollSockets[i].fd);

						caerLog(CAER_LOG_DEBUG, "Config Server", "Disconnected client on recv (fd %d).",
							pollSockets[i].fd);
						pollSockets[i].fd = -1;

						continue;
					}

					// Decode header fields (all in little-endian).
					uint8_t action = configServerBuffer[0];
					uint8_t type = configServerBuffer[1];
					uint16_t extraLength = le16toh(*(uint16_t * )(configServerBuffer + 2));
					uint16_t nodeLength = le16toh(*(uint16_t * )(configServerBuffer + 4));
					uint16_t keyLength = le16toh(*(uint16_t * )(configServerBuffer + 6));
					uint16_t valueLength = le16toh(*(uint16_t * )(configServerBuffer + 8));

					// Total length to get for command.
					size_t readLength = (size_t) (extraLength + nodeLength + keyLength + valueLength);

					if (!recvUntilDone(pollSockets[i].fd, configServerBuffer + 10, readLength)) {
						// Closed on other side or error. Let's just close here too.
						close(pollSockets[i].fd);

						caerLog(CAER_LOG_DEBUG, "Config Server", "Disconnected client on recv (fd %d).",
							pollSockets[i].fd);
						pollSockets[i].fd = -1;

						continue;
					}

					// Now we have everything. The header fields are already
					// fully decoded: handle request (and send back data eventually).
					caerConfigServerHandleRequest(pollSockets[i].fd, action, type, configServerBuffer + 10, extraLength,
						configServerBuffer + 10 + extraLength, nodeLength,
						configServerBuffer + 10 + extraLength + nodeLength, keyLength,
						configServerBuffer + 10 + extraLength + nodeLength + keyLength, valueLength);
				}
			}
		}
		else if (pollResult < 0) {
			caerLog(CAER_LOG_ALERT, "Config Server", "poll() failed. Error: %d.", errno);
		}
		// pollResult == 0 just means nothing to do (timeout reached).
	}

	// Shutdown!
	close(configServerSocket);

	return (EXIT_SUCCESS);
}

// The response from the server follows a simplified version of the request
// protocol. A byte for ACTION, a byte for TYPE, 2 bytes for MSG_LEN and then
// up to 4092 bytes of MSG, for a maximum total of 4096 bytes again.
// MSG must be NUL terminated, and the NUL byte shall be part of the length.
static inline void setMsgLen(uint8_t *buf, uint16_t msgLen) {
	*((uint16_t *) (buf + 2)) = htole16(msgLen);
}

static inline void caerConfigSendError(int connectedClientSocket, const char *errorMsg) {
	size_t errorMsgLength = strlen(errorMsg);

	size_t responseLength = 4 + errorMsgLength + 1; // +1 for terminating NUL byte.
	uint8_t response[responseLength];

	response[0] = ERROR;
	response[1] = STRING;
	setMsgLen(response, (uint16_t) (errorMsgLength + 1));
	memcpy(response + 4, errorMsg, errorMsgLength);
	response[4 + errorMsgLength] = '\0';

	if (!sendUntilDone(connectedClientSocket, response, responseLength)) {
		// Error on send. Log for now.
		caerLog(CAER_LOG_DEBUG, "Config Server", "Disconnected client on send (fd %d).", connectedClientSocket);
		return;
	}

	caerLog(CAER_LOG_DEBUG, "Config Server", "Sent back error message '%s' to client.", errorMsg);
}

static inline void caerConfigSendResponse(int connectedClientSocket, uint8_t action, uint8_t type, const uint8_t *msg,
	size_t msgLength) {
	size_t responseLength = 4 + msgLength;
	uint8_t response[responseLength];

	response[0] = action;
	response[1] = type;
	setMsgLen(response, (uint16_t) msgLength);
	memcpy(response + 4, msg, msgLength);
	// Msg must already be NUL terminated!

	if (!sendUntilDone(connectedClientSocket, response, responseLength)) {
		// Error on send. Log for now.
		caerLog(CAER_LOG_DEBUG, "Config Server", "Disconnected client on send (fd %d).", connectedClientSocket);
		return;
	}

	caerLog(CAER_LOG_DEBUG, "Config Server",
		"Sent back message to client: action=%" PRIu8 ", type=%" PRIu8 ", msgLength=%zu.", action, type, msgLength);
}

static void caerConfigServerHandleRequest(int connectedClientSocket, uint8_t action, uint8_t type, const uint8_t *extra,
	size_t extraLength, const uint8_t *node, size_t nodeLength, const uint8_t *key, size_t keyLength,
	const uint8_t *value, size_t valueLength) {
	UNUSED_ARGUMENT(extra);

	caerLog(CAER_LOG_DEBUG, "Config Server",
		"Handling request: action=%" PRIu8 ", type=%" PRIu8 ", extraLength=%zu, nodeLength=%zu, keyLength=%zu, valueLength=%zu.",
		action, type, extraLength, nodeLength, keyLength, valueLength);

	// Interpretation of data is up to each action individually.
	sshs configStore = sshsGetGlobal();

	switch (action) {
		case NODE_EXISTS: {
			// We only need the node name here. Type is not used (ignored)!
			bool result = sshsExistsNode(configStore, (const char *) node);

			// Send back result to client. Format is the same as incoming data.
			const uint8_t *sendResult = (const uint8_t *) ((result) ? ("true") : ("false"));
			size_t sendResultLength = (result) ? (5) : (6);
			caerConfigSendResponse(connectedClientSocket, NODE_EXISTS, BOOL, sendResult, sendResultLength);

			break;
		}

		case ATTR_EXISTS: {
			bool nodeExists = sshsExistsNode(configStore, (const char *) node);

			// Only allow operations on existing nodes, this is for remote
			// control, so we only manipulate what's already there!
			if (!nodeExists) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket,
					"Node doesn't exist. Operations are only allowed on existing data.");

				break;
			}

			// This cannot fail, since we know the node exists from above.
			sshsNode wantedNode = sshsGetNode(configStore, (const char *) node);

			// Check if attribute exists.
			bool result = sshsNodeAttributeExists(wantedNode, (const char *) key, type);

			// Send back result to client. Format is the same as incoming data.
			const uint8_t *sendResult = (const uint8_t *) ((result) ? ("true") : ("false"));
			size_t sendResultLength = (result) ? (5) : (6);
			caerConfigSendResponse(connectedClientSocket, ATTR_EXISTS, BOOL, sendResult, sendResultLength);

			break;
		}

		case GET: {
			bool nodeExists = sshsExistsNode(configStore, (const char *) node);

			// Only allow operations on existing nodes, this is for remote
			// control, so we only manipulate what's already there!
			if (!nodeExists) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket,
					"Node doesn't exist. Operations are only allowed on existing data.");

				break;
			}

			// This cannot fail, since we know the node exists from above.
			sshsNode wantedNode = sshsGetNode(configStore, (const char *) node);

			// Check if attribute exists. Only allow operations on existing attributes!
			bool attrExists = sshsNodeAttributeExists(wantedNode, (const char *) key, type);

			if (!attrExists) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket,
					"Attribute of given type doesn't exist. Operations are only allowed on existing data.");

				break;
			}

			union sshs_node_attr_value result = sshsNodeGetAttribute(wantedNode, (const char *) key, type);

			char *resultStr = sshsHelperValueToStringConverter(type, result);

			if (resultStr == NULL) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket, "Failed to allocate memory for value string.");
			}
			else {
				caerConfigSendResponse(connectedClientSocket, GET, type, (const uint8_t *) resultStr,
					strlen(resultStr) + 1);

				free(resultStr);
			}

			// If this is a string, we must remember to free the original result.str
			// too, since it will also be a copy of the string coming from SSHS.
			if (type == STRING) {
				free(result.string);
			}

			break;
		}

		case PUT: {
			bool nodeExists = sshsExistsNode(configStore, (const char *) node);

			// Only allow operations on existing nodes, this is for remote
			// control, so we only manipulate what's already there!
			if (!nodeExists) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket,
					"Node doesn't exist. Operations are only allowed on existing data.");

				break;
			}

			// This cannot fail, since we know the node exists from above.
			sshsNode wantedNode = sshsGetNode(configStore, (const char *) node);

			// Check if attribute exists. Only allow operations on existing attributes!
			bool attrExists = sshsNodeAttributeExists(wantedNode, (const char *) key, type);

			if (!attrExists) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket,
					"Attribute of given type doesn't exist. Operations are only allowed on existing data.");

				break;
			}

			// Put given value into config node. Node, attr and type are already verified.
			const char *typeStr = sshsHelperTypeToStringConverter(type);
			if (!sshsNodeStringToNodeConverter(wantedNode, (const char *) key, typeStr, (const char *) value)) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket, "Impossible to convert value according to type.");

				break;
			}

			// Send back confirmation to the client.
			caerConfigSendResponse(connectedClientSocket, PUT, BOOL, (const uint8_t *) "true", 5);

			break;
		}

		case GET_CHILDREN: {
			bool nodeExists = sshsExistsNode(configStore, (const char *) node);

			// Only allow operations on existing nodes, this is for remote
			// control, so we only manipulate what's already there!
			if (!nodeExists) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket,
					"Node doesn't exist. Operations are only allowed on existing data.");

				break;
			}

			// This cannot fail, since we know the node exists from above.
			sshsNode wantedNode = sshsGetNode(configStore, (const char *) node);

			// Get the names of all the child nodes and return them.
			size_t numNames;
			const char **childNames = sshsNodeGetChildNames(wantedNode, &numNames);

			// No children at all, return empty.
			if (childNames == NULL) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket, "Node has no children.");

				break;
			}

			// We need to return a big string with all of the child names,
			// separated by a NUL character.
			size_t namesLength = 0;

			for (size_t i = 0; i < numNames; i++) {
				namesLength += strlen(childNames[i]) + 1; // +1 for terminating NUL byte.
			}

			// Allocate a buffer for the names and copy them over.
			char namesBuffer[namesLength];

			for (size_t i = 0, acc = 0; i < numNames; i++) {
				size_t len = strlen(childNames[i]) + 1;
				memcpy(namesBuffer + acc, childNames[i], len);
				acc += len;
			}

			caerConfigSendResponse(connectedClientSocket, GET_CHILDREN, STRING, (const uint8_t *) namesBuffer,
				namesLength);

			break;
		}

		case GET_ATTRIBUTES: {
			bool nodeExists = sshsExistsNode(configStore, (const char *) node);

			// Only allow operations on existing nodes, this is for remote
			// control, so we only manipulate what's already there!
			if (!nodeExists) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket,
					"Node doesn't exist. Operations are only allowed on existing data.");

				break;
			}

			// This cannot fail, since we know the node exists from above.
			sshsNode wantedNode = sshsGetNode(configStore, (const char *) node);

			// Get the keys of all the attributes and return them.
			size_t numKeys;
			const char **attrKeys = sshsNodeGetAttributeKeys(wantedNode, &numKeys);

			// No attributes at all, return empty.
			if (attrKeys == NULL) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket, "Node has no attributes.");

				break;
			}

			// We need to return a big string with all of the attribute keys,
			// separated by a NUL character.
			size_t keysLength = 0;

			for (size_t i = 0; i < numKeys; i++) {
				keysLength += strlen(attrKeys[i]) + 1; // +1 for terminating NUL byte.
			}

			// Allocate a buffer for the keys and copy them over.
			char keysBuffer[keysLength];

			for (size_t i = 0, acc = 0; i < numKeys; i++) {
				size_t len = strlen(attrKeys[i]) + 1;
				memcpy(keysBuffer + acc, attrKeys[i], len);
				acc += len;
			}

			caerConfigSendResponse(connectedClientSocket, GET_ATTRIBUTES, STRING, (const uint8_t *) keysBuffer,
				keysLength);

			break;
		}

		case GET_TYPES: {
			bool nodeExists = sshsExistsNode(configStore, (const char *) node);

			// Only allow operations on existing nodes, this is for remote
			// control, so we only manipulate what's already there!
			if (!nodeExists) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket,
					"Node doesn't exist. Operations are only allowed on existing data.");

				break;
			}

			// This cannot fail, since we know the node exists from above.
			sshsNode wantedNode = sshsGetNode(configStore, (const char *) node);

			// Check if any keys match the given one and return its types.
			size_t numTypes;
			enum sshs_node_attr_value_type *attrTypes = sshsNodeGetAttributeTypes(wantedNode, (const char *) key,
				&numTypes);

			// No attributes for specified key, return empty.
			if (attrTypes == NULL) {
				// Send back error message to client.
				caerConfigSendError(connectedClientSocket, "Node has no attributes with specified key.");

				break;
			}

			// We need to return a big string with all of the attribute types,
			// separated by a NUL character.
			size_t typesLength = 0;

			for (size_t i = 0; i < numTypes; i++) {
				const char *typeString = sshsHelperTypeToStringConverter(attrTypes[i]);
				typesLength += strlen(typeString) + 1; // +1 for terminating NUL byte.
			}

			// Allocate a buffer for the types and copy them over.
			char typesBuffer[typesLength];

			for (size_t i = 0, acc = 0; i < numTypes; i++) {
				const char *typeString = sshsHelperTypeToStringConverter(attrTypes[i]);
				size_t len = strlen(typeString) + 1;
				memcpy(typesBuffer + acc, typeString, len);
				acc += len;
			}

			caerConfigSendResponse(connectedClientSocket, GET_TYPES, STRING, (const uint8_t *) typesBuffer,
				typesLength);

			break;
		}

		default:
			// Unknown action, send error back to client.
			caerConfigSendError(connectedClientSocket, "Unknown action.");

			break;
	}
}
