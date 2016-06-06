#ifndef SSHS_INTERNAL_H_
#define SSHS_INTERNAL_H_

// Implementation relevant common includes.
#include "sshs.h"
#include <string.h>
#include <stdarg.h>
#include <mxml.h>

#ifdef HAVE_PTHREADS
	#include "ext/c11threads_posix.h"
#endif

// Terminate process on failed memory allocation.
#define SSHS_MALLOC_CHECK_EXIT(ptr) \
	if ((ptr) == NULL) { \
		(*sshsGetGlobalErrorLogCallback())("Unable to allocate memory."); \
		exit(EXIT_FAILURE); \
	}

// SSHS node
typedef struct sshs_node_attr *sshsNodeAttr;
typedef struct sshs_node_listener *sshsNodeListener;
typedef struct sshs_node_attr_listener *sshsNodeAttrListener;

sshsNode sshsNodeNew(const char *nodeName, sshsNode parent);
sshsNode sshsNodeAddChild(sshsNode node, const char *childName);
sshsNode sshsNodeGetChild(sshsNode node, const char* childName);
void sshsNodeTransactionLock(sshsNode node);
void sshsNodeTransactionUnlock(sshsNode node);

// SSHS
sshsErrorLogCallback sshsGetGlobalErrorLogCallback(void);

#endif /* SSHS_INTERNAL_H_ */
