/*
 * mainloops.c
 *
 *  Created on: Dec 9, 2013
 *      Author: chtekk
 */

#include "mainloop.h"
#include <signal.h>
#include <unistd.h>

// Main-loop-related definitions.
static struct {
	// Set this to false for global program shutdown.
	atomic_bool running;
	caerMainloopData loopThreads;
	size_t loopThreadsLength;
} mainloopThreads;

static _Thread_local caerMainloopData glMainloopData = NULL;

static int caerMainloopRunner(void *inPtr);
static void caerMainloopSignalHandler(int signal);
static void caerMainloopShutdownListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue);

void caerMainloopRun(struct caer_mainloop_definition (*mainLoops)[], size_t numLoops) {
	if (numLoops == 0) {
		// Nothing to start, exit right away.
		caerLog(CAER_LOG_CRITICAL, "Mainloop",
			"The number of Mainloops to start is specified at zero: nothing to start!");
		return;
	}

	// Install signal handler for global shutdown.
	struct sigaction shutdown;

	shutdown.sa_handler = &caerMainloopSignalHandler;
	shutdown.sa_flags = 0;
	sigemptyset(&shutdown.sa_mask);
	sigaddset(&shutdown.sa_mask, SIGTERM);
	sigaddset(&shutdown.sa_mask, SIGINT);

	if (sigaction(SIGTERM, &shutdown, NULL) == -1) {
		caerLog(CAER_LOG_EMERGENCY, "Mainloop", "Failed to set signal handler for SIGTERM. Error: %d.", errno);
		exit(EXIT_FAILURE);
	}

	if (sigaction(SIGINT, &shutdown, NULL) == -1) {
		caerLog(CAER_LOG_EMERGENCY, "Mainloop", "Failed to set signal handler for SIGINT. Error: %d.", errno);
		exit(EXIT_FAILURE);
	}

	sshsNode rootNode = sshsGetNode(sshsGetGlobal(), "/");

	// Enable main-loops.
	atomic_store(&mainloopThreads.running, true);

	// Add shutdown hook to SSHS for external control.
	sshsNodePutBool(rootNode, "shutdown", false); // Always reset to false.
	sshsNodeAddAttributeListener(rootNode, &mainloopThreads.running, &caerMainloopShutdownListener);

	// Allocate memory for main-loops.
	mainloopThreads.loopThreadsLength = numLoops;
	mainloopThreads.loopThreads = calloc(mainloopThreads.loopThreadsLength, sizeof(struct caer_mainloop_data));
	if (mainloopThreads.loopThreads == NULL) {
		caerLog(CAER_LOG_EMERGENCY, "Mainloop", "Failed to allocate memory for main-loops. Error: %d.", errno);
		exit(EXIT_FAILURE);
	}

	// Configure and launch all main-loops.
	for (size_t i = 0; i < mainloopThreads.loopThreadsLength; i++) {
		mainloopThreads.loopThreads[i].mainloopID = (*mainLoops)[i].mlID;
		mainloopThreads.loopThreads[i].mainloopFunction = (*mainLoops)[i].mlFunction;

		// '/', then uint16_t as string -> max. 5 characters, '/': 7 bytes.
		char mlString[7 + 1]; // +1 for terminating NUL byte.
		snprintf(mlString, 7, "/%" PRIu16 "/", mainloopThreads.loopThreads[i].mainloopID);
		mlString[7] = '\0';

		mainloopThreads.loopThreads[i].mainloopNode = sshsGetNode(sshsGetGlobal(), mlString);

		// Enable this main-loop.
		atomic_store(&mainloopThreads.loopThreads[i].running, true);

		// Add per-mainloop shutdown hooks to SSHS for external control.
		sshsNodePutBool(mainloopThreads.loopThreads[i].mainloopNode, "shutdown", false); // Always reset to false.
		sshsNodeAddAttributeListener(mainloopThreads.loopThreads[i].mainloopNode, &mainloopThreads.loopThreads[i].running,
			&caerMainloopShutdownListener);

		if ((errno = thrd_create(&mainloopThreads.loopThreads[i].mainloop, &caerMainloopRunner,
			&mainloopThreads.loopThreads[i])) != thrd_success) {
			caerLog(CAER_LOG_EMERGENCY, sshsNodeGetName(mainloopThreads.loopThreads[i].mainloopNode),
				"Failed to create main-loop %" PRIu16 " thread. Error: %d.", mainloopThreads.loopThreads[i].mainloopID,
				errno);
			// TODO: better cleanup on failure?
			exit(EXIT_FAILURE);
		}
	}

	// Wait for someone to toggle the global shutdown flag.
	struct timespec oneSecondSleep = { .tv_sec = 1, .tv_nsec = 0 };

	while (atomic_load_explicit(&mainloopThreads.running, memory_order_relaxed)) {
		thrd_sleep(&oneSecondSleep, NULL);
	}

	// Notify shutdown to the main-loops ...
	for (size_t i = 0; i < mainloopThreads.loopThreadsLength; i++) {
		// Shutdown all loops that are still active.
		sshsNodePutBool(mainloopThreads.loopThreads[i].mainloopNode, "shutdown", true);
	}

	// ... and then wait for their clean shutdown.
	for (size_t i = 0; i < mainloopThreads.loopThreadsLength; i++) {
		if ((errno = thrd_join(mainloopThreads.loopThreads[i].mainloop, NULL) != thrd_success)) {
			caerLog(CAER_LOG_EMERGENCY, sshsNodeGetName(mainloopThreads.loopThreads[i].mainloopNode),
				"Failed to join main-loop %" PRIu16 " thread. Error: %d.", mainloopThreads.loopThreads[i].mainloopID,
				errno);
			// TODO: better cleanup on failure?
			exit(EXIT_FAILURE);
		}
	}

	// Done with everything, free the remaining memory.
	free(mainloopThreads.loopThreads);
}

