/*
 * file.c (input)
 *
 *  Created on: Okt 29, 2015
 *      Author: phineasng
 */

#include "in_file.h"
#include "base/module.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <pwd.h>
#include <time.h>
#include <unistd.h>
#include "ext/ringbuffer/ringbuffer.h"
#include <libcaer/devices/dvs128.h>
#include <libcaer/devices/davis.h>
#include <libcaer/events/packetContainer.h>

static int inputFromFileThread(void* ptr);

struct input_file_state {
	// io params
	int fileDescriptor;
	// playback params
	atomic_bool play;
	atomic_bool stop; // equivalent to: pause (i.e. play = false) and reset (close and reopen the file)
	// ringbuffer parameters
	RingBuffer rBuf;
	size_t rBufSize; // used only at initializazion, i.e. no dynamic reallocation of the ringbuffer
	// input thread variables
	thrd_t inputReadThread;
	void (*dataNotifyIncrease)(void *ptr);
	void (*dataNotifyDecrease)(void *ptr);
	void *dataNotifyUserPtr;
};

typedef struct input_file_state* inputFileState;

static bool caerInputFileInit(caerModuleData moduleData);
static void caerInputFileRun(caerModuleData moduleData, size_t argsNumber, va_list args);
static void caerInputFileConfig(caerModuleData moduleData);
static void caerInputFileExit(caerModuleData moduleData);
static caerEventPacketContainer packetsFromFileToContainer(caerModuleData moduleData);
static void resetBuffer(caerModuleData);

static struct caer_module_functions caerInputFileFunctions = { .moduleInit = &caerInputFileInit, .moduleRun =
	&caerInputFileRun, .moduleConfig = &caerInputFileConfig, .moduleExit = &caerInputFileExit };

caerEventPacketContainer caerInputFile(uint16_t moduleID) {
	caerModuleData moduleData = caerMainloopFindModule(moduleID, "InputFile");

	caerEventPacketContainer result = NULL;

	caerModuleSM(&caerInputFileFunctions, moduleData, sizeof(struct input_file_state), 1, &result);

	return ((caerEventPacketContainer) result);
}

static char *getUserHomeDirectory(const char *subSystemString);
static char *getFullFilePath(const char * subSystemString, const char *directory, const char *fileName);
static void caerInputFileConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue);

// Remember to free strings returned by this.
static char *getUserHomeDirectory(const char *subSystemString) {
	// First check the environment for $HOME.
	char *homeVar = getenv("HOME");

	if (homeVar != NULL) {
		char *retVar = strdup(homeVar);
		if (retVar == NULL) {
			caerLog(CAER_LOG_CRITICAL, subSystemString, "Unable to allocate memory for user home directory path.");
			return (NULL);
		}

		return (retVar);
	}

	// Else try to get it from the user data storage.
	struct passwd userPasswd;
	struct passwd *userPasswdPtr;
	char userPasswdBuf[2048];

	if (getpwuid_r(getuid(), &userPasswd, userPasswdBuf, sizeof(userPasswdBuf), &userPasswdPtr) == 0) {
		// Success!
		char *retVar = strdup(userPasswd.pw_dir);
		if (retVar == NULL) {
			caerLog(CAER_LOG_CRITICAL, subSystemString, "Unable to allocate memory for user home directory path.");
			return (NULL);
		}

		return (retVar);
	}

	// Else just return /tmp as a place to write to.
	char *retVar = strdup("/tmp");
	if (retVar == NULL) {
		caerLog(CAER_LOG_CRITICAL, subSystemString, "Unable to allocate memory for user home directory path.");
		return (NULL);
	}

	return (retVar);
}

// Remember to free strings returned by this.
static char *getFullFilePath(const char * subSystemString, const char *directory, const char *fileName) {

	// Assemble together: directory/fileName
	size_t filePathLength = strlen(directory) + strlen(fileName) + 2;
	// 1 for the directory/fileName separating slash.

	char *filePath = malloc(filePathLength);
	if (filePath == NULL) {
		caerLog(CAER_LOG_CRITICAL, subSystemString, "Unable to allocate memory for full file path.");
		return (NULL);
	}

	snprintf(filePath, filePathLength, "%s/%s", directory, fileName);

	return (filePath);
}

