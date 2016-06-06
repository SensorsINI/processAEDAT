#include "sshs_internal.h"
#include "ext/uthash/uthash.h"
#include "ext/uthash/utlist.h"

struct sshs_node {
	char *name;
	char *path;
	sshsNode parent;
	sshsNode children;
	sshsNodeAttr attributes;
	sshsNodeListener nodeListeners;
	sshsNodeAttrListener attrListeners;
	mtx_shared_t traversal_lock;
	mtx_shared_t node_lock;
	UT_hash_handle hh;
};

struct sshs_node_attr {
	UT_hash_handle hh;
	union sshs_node_attr_value value;
	enum sshs_node_attr_value_type value_type;
	char key[];
};

struct sshs_node_listener {
	void (*node_changed)(sshsNode node, void *userData, enum sshs_node_node_events event, sshsNode changeNode);
	void *userData;
	sshsNodeListener next;
};

struct sshs_node_attr_listener {
	void (*attribute_changed)(sshsNode node, void *userData, enum sshs_node_attribute_events event,
		const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue);
	void *userData;
	sshsNodeAttrListener next;
};

static bool sshsNodePutAttributeIfAbsent(sshsNode node, const char *key, enum sshs_node_attr_value_type type,
	union sshs_node_attr_value value);
static void sshsNodePutAttribute(sshsNode node, const char *key, enum sshs_node_attr_value_type type,
	union sshs_node_attr_value value);
static bool sshsNodeCheckAttributeValueChanged(enum sshs_node_attr_value_type type, union sshs_node_attr_value oldValue,
	union sshs_node_attr_value newValue);
static sshsNodeAttr *sshsNodeGetAttributes(sshsNode node, size_t *numAttributes);
static const char *sshsNodeXMLWhitespaceCallback(mxml_node_t *node, int where);
static void sshsNodeToXML(sshsNode node, int outFd, bool recursive, const char **filterKeys, size_t filterKeysLength,
	const char **filterNodes, size_t filterNodesLength);
static mxml_node_t *sshsNodeGenerateXML(sshsNode node, bool recursive, const char **filterKeys, size_t filterKeysLength,
	const char **filterNodes, size_t filterNodesLength);
static mxml_node_t **sshsNodeXMLFilterChildNodes(mxml_node_t *node, const char *nodeName, size_t *numChildren);
static bool sshsNodeFromXML(sshsNode node, int inFd, bool recursive, bool strict);
static void sshsNodeConsumeXML(sshsNode node, mxml_node_t *content, bool recursive);

sshsNode sshsNodeNew(const char *nodeName, sshsNode parent) {
	sshsNode newNode = malloc(sizeof(*newNode));
	SSHS_MALLOC_CHECK_EXIT(newNode);
	memset(newNode, 0, sizeof(*newNode));

	// Allocate full copy of string, so that we control the memory.
	size_t nameLength = strlen(nodeName);
	newNode->name = malloc(nameLength + 1);
	SSHS_MALLOC_CHECK_EXIT(newNode->name);

	// Copy the string.
	strcpy(newNode->name, nodeName);

	newNode->parent = parent;
	newNode->children = NULL;
	newNode->attributes = NULL;
	newNode->nodeListeners = NULL;
	newNode->attrListeners = NULL;

	if (mtx_shared_init(&newNode->traversal_lock) != thrd_success) {
		// Locks are critical for thread-safety.
		(*sshsGetGlobalErrorLogCallback())("Failed to initialize traversal_lock.");
		exit(EXIT_FAILURE);
	}
	if (mtx_shared_init(&newNode->node_lock) != thrd_success) {
		// Locks are critical for thread-safety.
		(*sshsGetGlobalErrorLogCallback())("Failed to initialize node_lock.");
		exit(EXIT_FAILURE);
	}

	// Path is based on parent.
	if (parent != NULL) {
		// Either allocate string copy for full path.
		size_t pathLength = strlen(sshsNodeGetPath(parent)) + nameLength + 1; // + 1 for trailing slash
		newNode->path = malloc(pathLength + 1);
		SSHS_MALLOC_CHECK_EXIT(newNode->path);

		// Generate string.
		snprintf(newNode->path, pathLength + 1, "%s%s/", sshsNodeGetPath(parent), nodeName);
	}
	else {
		// Or the root has an empty, constant path.
		newNode->path = "/";
	}

	return (newNode);
}

const char *sshsNodeGetName(sshsNode node) {
	return (node->name);
}

const char *sshsNodeGetPath(sshsNode node) {
	return (node->path);
}

sshsNode sshsNodeGetParent(sshsNode node) {
	return (node->parent);
}

