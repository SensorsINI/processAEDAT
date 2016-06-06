#include "sshs_internal.h"
#include "ext/slre/slre.h"

struct sshs_struct {
	sshsNode root;
};

static void sshsGlobalInitialize(void);
static void sshsGlobalErrorLogCallbackInitialize(void);
static void sshsGlobalErrorLogCallbackSetInternal(sshsErrorLogCallback error_log_cb);
static void sshsDefaultErrorLogCallback(const char *msg);
static bool sshsCheckAbsoluteNodePath(const char *absolutePath, size_t absolutePathLength);
static bool sshsCheckRelativeNodePath(const char *relativePath, size_t relativePathLength);

static sshs sshsGlobal = NULL;
static once_flag sshsGlobalIsInitialized = ONCE_FLAG_INIT;

static void sshsGlobalInitialize(void) {
	sshsGlobal = sshsNew();
}

sshs sshsGetGlobal(void) {
	call_once(&sshsGlobalIsInitialized, &sshsGlobalInitialize);

	return (sshsGlobal);
}

static sshsErrorLogCallback sshsGlobalErrorLogCallback = NULL;
static once_flag sshsGlobalErrorLogCallbackIsInitialized = ONCE_FLAG_INIT;

static void sshsGlobalErrorLogCallbackInitialize(void) {
	sshsGlobalErrorLogCallbackSetInternal(&sshsDefaultErrorLogCallback);
}

static void sshsGlobalErrorLogCallbackSetInternal(sshsErrorLogCallback error_log_cb) {
	sshsGlobalErrorLogCallback = error_log_cb;

	// sshsErrorLogCallback is compatible to the Mini-XML error logging function.
	mxmlSetErrorCallback(error_log_cb);
}

sshsErrorLogCallback sshsGetGlobalErrorLogCallback(void) {
	call_once(&sshsGlobalErrorLogCallbackIsInitialized, &sshsGlobalErrorLogCallbackInitialize);

	return (sshsGlobalErrorLogCallback);
}

/**
 * This is not thread-safe, and it's not meant to be.
 * Set the global error callback preferably only once, before using SSHS.
 */
void sshsSetGlobalErrorLogCallback(sshsErrorLogCallback error_log_cb) {
	call_once(&sshsGlobalErrorLogCallbackIsInitialized, &sshsGlobalErrorLogCallbackInitialize);

	// If NULL, set to default logging callback.
	if (error_log_cb == NULL) {
		sshsGlobalErrorLogCallbackSetInternal(&sshsDefaultErrorLogCallback);
	}
	else {
		sshsGlobalErrorLogCallbackSetInternal(error_log_cb);
	}
}

sshs sshsNew(void) {
	sshs newSshs = malloc(sizeof(*newSshs));
	SSHS_MALLOC_CHECK_EXIT(newSshs);

	// Create root node.
	newSshs->root = sshsNodeNew("", NULL);

	return (newSshs);
}

bool sshsExistsNode(sshs st, const char *nodePath) {
	size_t nodePathLength = strlen(nodePath);

	if (!sshsCheckAbsoluteNodePath(nodePath, nodePathLength)) {
		return (false);
	}

	// First node is the root.
	sshsNode curr = st->root;

	// Optimization: the root node always exists.
	if (strncmp(nodePath, "/", nodePathLength) == 0) {
		return (true);
	}

	// Create a copy of nodePath, so that strtok_r() can modify it.
	char nodePathCopy[nodePathLength + 1];
	strcpy(nodePathCopy, nodePath);

	// Search (or create) viable node iteratively.
	char *tokenSavePtr = NULL, *nextName = NULL, *currName = nodePathCopy;
	while ((nextName = strtok_r(currName, "/", &tokenSavePtr)) != NULL) {
		sshsNode next = sshsNodeGetChild(curr, nextName);

		// If node doesn't exist, return that.
		if (next == NULL) {
			return (false);
		}

		curr = next;

		currName = NULL;
	}

	// We got to the end, so the node exists.
	return (true);
}

sshsNode sshsGetNode(sshs st, const char *nodePath) {
	size_t nodePathLength = strlen(nodePath);

	if (!sshsCheckAbsoluteNodePath(nodePath, nodePathLength)) {
		return (NULL);
	}

	// First node is the root.
	sshsNode curr = st->root;

	// Optimization: the root node always exists and is right there.
	if (strncmp(nodePath, "/", nodePathLength) == 0) {
		return (curr);
	}

	// Create a copy of nodePath, so that strtok_r() can modify it.
	char nodePathCopy[nodePathLength + 1];
	strcpy(nodePathCopy, nodePath);

	// Search (or create) viable node iteratively.
	char *tokenSavePtr = NULL, *nextName = NULL, *currName = nodePathCopy;
	while ((nextName = strtok_r(currName, "/", &tokenSavePtr)) != NULL) {
		sshsNode next = sshsNodeGetChild(curr, nextName);

		// Create next node in path if not existing.
		if (next == NULL) {
			next = sshsNodeAddChild(curr, nextName);
		}

		curr = next;

		currName = NULL;
	}

	// 'curr' now contains the specified node.
	return (curr);
}

