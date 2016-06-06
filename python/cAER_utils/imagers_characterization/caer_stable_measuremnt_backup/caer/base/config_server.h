#ifndef CONFIG_SERVER_H_
#define CONFIG_SERVER_H_

#include "main.h"

enum config_actions {
	NODE_EXISTS = 0, ATTR_EXISTS = 1, GET = 2, PUT = 3, ERROR = 4, GET_CHILDREN = 5, GET_ATTRIBUTES = 6, GET_TYPES = 7,
};

void caerConfigServerStart(void);
void caerConfigServerStop(void);

#endif /* CONFIG_SERVER_H_ */