static bool caerInputFileInit(caerModuleData moduleData) {
	inputFileState state = moduleData->moduleState;

	// setup SSHS nodes
	// -- directory path
	char *userHomeDir = getUserHomeDirectory(moduleData->moduleSubSystemString);
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "directory", userHomeDir);
	// -- default filename (dummy)
	char *fileName = strdup("caer_out-YYYY-MM-DD_hh:mm:ss.aer2");
	sshsNodePutStringIfAbsent(moduleData->moduleNode, "filename", fileName);
	free(userHomeDir);
	free(fileName);
	// -- playback boolean (false = pause); always setting initial value to false
	sshsNodePutBool(moduleData->moduleNode, "StartPlayback", false);
	state->play = false;
	sshsNodePutBool(moduleData->moduleNode, "StopPlayback", false);
	state->stop = false;
	// -- ring buffer size
	sshsNodePutShortIfAbsent(moduleData->moduleNode, "RingBufferSize", 128);
	// -- process_all flag (not modifiable at runtime)
	sshsNodePutBoolIfAbsent(moduleData->moduleNode, "ProcessAll", false);
	// -- if relative node "sourceInfo/" does not exist, add it (so file can be used with the visualization module)
	sshsNode sourceInfoNode = sshsGetRelativeNode(moduleData->moduleNode, "sourceInfo/");
	// -- -- array(frame) size of the original device (added so it works with the visualizer module)
	sshsNodePutShortIfAbsent(sourceInfoNode, "dvsSizeX", 240);
	sshsNodePutShortIfAbsent(sourceInfoNode, "dvsSizeY", 180);
	sshsNodePutShortIfAbsent(sourceInfoNode, "apsSizeX", 240);
	sshsNodePutShortIfAbsent(sourceInfoNode, "apsSizeY", 180);

	// NOTE: add here other fields that seem reasonable for input control (playback param, time window)

	// Take actual values
	userHomeDir = sshsNodeGetString(moduleData->moduleNode, "directory");
	fileName = sshsNodeGetString(moduleData->moduleNode, "filename");

	// Generate filename and open it
	char *filePath = getFullFilePath(moduleData->moduleSubSystemString, userHomeDir, fileName);
	free(userHomeDir);
	free(fileName);
	state->fileDescriptor = open(filePath, O_RDONLY);
	if (state->fileDescriptor < 0) {
		caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
			"Could not open input file '%s' for reading. Error: %d.", filePath, errno);
		free(filePath);

		return (false);
	}

	// log successful opening of the file
	caerLog(CAER_LOG_DEBUG, moduleData->moduleSubSystemString, "Opened input file '%s' successfully for reading.",
		filePath);
	free(filePath);

	// initialize ringbuffer
	state->rBuf = ringBufferInit((size_t) sshsNodeGetShort(moduleData->moduleNode, "RingBufferSize"));
	// set notifier
	state->dataNotifyDecrease = &mainloopDataNotifyDecrease;
	state->dataNotifyIncrease = &mainloopDataNotifyIncrease;
	state->dataNotifyUserPtr = caerMainloopGetReference();
	// start thread
	if ((errno = thrd_create(&state->inputReadThread, &inputFromFileThread, moduleData)) != thrd_success) {
		ringBufferFree(state->rBuf);
		caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
			"Failed to start data acquisition thread. Error: %d.",
			errno);
		return (false);
	}

	// Add config listeners last, to avoid having them dangling if Init doesn't succeed.
	sshsNodeAddAttributeListener(moduleData->moduleNode, moduleData, &caerInputFileConfigListener);

	return (true);
}

static void caerInputFileRun(caerModuleData moduleData, size_t argsNumber, va_list args) {
	inputFileState state = moduleData->moduleState;
	UNUSED_ARGUMENT(argsNumber);

	// Wait for play command
	if (!atomic_load(&state->play)) {
		return;
	}

	// Interpret variable arguments
	caerEventPacketContainer* container = va_arg(args, caerEventPacketContainer*);

	*container = ringBufferGet(state->rBuf);

	if (*container != NULL) {
		state->dataNotifyDecrease(state->dataNotifyUserPtr);
		caerMainloopFreeAfterLoop((void (*)(void*)) &caerEventPacketContainerFree, *container);
	}
	return;
}