sshsNode sshsNodeAddChild(sshsNode node, const char *childName) {
	mtx_shared_lock_exclusive(&node->traversal_lock);

	// Atomic putIfAbsent: returns null if nothing was there before and the
	// node is the new one, or it returns the old node if already present.
	sshsNode child = NULL, newChild = NULL;
	HASH_FIND_STR(node->children, childName, child);

	if (child == NULL) {
		// Create new child node with appropriate name and parent.
		newChild = sshsNodeNew(childName, node);

		// No node present, let's add it.
		HASH_ADD_KEYPTR(hh, node->children, sshsNodeGetName(newChild), strlen(sshsNodeGetName(newChild)), newChild);
	}

	mtx_shared_unlock_exclusive(&node->traversal_lock);

	// If null was returned, then nothing was in the map beforehand, and
	// thus the new node 'child' is the node that's now in the map.
	if (child == NULL) {
		// Listener support (only on new addition!).
		mtx_shared_lock_shared(&node->node_lock);

		sshsNodeListener l;
		LL_FOREACH(node->nodeListeners, l)
		{
			l->node_changed(node, l->userData, CHILD_NODE_ADDED, newChild);
		}

		mtx_shared_unlock_shared(&node->node_lock);

		return (newChild);
	}

	return (child);
}

sshsNode sshsNodeGetChild(sshsNode node, const char* childName) {
	mtx_shared_lock_shared(&node->traversal_lock);

	sshsNode child;
	HASH_FIND_STR(node->children, childName, child);

	mtx_shared_unlock_shared(&node->traversal_lock);

	// Either null or an always valid value.
	return (child);
}

static int sshsNodeCmp(const void *a, const void *b) {
	const sshsNode *aa = a;
	const sshsNode *bb = b;

	return (strcmp(sshsNodeGetName(*aa), sshsNodeGetName(*bb)));
}

sshsNode *sshsNodeGetChildren(sshsNode node, size_t *numChildren) {
	mtx_shared_lock_shared(&node->traversal_lock);

	size_t childrenCount = HASH_COUNT(node->children);

	// If none, exit gracefully.
	if (childrenCount == 0) {
		mtx_shared_unlock_shared(&node->traversal_lock);

		*numChildren = 0;
		return (NULL);
	}

	sshsNode *children = malloc(childrenCount * sizeof(*children));
	SSHS_MALLOC_CHECK_EXIT(children);

	size_t i = 0;
	for (sshsNode n = node->children; n != NULL; n = n->hh.next) {
		children[i++] = n;
	}

	mtx_shared_unlock_shared(&node->traversal_lock);

	// Sort by name.
	qsort(children, childrenCount, sizeof(sshsNode), &sshsNodeCmp);

	*numChildren = childrenCount;
	return (children);
}

void sshsNodeAddNodeListener(sshsNode node, void *userData,
	void (*node_changed)(sshsNode node, void *userData, enum sshs_node_node_events event, sshsNode changeNode)) {
	sshsNodeListener listener = malloc(sizeof(*listener));
	SSHS_MALLOC_CHECK_EXIT(listener);

	listener->node_changed = node_changed;
	listener->userData = userData;

	mtx_shared_lock_exclusive(&node->node_lock);

	// Search if we don't already have this exact listener, to avoid duplicates.
	bool found = false;

	sshsNodeListener curr;
	LL_FOREACH(node->nodeListeners, curr)
	{
		if (curr->node_changed == node_changed && curr->userData == userData) {
			found = true;
		}
	}

	if (!found) {
		LL_PREPEND(node->nodeListeners, listener);
	}
	else {
		free(listener);
	}

	mtx_shared_unlock_exclusive(&node->node_lock);
}

void sshsNodeRemoveNodeListener(sshsNode node, void *userData,
	void (*node_changed)(sshsNode node, void *userData, enum sshs_node_node_events event, sshsNode changeNode)) {
	mtx_shared_lock_exclusive(&node->node_lock);

	sshsNodeListener curr, curr_tmp;
	LL_FOREACH_SAFE(node->nodeListeners, curr, curr_tmp)
	{
		if (curr->node_changed == node_changed && curr->userData == userData) {
			LL_DELETE(node->nodeListeners, curr);
			free(curr);
		}
	}

	mtx_shared_unlock_exclusive(&node->node_lock);
}

void sshsNodeRemoveAllNodeListeners(sshsNode node) {
	mtx_shared_lock_exclusive(&node->node_lock);

	sshsNodeListener curr, curr_tmp;
	LL_FOREACH_SAFE(node->nodeListeners, curr, curr_tmp)
	{
		LL_DELETE(node->nodeListeners, curr);
		free(curr);
	}

	mtx_shared_unlock_exclusive(&node->node_lock);
}

void sshsNodeAddAttributeListener(sshsNode node, void *userData,
	void (*attribute_changed)(sshsNode node, void *userData, enum sshs_node_attribute_events event,
		const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue)) {
	sshsNodeAttrListener listener = malloc(sizeof(*listener));
	SSHS_MALLOC_CHECK_EXIT(listener);

	listener->attribute_changed = attribute_changed;
	listener->userData = userData;

	mtx_shared_lock_exclusive(&node->node_lock);

	// Search if we don't already have this exact listener, to avoid duplicates.
	bool found = false;

	sshsNodeAttrListener curr;
	LL_FOREACH(node->attrListeners, curr)
	{
		if (curr->attribute_changed == attribute_changed && curr->userData == userData) {
			found = true;
		}
	}

	if (!found) {
		LL_PREPEND(node->attrListeners, listener);
	}
	else {
		free(listener);
	}

	mtx_shared_unlock_exclusive(&node->node_lock);
}