// Only use this inside the mainloop-thread, not inside any other thread,
// like additional data acquisition threads or output threads.
caerModuleData caerMainloopFindModule(uint16_t moduleID, const char *moduleShortName) {
	caerMainloopData mainloopData = glMainloopData;
	caerModuleData moduleData;

	// This is only ever called from within modules running in a main-loop.
	// So always inside the same thread, needing thus no synchronization.
	HASH_FIND(hh, mainloopData->modules, &moduleID, sizeof(uint16_t), moduleData);

	if (moduleData == NULL) {
		// Create module (will succeed! If errors happen, whole mainloop dies).
		moduleData = caerModuleInitialize(moduleID, moduleShortName, mainloopData->mainloopNode);

		HASH_ADD(hh, mainloopData->modules, moduleID, sizeof(uint16_t), moduleData);
	}

	return (moduleData);
}

struct genericFree {
	void (*func)(void *mem);
	void *memPtr;
};

static const UT_icd ut_genericFree_icd = { sizeof(struct genericFree), NULL, NULL, NULL };

static int caerMainloopRunner(void *inPtr) {
	caerMainloopData mainloopData = inPtr;

	// Set global reference to main-loop memory for this thread (for modules).
	glMainloopData = mainloopData;

	// Enable memory recycling.
	utarray_new(mainloopData->memoryToFree, &ut_genericFree_icd);

	// If no data is available, sleep for a millisecond to avoid wasting resources.
	struct timespec noDataSleep = { .tv_sec = 0, .tv_nsec = 1000000 };

	// Make sure to call loop at least once to ensure initialization of data
	// producers, else dataAvailable will never be > 0.
	(*mainloopData->mainloopFunction)();

	// Wait for someone to toggle the module shutdown flag OR for the loop
	// itself to signal termination.
	size_t sleepCount = 0;

	while (atomic_load_explicit(&mainloopData->running, memory_order_relaxed)) {
		// Run only if data available to consume, else sleep. But make a run
		// anyway each second, to detect new devices for example.
		if (atomic_load_explicit(&mainloopData->dataAvailable, memory_order_acquire) > 0 || sleepCount > 1000) {
			sleepCount = 0;

			if (!(*mainloopData->mainloopFunction)()) {
				// Returning false from the main-loop: shutdown!
				break;
			}

			// After each successful main-loop run, free the memory that was
			// accumulated for things like packets, valid only during the run.
			struct genericFree *memFree = NULL;
			while ((memFree = (struct genericFree *) utarray_next(mainloopData->memoryToFree, memFree)) != NULL) {
				memFree->func(memFree->memPtr);
			}
			utarray_clear(mainloopData->memoryToFree);
		}
		else {
			sleepCount++;
			thrd_sleep(&noDataSleep, NULL);
		}
	}

	// Shutdown all modules.
	for (caerModuleData m = mainloopData->modules; m != NULL; m = m->hh.next) {
		sshsNodePutBool(m->moduleNode, "shutdown", true);
	}

	// Run through the loop one last time to correctly shutdown all the modules.
	(*mainloopData->mainloopFunction)();

	// Free module memory, allocated in caerMainloopFindModule().
	caerModuleData module, tmp;

	HASH_ITER(hh, mainloopData->modules, module, tmp)
	{
		HASH_DEL(mainloopData->modules, module);
		caerModuleDestroy(module);
	}

	// Do one last memory recycle run.
	struct genericFree *memFree = NULL;
	while ((memFree = (struct genericFree *) utarray_next(mainloopData->memoryToFree, memFree)) != NULL) {
		memFree->func(memFree->memPtr);
	}
	utarray_clear(mainloopData->memoryToFree);

	utarray_free(mainloopData->memoryToFree);

	return (EXIT_SUCCESS);
}

