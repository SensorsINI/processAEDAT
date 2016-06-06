/*
 * udpststat.c
 *
 *  Created on: Jan 14, 2014
 *      Author: llongi
 */

#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#include <libcaer/events/common.h>

#include <signal.h>
#include <stdatomic.h>

static atomic_bool globalShutdown = ATOMIC_VAR_INIT(false);

static void globalShutdownSignalHandler(int signal) {
	// Simply set the running flag to false on SIGTERM and SIGINT (CTRL+C) for global shutdown.
	if (signal == SIGTERM || signal == SIGINT) {
		atomic_store(&globalShutdown, true);
	}
}

int main(int argc, char *argv[]) {
	// Install signal handler for global shutdown.
	struct sigaction shutdownAction;

	shutdownAction.sa_handler = &globalShutdownSignalHandler;
	shutdownAction.sa_flags = 0;
	sigemptyset(&shutdownAction.sa_mask);
	sigaddset(&shutdownAction.sa_mask, SIGTERM);
	sigaddset(&shutdownAction.sa_mask, SIGINT);

	if (sigaction(SIGTERM, &shutdownAction, NULL) == -1) {
		caerLog(CAER_LOG_CRITICAL, "ShutdownAction", "Failed to set signal handler for SIGTERM. Error: %d.", errno);
		return (EXIT_FAILURE);
	}

	if (sigaction(SIGINT, &shutdownAction, NULL) == -1) {
		caerLog(CAER_LOG_CRITICAL, "ShutdownAction", "Failed to set signal handler for SIGINT. Error: %d.", errno);
		return (EXIT_FAILURE);
	}

	// First of all, parse the IP:Port we need to listen on.
	// Those are for now also the only two parameters permitted.
	// If none passed, attempt to connect to default UDP IP:Port.
	const char *ipAddress = "127.0.0.1";
	uint16_t portNumber = 8888;

	if (argc != 1 && argc != 3) {
		fprintf(stderr, "Incorrect argument number. Either pass none for default IP:Port"
			"combination of 127.0.0.1:8888, or pass the IP followed by the Port.\n");
		return (EXIT_FAILURE);
	}

	// If explicitly passed, parse arguments.
	if (argc == 3) {
		ipAddress = argv[1];
		sscanf(argv[2], "%" SCNu16, &portNumber);
	}

	// Create listening socket for UDP data.
	int listenUDPSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (listenUDPSocket < 0) {
		fprintf(stderr, "Failed to create UDP socket.\n");
		return (EXIT_FAILURE);
	}

	struct sockaddr_in listenUDPAddress;
	memset(&listenUDPAddress, 0, sizeof(struct sockaddr_in));

	listenUDPAddress.sin_family = AF_INET;
	listenUDPAddress.sin_port = htons(portNumber);
	inet_aton(ipAddress, &listenUDPAddress.sin_addr); // htonl() is implicit here.

	if (bind(listenUDPSocket, (struct sockaddr *) &listenUDPAddress, sizeof(struct sockaddr_in)) < 0) {
		fprintf(stderr, "Failed to listen on UDP socket.\n");
		return (EXIT_FAILURE);
	}

	// 64K data buffer should be enough for the UDP packets.
	size_t dataBufferLength = 1024 * 64;
	uint8_t *dataBuffer = malloc(dataBufferLength);

	while (!atomic_load_explicit(&globalShutdown, memory_order_relaxed)) {
		ssize_t result = recv(listenUDPSocket, dataBuffer, dataBufferLength, 0);
		if (result <= 0) {
			fprintf(stderr, "Error in recv() call: %d\n", errno);
			continue;
		}

		printf("Result of recv() call: %zd\n", result);

		// Decode successfully received data.
		caerEventPacketHeader header = (caerEventPacketHeader) dataBuffer;

		int16_t eventType = caerEventPacketHeaderGetEventType(header);
		int16_t eventSource = caerEventPacketHeaderGetEventSource(header);
		int32_t eventSize = caerEventPacketHeaderGetEventSize(header);
		int32_t eventTSOffset = caerEventPacketHeaderGetEventTSOffset(header);
		int32_t eventCapacity = caerEventPacketHeaderGetEventCapacity(header);
		int32_t eventNumber = caerEventPacketHeaderGetEventNumber(header);
		int32_t eventValid = caerEventPacketHeaderGetEventValid(header);

		printf(
			"type = %" PRIi16 ", source = %" PRIi16 ", size = %" PRIi32 ", tsOffset = %" PRIi32 ", capacity = %" PRIi32 ", number = %" PRIi32 ", valid = %" PRIi32 ".\n",
			eventType, eventSource, eventSize, eventTSOffset, eventCapacity, eventNumber, eventValid);

		if (eventValid > 0) {
			void *firstEvent = caerGenericEventGetEvent(header, 0);
			void *lastEvent = caerGenericEventGetEvent(header, eventValid - 1);

			int32_t firstTS = caerGenericEventGetTimestamp(firstEvent, header);
			int32_t lastTS = caerGenericEventGetTimestamp(lastEvent, header);

			int32_t tsDifference = lastTS - firstTS;

			printf("Time difference in packet: %" PRIi32 " (first = %" PRIi32 ", last = %" PRIi32 ").\n", tsDifference,
				firstTS, lastTS);
		}

		printf("\n\n");
	}

	// Close connection.
	close(listenUDPSocket);

	free(dataBuffer);

	return (EXIT_SUCCESS);
}