void sshsNodeRemoveAttributeListener(sshsNode node, void *userData,
	void (*attribute_changed)(sshsNode node, void *userData, enum sshs_node_attribute_events event,
		const char *changeKey, enum sshs_node_attr_value_type changeType, union sshs_node_attr_value changeValue)) {
	mtx_shared_lock_exclusive(&node->node_lock);

	sshsNodeAttrListener curr, curr_tmp;
	LL_FOREACH_SAFE(node->attrListeners, curr, curr_tmp)
	{
		if (curr->attribute_changed == attribute_changed && curr->userData == userData) {
			LL_DELETE(node->attrListeners, curr);
			free(curr);
		}
	}

	mtx_shared_unlock_exclusive(&node->node_lock);
}

void sshsNodeRemoveAllAttributeListeners(sshsNode node) {
	mtx_shared_lock_exclusive(&node->node_lock);

	sshsNodeAttrListener curr, curr_tmp;
	LL_FOREACH_SAFE(node->attrListeners, curr, curr_tmp)
	{
		LL_DELETE(node->attrListeners, curr);
		free(curr);
	}

	mtx_shared_unlock_exclusive(&node->node_lock);
}

void sshsNodeTransactionLock(sshsNode node) {
	mtx_shared_lock_exclusive(&node->node_lock);
}

void sshsNodeTransactionUnlock(sshsNode node) {
	mtx_shared_unlock_exclusive(&node->node_lock);
}

bool sshsNodeAttributeExists(sshsNode node, const char *key, enum sshs_node_attr_value_type type) {
	size_t keyLength = strlen(key);
	sshsNodeAttr lookupAttr = malloc(sizeof(*lookupAttr) + keyLength + 1);
	SSHS_MALLOC_CHECK_EXIT(lookupAttr);
	memset(lookupAttr, 0, sizeof(*lookupAttr));

	lookupAttr->value_type = type;
	strcpy(lookupAttr->key, key);

	size_t fullKeyLength = offsetof(struct sshs_node_attr, key) + keyLength
		+ 1- offsetof(struct sshs_node_attr, value_type);

	mtx_shared_lock_shared(&node->node_lock);

	sshsNodeAttr attr;
	HASH_FIND(hh, node->attributes, &lookupAttr->value_type, fullKeyLength, attr);

	mtx_shared_unlock_shared(&node->node_lock);

	// Free lookup key again.
	free(lookupAttr);

	// If attr == NULL, the specified attribute was not found.
	if (attr == NULL) {
		return (false);
	}

	// The specified attribute exists.
	return (true);
}

static bool sshsNodePutAttributeIfAbsent(sshsNode node, const char *key, enum sshs_node_attr_value_type type,
	union sshs_node_attr_value value) {
	size_t keyLength = strlen(key);
	sshsNodeAttr newAttr = malloc(sizeof(*newAttr) + keyLength + 1);
	SSHS_MALLOC_CHECK_EXIT(newAttr);
	memset(newAttr, 0, sizeof(*newAttr));

	if (type == STRING) {
		// Make a copy of the string so we own the memory internally.
		char *valueCopy = strdup(value.string);
		SSHS_MALLOC_CHECK_EXIT(valueCopy);

		newAttr->value.string = valueCopy;
	}
	else {
		newAttr->value = value;
	}

	newAttr->value_type = type;
	strcpy(newAttr->key, key);

	size_t fullKeyLength = offsetof(struct sshs_node_attr, key) + keyLength
		+ 1- offsetof(struct sshs_node_attr, value_type);

	mtx_shared_lock_exclusive(&node->node_lock);

	sshsNodeAttr oldAttr;
	HASH_FIND(hh, node->attributes, &newAttr->value_type, fullKeyLength, oldAttr);

	// Only add if not present.
	if (oldAttr == NULL) {
		HASH_ADD(hh, node->attributes, value_type, fullKeyLength, newAttr);
	}

	mtx_shared_unlock_exclusive(&node->node_lock);

	if (oldAttr == NULL) {
		// Listener support. Call only on change, which is always the case here.
		mtx_shared_lock_shared(&node->node_lock);

		sshsNodeAttrListener l;
		LL_FOREACH(node->attrListeners, l)
		{
			l->attribute_changed(node, l->userData, ATTRIBUTE_ADDED, key, type, value);
		}

		mtx_shared_unlock_shared(&node->node_lock);

		return (true);
	}
	else {
		// Free lookup memory, if not added to table.
		if (type == STRING) {
			free((newAttr->value).string);
		}

		free(newAttr);

		return (false);
	}
}

