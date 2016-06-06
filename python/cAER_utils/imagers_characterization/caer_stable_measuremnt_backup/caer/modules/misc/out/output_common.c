#include "output_common.h"
#include <unistd.h>
#include <sys/uio.h>
#include <stdatomic.h>

#include <libcaer/events/common.h>

struct output_common_state {
	int fileDescriptor;
	bool validOnly;
	int32_t maxBufferSize;
	int32_t maxBufferInterval;
	int32_t transferBufferSize;
	atomic_uint_fast32_t packetAmount;
	struct eventPacketMapper *packetMapper;
	thrd_t outputThread;
};

typedef struct output_common_state *outputCommonState;

static void copyPacketToTransferRing(struct eventPacketMapper *packetMapper, size_t packetAmount, void *eventPacket);
static struct eventPacketMapper *initializePacketMapper(size_t amount, size_t bufferSize);
static int outputHandlerThread(void *stateArg);

/**
 * Copy event packets to the right ring buffer for transfer
 * to the external output handling thread.
 *
 * @param packetMapper array of packet mapper structures: (Type, Source) -> TransferRing.
 * @param packetAmount length of arrays, amount of expected different event packets.
 * @param eventPacket an event packet.
 */
static void copyPacketToTransferRing(struct eventPacketMapper *packetMapper, size_t packetAmount, void *eventPacket) {
	// Skip empty event packets.
	if (eventPacket == NULL) {
		return;
	}

	// Get type and source information from the event packet.
	caerEventPacketHeader header = eventPacket;
	int16_t eventSource = caerEventPacketHeaderGetEventSource(header);
	int16_t eventType = caerEventPacketHeaderGetEventType(header);

	RingBuffer transferRing = NULL;

	// Map it to a transfer ring buffer.
	for (size_t i = 0; i < packetAmount; i++) {
		// Check that there is a unique mapping to a transfer ring, or if not,
		// create a new one in a free mapper slot. Slots are filled up in increasing
		// index order, so if we reach empty slots, there can't be a match afterwards.
		if (packetMapper[i].sourceID == eventSource && packetMapper[i].typeID == eventType) {
			// Found match, use it.
			transferRing = packetMapper[i].transferRing;
			break;
		}

		// Reached empty slot, use it.
		if (packetMapper[i].sourceID == -1) {
			packetMapper[i].sourceID = eventSource;
			packetMapper[i].typeID = eventType;

			transferRing = packetMapper[i].transferRing;
			break;
		}
	}

	// Check that a valid index was found, else complain.
	if (transferRing == NULL) {
		caerLog(CAER_LOG_ERROR, "Data Output",
			"New packet source/type and no more free slots available, this means an unexpected event packet made its way to this output module, one that was not declared at call time.");
		return;
	}

	// Now that we know where to copy the event packet to, let's do it.
	caerEventPacketHeader eventPacketCopy = caerCopyEventPacket(eventPacket);
	if (eventPacketCopy == NULL) {
		// Failed to copy packet.
		caerLog(CAER_LOG_ERROR, "Data Output", "Failed to put copy packet.");
		return;
	}

	if (!ringBufferPut(transferRing, eventPacketCopy)) {
		// TODO: handle ring buffer full, maybe block on setting?
		caerLog(CAER_LOG_INFO, "Data Output", "Failed to put new packet on transfer ring: ring full.");
		free(eventPacketCopy);
	}
}

static struct eventPacketMapper *initializePacketMapper(size_t amount, size_t bufferSize) {
	struct eventPacketMapper *mapper = calloc(amount, sizeof(*mapper));
	if (mapper == NULL) {
		// Allocation error.
		return (NULL);
	}

	// Initialize all the ring buffers.
	bool initFail = false;

	for (size_t i = 0; i < amount; i++) {
		mapper[i].transferRing = ringBufferInit(bufferSize);
		if (mapper[i].transferRing == NULL) {
			// Failed to initialize.
			initFail = true;
		}
	}

	// Check that they were initialized correctly.
	if (initFail) {
		// Free everything.
		for (size_t i = 0; i < amount; i++) {
			if (mapper[i].transferRing != NULL) {
				ringBufferFree(mapper[i].transferRing);
			}
		}

		free(mapper);

		return (NULL);
	}