static void caerInputFileExit(caerModuleData moduleData) {
	// Remove listener, which can reference invalid memory in userData.
	sshsNodeRemoveAttributeListener(moduleData->moduleNode, moduleData, &caerInputFileConfigListener);

	inputFileState state = moduleData->moduleState;

	// Tell the input thread to stop. Main thread waits until it stopped
	atomic_store(&state->stop, true);
	int* res = malloc(sizeof(int));
	thrd_join(state->inputReadThread, res);
	// Reset and Free RingBuffer
	resetBuffer(moduleData);
	ringBufferFree(state->rBuf);
	// Close file.
	close(state->fileDescriptor);
}

static void caerInputFileConfig(caerModuleData moduleData) {
	inputFileState state = moduleData->moduleState;
	sshsNode node = moduleData->moduleNode;

	// Get the current value to examine by atomic exchange, since we don't
	// want there to be any possible store between a load/store pair.
	// NOTE: configUpdate treated as a bit field, cf. caerInputFileConfigListener()
	uintptr_t configUpdate = atomic_exchange(&moduleData->configUpdate, 0);
	if (configUpdate & (0x01 << 0)) {
		sshsNodePutBool(node, "StopPlayback", true);
	}

	if (configUpdate & (0x01 << 1)) {
		// wait for the thread to correctly exit
		int* res = malloc(sizeof(int));
		thrd_join(state->inputReadThread, res);
		if ((*res) > thrd_success) {
			caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
				"Something bad happened while waiting for the input thread. Error: %d.", *res);
		}
		// reset buffer
		resetBuffer(moduleData);
		// set everything to false
		sshsNodePutBool(node, "StopPlayback", false);
		sshsNodePutBool(node, "StartPlayback", false);
		// Filename related settings changed.
		// Generate new file name and open it.
		char *directory = sshsNodeGetString(moduleData->moduleNode, "directory");
		char *fileName = sshsNodeGetString(moduleData->moduleNode, "filename");
		char *filePath = getFullFilePath(moduleData->moduleSubSystemString, directory, fileName);
		free(directory);
		free(fileName);

		int newFileDescriptor = open(filePath, O_RDONLY);
		if (newFileDescriptor < 0) {
			caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
				"Could open input file '%s' for reading. Error: %d.", filePath, errno);
			free(filePath);

			return;
		}

		caerLog(CAER_LOG_DEBUG, moduleData->moduleSubSystemString, "Opened input file '%s' successfully for reading.",
			filePath);
		free(filePath);

		// New fd ready and opened, close old and set new.
		close(state->fileDescriptor);
		state->fileDescriptor = newFileDescriptor;

		// start a new thread
		if ((errno = thrd_create(&state->inputReadThread, &inputFromFileThread, moduleData)) != thrd_success) {
			ringBufferFree(state->rBuf);
			caerLog(CAER_LOG_CRITICAL, moduleData->moduleSubSystemString,
				"Failed to start data acquisition thread. Error: %d.",
				errno);

			return;
		}
	}
}

static void caerInputFileConfigListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue) {
	UNUSED_ARGUMENT(changeValue);

	caerModuleData data = userData;
	inputFileState state = data->moduleState;

	// Distinguish changes to the validOnly flag or to the filename, by setting
	// configUpdate appropriately like a bit-field.
	if (event == ATTRIBUTE_MODIFIED) {
		if (changeType == STRING && (caerStrEquals(changeKey, "directory") || caerStrEquals(changeKey, "filename"))) {
			atomic_fetch_or(&data->configUpdate, (0x01 << 0));
		}
		if (changeType == BOOL && caerStrEquals(changeKey, "StartPlayback")) {
			bool newVal = sshsNodeGetBool(node, "StartPlayback");
			atomic_store(&state->play, newVal);
		}
		if (changeType == BOOL && caerStrEquals(changeKey, "StopPlayback")) { // stop playback is equivalent to change file and pause
			bool newVal = sshsNodeGetBool(node, "StopPlayback");
			atomic_store(&state->stop, newVal);
			if (newVal) {
				atomic_fetch_or(&data->configUpdate, (0x01 << 1));
			}
		}
	}

}