static void sshsNodePutAttribute(sshsNode node, const char *key, enum sshs_node_attr_value_type type,
	union sshs_node_attr_value value) {
	size_t keyLength = strlen(key);
	sshsNodeAttr newAttr = malloc(sizeof(*newAttr) + keyLength + 1);
	SSHS_MALLOC_CHECK_EXIT(newAttr);
	memset(newAttr, 0, sizeof(*newAttr));

	if (type == STRING) {
		// Make a copy of the string so we own the memory internally.
		char *valueCopy = strdup(value.string);
		SSHS_MALLOC_CHECK_EXIT(valueCopy);

		newAttr->value.string = valueCopy;
	}
	else {
		newAttr->value = value;
	}

	newAttr->value_type = type;
	strcpy(newAttr->key, key);

	size_t fullKeyLength = offsetof(struct sshs_node_attr, key) + keyLength
		+ 1- offsetof(struct sshs_node_attr, value_type);

	mtx_shared_lock_exclusive(&node->node_lock);

	sshsNodeAttr oldAttr;
	union sshs_node_attr_value oldAttrValue = { .ilong = 0 };

	HASH_FIND(hh, node->attributes, &newAttr->value_type, fullKeyLength, oldAttr);

	// If not present, add the new one, else update the old one.
	if (oldAttr == NULL) {
		HASH_ADD(hh, node->attributes, value_type, fullKeyLength, newAttr);
	}
	else {
		// Key and valueType have to be the same, so only update the value
		// itself with the new one, and save the old one for later.
		oldAttrValue = oldAttr->value;
		oldAttr->value = newAttr->value;
	}

	mtx_shared_unlock_exclusive(&node->node_lock);

	if (oldAttr == NULL) {
		// Listener support. Call only on change, which is always the case here.
		mtx_shared_lock_shared(&node->node_lock);

		sshsNodeAttrListener l;
		LL_FOREACH(node->attrListeners, l)
		{
			l->attribute_changed(node, l->userData, ATTRIBUTE_ADDED, key, type, value);
		}

		mtx_shared_unlock_shared(&node->node_lock);
	}
	else {
		// Let's check if anything changed with this update and call
		// the appropriate listeners if needed.
		if (sshsNodeCheckAttributeValueChanged(type, oldAttrValue, value)) {
			// Listener support. Call only on change, which is always the case here.
			mtx_shared_lock_shared(&node->node_lock);

			sshsNodeAttrListener l;
			LL_FOREACH(node->attrListeners, l)
			{
				l->attribute_changed(node, l->userData, ATTRIBUTE_MODIFIED, key, type, value);
			}

			mtx_shared_unlock_shared(&node->node_lock);
		}

		// Free newAttr memory, if not added to table.
		// Free also oldAttr's string memory, not newAttr's one, since that
		// is now being used by oldAttr instead.
		if (type == STRING) {
			free(oldAttrValue.string);
		}

		free(newAttr);
	}
}

static bool sshsNodeCheckAttributeValueChanged(enum sshs_node_attr_value_type type, union sshs_node_attr_value oldValue,
	union sshs_node_attr_value newValue) {
	// Check that the two values changed, that there is a difference between then.
	switch (type) {
		case BOOL:
			return (oldValue.boolean != newValue.boolean);

		case BYTE:
			return (oldValue.ibyte != newValue.ibyte);

		case SHORT:
			return (oldValue.ishort != newValue.ishort);

		case INT:
			return (oldValue.iint != newValue.iint);

		case LONG:
			return (oldValue.ilong != newValue.ilong);

		case FLOAT:
			return (oldValue.ffloat != newValue.ffloat);

		case DOUBLE:
			return (oldValue.ddouble != newValue.ddouble);

		case STRING:
			return (strcmp(oldValue.string, newValue.string) != 0);

		default:
			return (false);
	}
}

union sshs_node_attr_value sshsNodeGetAttribute(sshsNode node, const char *key, enum sshs_node_attr_value_type type) {
	size_t keyLength = strlen(key);
	sshsNodeAttr lookupAttr = malloc(sizeof(*lookupAttr) + keyLength + 1);
	SSHS_MALLOC_CHECK_EXIT(lookupAttr);
	memset(lookupAttr, 0, sizeof(*lookupAttr));

	lookupAttr->value_type = type;
	strcpy(lookupAttr->key, key);

	size_t fullKeyLength = offsetof(struct sshs_node_attr, key) + keyLength
		+ 1- offsetof(struct sshs_node_attr, value_type);

	mtx_shared_lock_shared(&node->node_lock);

	sshsNodeAttr attr;
	HASH_FIND(hh, node->attributes, &lookupAttr->value_type, fullKeyLength, attr);

	// Copy the value while still holding the lock, to ensure accessing it is
	// still possible and the value behind it valid.
	union sshs_node_attr_value value = { .ilong = 0 };
	if (attr != NULL) {
		value = attr->value;

		// For strings, make a copy on the heap to give out.
		if (type == STRING) {
			char *valueCopy = strdup(value.string);
			SSHS_MALLOC_CHECK_EXIT(valueCopy);

			value.string = valueCopy;
		}
	}

	mtx_shared_unlock_shared(&node->node_lock);

	// Free lookup key again.
	free(lookupAttr);

	// Verify that we're getting values from a valid attribute.
	// Valid means it already exists and has a well-defined default.
	if (attr == NULL) {
		char errorMsg[1024];
		snprintf(errorMsg, 1024, "Attribute '%s' of type '%s' not present, please initialize it first.", key,
			sshsHelperTypeToStringConverter(type));

		(*sshsGetGlobalErrorLogCallback())(errorMsg);

		// This is a critical usage error that *must* be fixed!
		exit(EXIT_FAILURE);
	}