// Only use this inside the mainloop-thread, not inside any other thread,
// like additional data acquisition threads or output threads.
void caerMainloopFreeAfterLoop(void (*func)(void *mem), void *memPtr) {
	caerMainloopData mainloopData = glMainloopData;

	struct genericFree memFree = { .func = func, .memPtr = memPtr };

	utarray_push_back(mainloopData->memoryToFree, &memFree);
}

// Only use this inside the mainloop-thread, not inside any other thread,
// like additional data acquisition threads or output threads.
caerMainloopData caerMainloopGetReference(void) {
	return (glMainloopData);
}

static inline caerModuleData findSourceModule(uint16_t source) {
	caerMainloopData mainloopData = glMainloopData;
	caerModuleData moduleData;

	// This is only ever called from within modules running in a main-loop.
	// So always inside the same thread, needing thus no synchronization.
	HASH_FIND(hh, mainloopData->modules, &source, sizeof(uint16_t), moduleData);

	if (moduleData == NULL) {
		// This is impossible if used correctly, you can't have a packet with
		// an event source X and that event source doesn't exist ...
		caerLog(CAER_LOG_ALERT, sshsNodeGetName(mainloopData->mainloopNode),
			"Impossible to get module data for source ID %" PRIu16 ".", source);
		thrd_exit(EXIT_FAILURE);
	}

	return (moduleData);
}

sshsNode caerMainloopGetSourceInfo(uint16_t source) {
	caerModuleData moduleData = findSourceModule(source);

	// All sources have a sub-node in SSHS called 'sourceInfo/'.
	return (sshsGetRelativeNode(moduleData->moduleNode, "sourceInfo/"));
}

void *caerMainloopGetSourceState(uint16_t source) {
	caerModuleData moduleData = findSourceModule(source);

	return (moduleData->moduleState);
}

static void caerMainloopSignalHandler(int signal) {
	// Simply set the running flag to false on SIGTERM and SIGINT (CTRL+C) for global shutdown.
	if (signal == SIGTERM || signal == SIGINT) {
		atomic_store(&mainloopThreads.running, false);
	}
}

static void caerMainloopShutdownListener(sshsNode node, void *userData, enum sshs_node_attribute_events event,
	const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue) {
	UNUSED_ARGUMENT(node);

	if (event == ATTRIBUTE_MODIFIED && changeType == BOOL && caerStrEquals(changeKey, "shutdown")) {
		// Shutdown changed, let's see.
		if (changeValue.boolean == true) {
			// Shutdown requested!
			atomic_store((atomic_bool * ) userData, false);
		}
	}
}