bool sshsExistsRelativeNode(sshsNode node, const char *nodePath) {
	size_t nodePathLength = strlen(nodePath);

	if (!sshsCheckRelativeNodePath(nodePath, nodePathLength)) {
		return (false);
	}

	// Start with the given node.
	sshsNode curr = node;

	// Create a copy of nodePath, so that strtok_r() can modify it.
	char nodePathCopy[nodePathLength + 1];
	strcpy(nodePathCopy, nodePath);

	// Search (or create) viable node iteratively.
	char *tokenSavePtr = NULL, *nextName = NULL, *currName = nodePathCopy;
	while ((nextName = strtok_r(currName, "/", &tokenSavePtr)) != NULL) {
		sshsNode next = sshsNodeGetChild(curr, nextName);

		// If node doesn't exist, return that.
		if (next == NULL) {
			return (false);
		}

		curr = next;

		currName = NULL;
	}

	// We got to the end, so the node exists.
	return (true);
}

sshsNode sshsGetRelativeNode(sshsNode node, const char *nodePath) {
	size_t nodePathLength = strlen(nodePath);

	if (!sshsCheckRelativeNodePath(nodePath, nodePathLength)) {
		return (NULL);
	}

	// Start with the given node.
	sshsNode curr = node;

	// Create a copy of nodePath, so that strtok_r() can modify it.
	char nodePathCopy[nodePathLength + 1];
	strcpy(nodePathCopy, nodePath);

	// Search (or create) viable node iteratively.
	char *tokenSavePtr = NULL, *nextName = NULL, *currName = nodePathCopy;
	while ((nextName = strtok_r(currName, "/", &tokenSavePtr)) != NULL) {
		sshsNode next = sshsNodeGetChild(curr, nextName);

		// Create next node in path if not existing.
		if (next == NULL) {
			next = sshsNodeAddChild(curr, nextName);
		}

		curr = next;

		currName = NULL;
	}

	// 'curr' now contains the specified node.
	return (curr);
}

bool sshsBeginTransaction(sshs st, char *nodePaths[], size_t nodePathsLength) {
	// Check all node paths, then lock them.
	for (size_t i = 0; i < nodePathsLength; i++) {
		if (!sshsCheckAbsoluteNodePath(nodePaths[i], strlen(nodePaths[i]))) {
			return (false);
		}
	}

	for (size_t i = 0; i < nodePathsLength; i++) {
		sshsNodeTransactionLock(sshsGetNode(st, nodePaths[i]));
	}

	return (true);
}

bool sshsEndTransaction(sshs st, char *nodePaths[], size_t nodePathsLength) {
	// Check all node paths, then unlock them.
	for (size_t i = 0; i < nodePathsLength; i++) {
		if (!sshsCheckAbsoluteNodePath(nodePaths[i], strlen(nodePaths[i]))) {
			return (false);
		}
	}

	for (size_t i = 0; i < nodePathsLength; i++) {
		sshsNodeTransactionUnlock(sshsGetNode(st, nodePaths[i]));
	}

	return (true);
}

#define ALLOWED_CHARS_REGEXP "([a-zA-Z-_\\d\\.:\\(\\)\\[\\]{}]+/)"
static const char *sshsAbsoluteNodePathRegexp = "^/" ALLOWED_CHARS_REGEXP "*$";
static const char *sshsRelativeNodePathRegexp = "^" ALLOWED_CHARS_REGEXP "+$";

static bool sshsCheckAbsoluteNodePath(const char *absolutePath, size_t absolutePathLength) {
	if (absolutePath == NULL || absolutePathLength == 0) {
		(*sshsGetGlobalErrorLogCallback())("Node path cannot be null.");
		return (false);
	}

	if (slre_match(sshsAbsoluteNodePathRegexp, absolutePath, (int) absolutePathLength, NULL, 0, 0) <= 0) {
		(*sshsGetGlobalErrorLogCallback())("Invalid absolute node path format.");
		return (false);
	}

	return (true);
}

static bool sshsCheckRelativeNodePath(const char *relativePath, size_t relativePathLength) {
	if (relativePath == NULL || relativePathLength == 0) {
		(*sshsGetGlobalErrorLogCallback())("Node path cannot be null.");
		return (false);
	}

	if (slre_match(sshsRelativeNodePathRegexp, relativePath, (int) relativePathLength, NULL, 0, 0) <= 0) {
		(*sshsGetGlobalErrorLogCallback())("Invalid relative node path format.");
		return (false);
	}

	return (true);
}

static void sshsDefaultErrorLogCallback(const char *msg) {
	fprintf(stderr, "%s\n", msg);
}