	// Return the final value.
	return (value);
}

static int sshsNodeAttrCmp(const void *a, const void *b) {
	const sshsNodeAttr *aa = a;
	const sshsNodeAttr *bb = b;

	return (strcmp((*aa)->key, (*bb)->key));
}

static sshsNodeAttr *sshsNodeGetAttributes(sshsNode node, size_t *numAttributes) {
	mtx_shared_lock_shared(&node->node_lock);

	size_t attributeCount = HASH_COUNT(node->attributes);

	// If none, exit gracefully.
	if (attributeCount == 0) {
		mtx_shared_unlock_shared(&node->node_lock);

		*numAttributes = 0;
		return (NULL);
	}

	sshsNodeAttr *attributes = malloc(attributeCount * sizeof(*attributes));
	SSHS_MALLOC_CHECK_EXIT(attributes);

	size_t i = 0;
	for (sshsNodeAttr a = node->attributes; a != NULL; a = a->hh.next) {
		attributes[i++] = a;
	}

	mtx_shared_unlock_shared(&node->node_lock);

	// Sort by name.
	qsort(attributes, attributeCount, sizeof(sshsNodeAttr), &sshsNodeAttrCmp);

	*numAttributes = attributeCount;
	return (attributes);
}

bool sshsNodePutBoolIfAbsent(sshsNode node, const char *key, bool value) {
	return (sshsNodePutAttributeIfAbsent(node, key, BOOL, (union sshs_node_attr_value ) { .boolean = value }));
}

void sshsNodePutBool(sshsNode node, const char *key, bool value) {
	sshsNodePutAttribute(node, key, BOOL, (union sshs_node_attr_value ) { .boolean = value });
}

bool sshsNodeGetBool(sshsNode node, const char *key) {
	return (sshsNodeGetAttribute(node, key, BOOL).boolean);
}

bool sshsNodePutByteIfAbsent(sshsNode node, const char *key, int8_t value) {
	return (sshsNodePutAttributeIfAbsent(node, key, BYTE, (union sshs_node_attr_value ) { .ibyte = value }));
}

void sshsNodePutByte(sshsNode node, const char *key, int8_t value) {
	sshsNodePutAttribute(node, key, BYTE, (union sshs_node_attr_value ) { .ibyte = value });
}

int8_t sshsNodeGetByte(sshsNode node, const char *key) {
	return (sshsNodeGetAttribute(node, key, BYTE).ibyte);
}

bool sshsNodePutShortIfAbsent(sshsNode node, const char *key, int16_t value) {
	return (sshsNodePutAttributeIfAbsent(node, key, SHORT, (union sshs_node_attr_value ) { .ishort = value }));
}

void sshsNodePutShort(sshsNode node, const char *key, int16_t value) {
	sshsNodePutAttribute(node, key, SHORT, (union sshs_node_attr_value ) { .ishort = value });
}

int16_t sshsNodeGetShort(sshsNode node, const char *key) {
	return (sshsNodeGetAttribute(node, key, SHORT).ishort);
}

bool sshsNodePutIntIfAbsent(sshsNode node, const char *key, int32_t value) {
	return (sshsNodePutAttributeIfAbsent(node, key, INT, (union sshs_node_attr_value ) { .iint = value }));
}

void sshsNodePutInt(sshsNode node, const char *key, int32_t value) {
	sshsNodePutAttribute(node, key, INT, (union sshs_node_attr_value ) { .iint = value });
}

int32_t sshsNodeGetInt(sshsNode node, const char *key) {
	return (sshsNodeGetAttribute(node, key, INT).iint);
}

bool sshsNodePutLongIfAbsent(sshsNode node, const char *key, int64_t value) {
	return (sshsNodePutAttributeIfAbsent(node, key, LONG, (union sshs_node_attr_value ) { .ilong = value }));
}

void sshsNodePutLong(sshsNode node, const char *key, int64_t value) {
	sshsNodePutAttribute(node, key, LONG, (union sshs_node_attr_value ) { .ilong = value });
}

int64_t sshsNodeGetLong(sshsNode node, const char *key) {
	return (sshsNodeGetAttribute(node, key, LONG).ilong);
}

bool sshsNodePutFloatIfAbsent(sshsNode node, const char *key, float value) {
	return (sshsNodePutAttributeIfAbsent(node, key, FLOAT, (union sshs_node_attr_value ) { .ffloat = value }));
}

void sshsNodePutFloat(sshsNode node, const char *key, float value) {
	sshsNodePutAttribute(node, key, FLOAT, (union sshs_node_attr_value ) { .ffloat = value });
}

float sshsNodeGetFloat(sshsNode node, const char *key) {
	return (sshsNodeGetAttribute(node, key, FLOAT).ffloat);
}

bool sshsNodePutDoubleIfAbsent(sshsNode node, const char *key, double value) {
	return (sshsNodePutAttributeIfAbsent(node, key, DOUBLE, (union sshs_node_attr_value ) { .ddouble = value }));
}

