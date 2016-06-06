/*
 * nets.h
 *
 *  Created on: Jan 19, 2014
 *      Author: chtekk
 */

#ifndef NETS_H_
#define NETS_H_

#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <fcntl.h>

static inline bool socketBlockingMode(int fd, bool blocking) {
	if (fd < 0) {
		return (false);
	}

	int currFlags = fcntl(fd, F_GETFL, 0);
	if (currFlags < 0) {
		return (false);
	}

	if (blocking) {
		currFlags &= ~O_NONBLOCK;
	}
	else {
		currFlags |= O_NONBLOCK;
	}

	return (fcntl(fd, F_SETFL, currFlags) == 0);
}

static inline bool socketReuseAddr(int fd, bool reuseAddr) {
	if (fd < 0) {
		return (false);
	}

	int val = 0;

	if (reuseAddr) {
		val = 1;
	}

	return (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(int)) == 0);
}

// Write toWrite bytes to the socket sock from buffer.
// Return true on success, false on failure.
static inline bool sendUntilDone(int sock, void *buffer, size_t toWrite) {
	uint8_t *dataBuffer = buffer;
	size_t written = 0;

	while (written < toWrite) {
		ssize_t sendResult = send(sock, dataBuffer + written, toWrite - written, 0);
		if (sendResult <= 0) {
			return (false);
		}

		written += (size_t) sendResult;
	}

	return (true);
}

// Read toRead bytes from the socket sock into buffer.
// Return true on success, false on failure.
static inline bool recvUntilDone(int sock, void *buffer, size_t toRead) {
	uint8_t *dataBuffer = buffer;
	size_t read = 0;

	while (read < toRead) {
		ssize_t recvResult = recv(sock, dataBuffer + read, toRead - read, 0);
		if (recvResult <= 0) {
			return (false);
		}

		read += (size_t) recvResult;
	}

	return (true);
}

#endif /* NETS_H_ */