	return (mapper);
}

bool caerOutputCommonInit(caerModuleData moduleData, int fd) {
	outputCommonState state = moduleData->moduleState;

	// Check for invalid file descriptor.
	if (fd < 0) {
		caerLog(CAER_LOG_ERROR, "Data Output", "Invalid file descriptor.");
		return (false);
	}

	state->fileDescriptor = fd;

	// Put defaults for buffer and get the actual value back.
	sshsNodePutIntIfAbsent(moduleData->moduleNode, "maxBufferSize", 8192); // in bytes
	sshsNodePutIntIfAbsent(moduleData->moduleNode, "maxBufferInterval", 10000); // in µs

	sshsNodePutIntIfAbsent(moduleData->moduleNode, "transferBufferSize", 128); // in packets

	state->maxBufferSize = sshsNodeGetInt(moduleData->moduleNode, "maxBufferSize");
	state->maxBufferInterval = sshsNodeGetInt(moduleData->moduleNode, "maxBufferInterval");

	state->transferBufferSize = sshsNodeGetInt(moduleData->moduleNode, "transferBufferSize");

	// Same for forward-valid-only-events flag.
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "validOnly", false);

	state->validOnly = sshsNodeGetBool(moduleData->moduleNode, "validOnly");

	// Start output handling thread.
	if (thrd_create(&state->outputThread, &outputHandlerThread, state) != thrd_success) {
		caerLog(CAER_LOG_ERROR, "Data Output", "Failed to start output handling thread.");
		return (false);
	}

	return (true);
}

void caerOutputCommonExit(caerModuleData moduleData) {
	outputCommonState state = moduleData->moduleState;

	if (thrd_join(state->outputThread, NULL) != thrd_success) {
		caerLog(CAER_LOG_ERROR, "Data Output", "Failed to join output handling thread.");
	}

	if (state->packetMapper != NULL) {
		// Free additional memory used for RingBuffers.
		for (size_t i = 0; i < atomic_load(&state->packetAmount); i++) {
			RingBuffer buf = state->packetMapper[i].transferRing;

			caerEventPacketHeader header;
			while ((header = ringBufferGet(buf)) != NULL) {
				free(header); // Free unused packet copies.
			}

			ringBufferFree(buf);
		}

		free(state->packetMapper);

		state->packetMapper = NULL;
		atomic_store(&state->packetAmount, 0);
	}

	// Close file descriptor.
	close(state->fileDescriptor);
}

void caerOutputCommonRun(caerModuleData moduleData, size_t argsNumber, va_list args) {
	outputCommonState state = moduleData->moduleState;

	// Initialize packet mappers array if first run.
	if (state->packetMapper == NULL) {
		state->packetMapper = initializePacketMapper(argsNumber, (size_t) state->transferBufferSize);
		if (state->packetMapper == NULL) {
			caerLog(CAER_LOG_ERROR, "Data Output", "Failed to allocate memory for output packet mapper.");
			return; // Skip on failure.
		}

		atomic_store_explicit(&state->packetAmount, argsNumber, memory_order_release);
	}

	// Check event mapper allocation size: must reflect argsNumber.
	size_t packetAmount = atomic_load_explicit(&state->packetAmount, memory_order_relaxed);

	if (packetAmount != argsNumber) {
		caerLog(CAER_LOG_ERROR, "Data Output", "Number of passed packet arguments changed, this is not supported!");
	}

	for (size_t i = 0; i < argsNumber; i++) {
		caerEventPacketHeader packetHeader = va_arg(args, caerEventPacketHeader);

		copyPacketToTransferRing(state->packetMapper, packetAmount, packetHeader);
	}
}

void caerOutputCommonConfig(caerModuleData moduleData) {
	outputCommonState state = moduleData->moduleState;

}

static int outputHandlerThread(void *stateArg) {
	outputCommonState state = stateArg;

	while (true) {
		size_t packetAmount = atomic_load_explicit(&state->packetAmount, memory_order_acquire);
		if (packetAmount == 0) {
			continue; // Wait.
		}


	}
}