void sshsNodePutDouble(sshsNode node, const char *key, double value) {
	sshsNodePutAttribute(node, key, DOUBLE, (union sshs_node_attr_value ) { .ddouble = value });
}

double sshsNodeGetDouble(sshsNode node, const char *key) {
	return (sshsNodeGetAttribute(node, key, DOUBLE).ddouble);
}

bool sshsNodePutStringIfAbsent(sshsNode node, const char *key, const char *value) {
	return (sshsNodePutAttributeIfAbsent(node, key, STRING, (union sshs_node_attr_value ) { .string = value }));
}

void sshsNodePutString(sshsNode node, const char *key, const char *value) {
	sshsNodePutAttribute(node, key, STRING, (union sshs_node_attr_value ) { .string = value });
}

// This is a copy of the string on the heap, remember to free() when done!
char *sshsNodeGetString(sshsNode node, const char *key) {
	return (sshsNodeGetAttribute(node, key, STRING).string);
}

void sshsNodeExportNodeToXML(sshsNode node, int outFd, const char **filterKeys, size_t filterKeysLength) {
	sshsNodeToXML(node, outFd, false, filterKeys, filterKeysLength, NULL, 0);
}

void sshsNodeExportSubTreeToXML(sshsNode node, int outFd, const char **filterKeys, size_t filterKeysLength,
	const char **filterNodes, size_t filterNodesLength) {
	sshsNodeToXML(node, outFd, true, filterKeys, filterKeysLength, filterNodes, filterNodesLength);
}

#define INDENT_MAX_LEVEL 20
#define INDENT_SPACES 4
static char spaces[(INDENT_MAX_LEVEL * INDENT_SPACES) + 1] =
	"                                                                                ";

static const char *sshsNodeXMLWhitespaceCallback(mxml_node_t *node, int where) {
	const char *name = mxmlGetElement(node);
	size_t level = 0;

	// Calculate indentation level always.
	for (mxml_node_t *parent = mxmlGetParent(node); parent != NULL; parent = mxmlGetParent(parent)) {
		level++;
	}

	// Clip indentation level to maximum.
	if (level > INDENT_MAX_LEVEL) {
		level = INDENT_MAX_LEVEL;
	}

	if (strcmp(name, "sshs") == 0) {
		switch (where) {
			case MXML_WS_AFTER_OPEN:
				return ("\n");
				break;

			case MXML_WS_AFTER_CLOSE:
				return ("\n");
				break;

			default:
				break;
		}
	}
	else if (strcmp(name, "node") == 0) {
		switch (where) {
			case MXML_WS_BEFORE_OPEN:
				return (&spaces[((INDENT_MAX_LEVEL - level) * INDENT_SPACES)]);
				break;

			case MXML_WS_AFTER_OPEN:
				return ("\n");
				break;

			case MXML_WS_BEFORE_CLOSE:
				return (&spaces[((INDENT_MAX_LEVEL - level) * INDENT_SPACES)]);
				break;

			case MXML_WS_AFTER_CLOSE:
				return ("\n");
				break;

			default:
				break;
		}
	}
	else if (strcmp(name, "attr") == 0) {
		switch (where) {
			case MXML_WS_BEFORE_OPEN:
				return (&spaces[((INDENT_MAX_LEVEL - level) * INDENT_SPACES)]);
				break;

			case MXML_WS_AFTER_CLOSE:
				return ("\n");
				break;

			default:
				break;
		}
	}

	return (NULL);
}

static void sshsNodeToXML(sshsNode node, int outFd, bool recursive, const char **filterKeys, size_t filterKeysLength,
	const char **filterNodes, size_t filterNodesLength) {
	mxml_node_t *root = mxmlNewElement(MXML_NO_PARENT, "sshs");
	mxmlElementSetAttr(root, "version", "1.0");
	mxmlAdd(root, MXML_ADD_AFTER, MXML_ADD_TO_PARENT,
		sshsNodeGenerateXML(node, recursive, filterKeys, filterKeysLength, filterNodes, filterNodesLength));

	// Disable wrapping
	mxmlSetWrapMargin(0);

	// Output to file descriptor.
	mxmlSaveFd(root, outFd, &sshsNodeXMLWhitespaceCallback);

	mxmlDelete(root);
}