static caerEventPacketContainer packetsFromFileToContainer(caerModuleData moduleData) {
	inputFileState state = moduleData->moduleState;

	// allocate new container
	caerEventPacketContainer newContainer = caerEventPacketContainerAllocate(1);

	for (int i = 0; i < 1; ++i) {
		caerEventPacketHeader packet = caerInputCommonReadPacket(state->fileDescriptor);
		if (packet == NULL) {
			caerEventPacketContainerFree(newContainer);
			return NULL;
		}
		else {
			caerEventPacketHeaderSetEventSource(packet, I16T(moduleData->moduleID));
			caerEventPacketContainerSetEventPacket(newContainer, i, packet);
		}
	}

	return (newContainer);
}

static int inputFromFileThread(void* ptr) {
	caerModuleData data = ptr;
	inputFileState state = data->moduleState;
	int16_t IDSource = I16T(data->moduleID);

	// create local copy of the file descriptor
	int fid = state->fileDescriptor;
	// remainder packet, used to identify the moment to send a container. Read in first packet.
	caerEventPacketHeader packetHeader = caerInputCommonReadPacket(fid);
	if (packetHeader == NULL)
		thrd_exit(thrd_success);
	caerEventPacketHeaderSetEventSource(packetHeader, IDSource);
	// keep track of the greatest event_type to appropriately allocate the container
	int16_t maxSizeContainer = I16T(caerEventPacketHeaderGetEventType(packetHeader) + 1);
	// allocate container
	caerEventPacketContainer container = caerEventPacketContainerAllocate(maxSizeContainer);
	// useful variables
	int16_t currType;

	while (1) {
		if (atomic_load(&state->stop)) {
			free(packetHeader);
			caerEventPacketContainerFree(container);
			thrd_exit(thrd_success);
		}
		currType = caerEventPacketHeaderGetEventType(packetHeader);
		// if currType is too big, reallocate container
		if (currType >= maxSizeContainer) {
			// new container and transfer the content, adding the new packet
			caerEventPacketContainer newContainer = caerEventPacketContainerAllocate(currType + 1);
			for (int16_t i = 0; i < maxSizeContainer; ++i) {
				caerEventPacketContainerSetEventPacket(newContainer, i,
					caerEventPacketContainerGetEventPacket(container, i));
			}
			free(container);
			container = newContainer;
			// update max size
			maxSizeContainer = I16T(currType + 1);
		}
		// if currType is already set, commit container to ring buffer ...
		if (caerEventPacketContainerGetEventPacket(container, currType) != NULL) {
			while (!ringBufferPut(state->rBuf, container) && !atomic_load(&state->stop)) {
			} // keep try to put, until succeed
			state->dataNotifyIncrease(state->dataNotifyUserPtr);

			// create new container
			container = caerEventPacketContainerAllocate(maxSizeContainer);
			continue; // last packet was not added to the container -> avoid reading a new one
		}
		else {	// ... else, add the packet to the container
			caerEventPacketContainerSetEventPacket(container, currType, packetHeader);
		}
		// read next packet
		packetHeader = caerInputCommonReadPacket(fid);
		if (packetHeader == NULL)
			thrd_exit(thrd_success);
		caerEventPacketHeaderSetEventSource(packetHeader, IDSource);
	}

	// push the new container to the ringbuffer
	thrd_exit(thrd_success);
}

static void resetBuffer(caerModuleData data) {
	inputFileState state = data->moduleState;
	RingBuffer rBuf = state->rBuf;

	void* ptr = ringBufferGet(rBuf);
	while (ptr != NULL) {
		state->dataNotifyDecrease(state->dataNotifyUserPtr);
		free(ptr);
		ptr = ringBufferGet(rBuf);
	}
}