static mxml_node_t *sshsNodeGenerateXML(sshsNode node, bool recursive, const char **filterKeys, size_t filterKeysLength,
	const char **filterNodes, size_t filterNodesLength) {
	mxml_node_t *this = mxmlNewElement(MXML_NO_PARENT, "node");

	// First this node's name and full path.
	mxmlElementSetAttr(this, "name", sshsNodeGetName(node));
	mxmlElementSetAttr(this, "path", sshsNodeGetPath(node));

	size_t numAttributes;
	sshsNodeAttr *attributes = sshsNodeGetAttributes(node, &numAttributes);

	// Then it's attributes (key:value pairs).
	for (size_t i = 0; i < numAttributes; i++) {
		bool isFilteredOut = false;

		// Verify that the key is not filtered out.
		for (size_t fk = 0; fk < filterKeysLength; fk++) {
			if (strcmp(attributes[i]->key, filterKeys[fk]) == 0) {
				// Matches, don't add this attribute.
				isFilteredOut = true;
				break;
			}
		}

		if (isFilteredOut) {
			continue;
		}

		const char *type = sshsHelperTypeToStringConverter(attributes[i]->value_type);
		char *value = sshsHelperValueToStringConverter(attributes[i]->value_type, attributes[i]->value);
		SSHS_MALLOC_CHECK_EXIT(value);

		mxml_node_t *attr = mxmlNewElement(this, "attr");
		mxmlElementSetAttr(attr, "key", attributes[i]->key);
		mxmlElementSetAttr(attr, "type", type);
		mxmlNewText(attr, 0, value);

		free(value);
	}

	free(attributes);

	// And lastly recurse down to the children.
	if (recursive) {
		size_t numChildren;
		sshsNode *children = sshsNodeGetChildren(node, &numChildren);

		for (size_t i = 0; i < numChildren; i++) {
			// First check that this child node is not filtered out.
			bool isFilteredOut = false;

			// Verify that the node is not filtered out.
			for (size_t fn = 0; fn < filterNodesLength; fn++) {
				if (strcmp(sshsNodeGetName(children[i]), filterNodes[fn]) == 0) {
					// Matches, don't process this node.
					isFilteredOut = true;
					break;
				}
			}

			if (isFilteredOut) {
				continue;
			}

			mxml_node_t *child = sshsNodeGenerateXML(children[i], recursive, filterKeys, filterKeysLength, filterNodes,
				filterNodesLength);

			if (mxmlGetFirstChild(child) != NULL) {
				mxmlAdd(this, MXML_ADD_AFTER, MXML_ADD_TO_PARENT, child);
			}
			else {
				// Free memory if not adding.
				mxmlDelete(child);
			}
		}

		free(children);
	}

	return (this);
}

bool sshsNodeImportNodeFromXML(sshsNode node, int inFd, bool strict) {
	return (sshsNodeFromXML(node, inFd, false, strict));
}

bool sshsNodeImportSubTreeFromXML(sshsNode node, int inFd, bool strict) {
	return (sshsNodeFromXML(node, inFd, true, strict));
}

static mxml_node_t **sshsNodeXMLFilterChildNodes(mxml_node_t *node, const char *nodeName, size_t *numChildren) {
	// Go through once to count the number of matching children.
	size_t matchedChildren = 0;

	for (mxml_node_t *current = mxmlGetFirstChild(node); current != NULL; current = mxmlGetNextSibling(current)) {
		const char *name = mxmlGetElement(current);

		if (name != NULL && strcmp(name, nodeName) == 0) {
			matchedChildren++;
		}
	}

	// If none, exit gracefully.
	if (matchedChildren == 0) {
		*numChildren = 0;
		return (NULL);
	}

	// Now allocate appropriate memory for list.
	mxml_node_t **filteredNodes = malloc(matchedChildren * sizeof(mxml_node_t *));
	SSHS_MALLOC_CHECK_EXIT(filteredNodes);

	// Go thorough again and collect the matching nodes.
	size_t i = 0;
	for (mxml_node_t *current = mxmlGetFirstChild(node); current != NULL; current = mxmlGetNextSibling(current)) {
		const char *name = mxmlGetElement(current);

		if (name != NULL && strcmp(name, nodeName) == 0) {
			filteredNodes[i++] = current;
		}
	}

	*numChildren = matchedChildren;
	return (filteredNodes);
}

static bool sshsNodeFromXML(sshsNode node, int inFd, bool recursive, bool strict) {
	mxml_node_t *root = mxmlLoadFd(NULL, inFd, MXML_OPAQUE_CALLBACK);

	if (root == NULL) {
		(*sshsGetGlobalErrorLogCallback())("Failed to load XML from file descriptor.");
		return (false);
	}

	// Check name and version for compliance.
	if ((strcmp(mxmlGetElement(root), "sshs") != 0) || (strcmp(mxmlElementGetAttr(root, "version"), "1.0") != 0)) {
		mxmlDelete(root);
		(*sshsGetGlobalErrorLogCallback())("Invalid SSHS v1.0 XML content.");
		return (false);
	}

	size_t numChildren = 0;
	mxml_node_t **children = sshsNodeXMLFilterChildNodes(root, "node", &numChildren);

	if (numChildren != 1) {
		mxmlDelete(root);
		free(children);
		(*sshsGetGlobalErrorLogCallback())("Multiple or no root child nodes present.");
		return (false);
	}

	mxml_node_t *rootNode = children[0];

	free(children);

	// Strict mode: check if names match.
	if (strict) {
		const char *rootNodeName = mxmlElementGetAttr(rootNode, "name");

		if (rootNodeName == NULL || strcmp(rootNodeName, sshsNodeGetName(node)) != 0) {
			mxmlDelete(root);
			(*sshsGetGlobalErrorLogCallback())("Names don't match (required in 'strict' mode).");
			return (false);
		}
	}

	sshsNodeConsumeXML(node, rootNode, recursive);

	mxmlDelete(root);

	return (true);
}

static void sshsNodeConsumeXML(sshsNode node, mxml_node_t *content, bool recursive) {
	size_t numAttrChildren = 0;
	mxml_node_t **attrChildren = sshsNodeXMLFilterChildNodes(content, "attr", &numAttrChildren);

	for (size_t i = 0; i < numAttrChildren; i++) {
		// Check that the proper attributes exist.
		const char *key = mxmlElementGetAttr(attrChildren[i], "key");
		const char *type = mxmlElementGetAttr(attrChildren[i], "type");

		if (key == NULL || type == NULL) {
			continue;
		}

		// Get the needed values.
		const char *value = mxmlGetOpaque(attrChildren[i]);

		if (!sshsNodeStringToNodeConverter(node, key, type, value)) {
			char errorMsg[1024];
			snprintf(errorMsg, 1024, "Failed to convert attribute '%s' of type '%s' with value '%s' from XML.", key,
				type, value);

			(*sshsGetGlobalErrorLogCallback())(errorMsg);
		}
	}

	free(attrChildren);

	if (recursive) {
		size_t numNodeChildren = 0;
		mxml_node_t **nodeChildren = sshsNodeXMLFilterChildNodes(content, "node", &numNodeChildren);

		for (size_t i = 0; i < numNodeChildren; i++) {
			// Check that the proper attributes exist.
			const char *childName = mxmlElementGetAttr(nodeChildren[i], "name");

			if (childName == NULL) {
				continue;
			}

			// Get the child node.
			sshsNode childNode = sshsNodeGetChild(node, childName);

			// If not existing, try to create.
			if (childNode == NULL) {
				childNode = sshsNodeAddChild(node, childName);
			}

			// And call recursively.
			sshsNodeConsumeXML(childNode, nodeChildren[i], recursive);
		}

		free(nodeChildren);
	}
}

bool sshsNodeStringToNodeConverter(sshsNode node, const char *key, const char *typeStr, const char *valueStr) {
	// Parse the values according to type and put them in the node.
	enum sshs_node_attr_value_type type;
	type = sshsHelperStringToTypeConverter(typeStr);

	union sshs_node_attr_value value;
	bool conversionSuccess = sshsHelperStringToValueConverter(type, valueStr, &value);

	if ((type == UNKNOWN) || !conversionSuccess) {
		return (false);
	}

	sshsNodePutAttribute(node, key, type, value);

	// Free string copy from helper.
	if (type == STRING) {
		free(value.string);
	}

	return (true);
}

const char **sshsNodeGetChildNames(sshsNode node, size_t *numNames) {
	size_t numChildren;
	sshsNode *children = sshsNodeGetChildren(node, &numChildren);

	if (children == NULL) {
		*numNames = 0;
		return (NULL);
	}

	const char **childNames = malloc(numChildren * sizeof(*childNames));
	SSHS_MALLOC_CHECK_EXIT(childNames);

	// Copy pointers to name string over. Safe because nodes are never deleted.
	for (size_t i = 0; i < numChildren; i++) {
		childNames[i] = sshsNodeGetName(children[i]);
	}

	free(children);

	*numNames = numChildren;
	return (childNames);
}

const char **sshsNodeGetAttributeKeys(sshsNode node, size_t *numKeys) {
	size_t numAttributes;
	sshsNodeAttr *attributes = sshsNodeGetAttributes(node, &numAttributes);

	if (attributes == NULL) {
		*numKeys = 0;
		return (NULL);
	}

	const char **attributeKeys = malloc(numAttributes * sizeof(*attributeKeys));
	SSHS_MALLOC_CHECK_EXIT(attributeKeys);

	// Copy pointers to key string over. Safe because attributes are never deleted.
	for (size_t i = 0; i < numAttributes; i++) {
		attributeKeys[i] = attributes[i]->key;
	}

	free(attributes);

	*numKeys = numAttributes;
	return (attributeKeys);
}

enum sshs_node_attr_value_type *sshsNodeGetAttributeTypes(sshsNode node, const char *key, size_t *numTypes) {
	size_t numAttributes;
	sshsNodeAttr *attributes = sshsNodeGetAttributes(node, &numAttributes);

	if (attributes == NULL) {
		*numTypes = 0;
		return (NULL);
	}

	// There are at most 8 types for one specific attribute key.
	enum sshs_node_attr_value_type *attributeTypes = malloc(8 * sizeof(*attributeTypes));
	SSHS_MALLOC_CHECK_EXIT(attributeTypes);

	// Check each attribute if it matches, and save its type if true.
	size_t typeCounter = 0;

	for (size_t i = 0; i < numAttributes; i++) {
		if (strcmp(key, attributes[i]->key) == 0) {
			attributeTypes[typeCounter++] = attributes[i]->value_type;
		}
	}

	free(attributes);

	// If we found nothing, return nothing.
	if (typeCounter == 0) {
		free(attributeTypes);
		attributeTypes = NULL;
	}

	*numTypes = typeCounter;
	return (attributeTypes);
}
