/*
 * log.h
 *
 *  Created on: Dec 30, 2013
 *      Author: llongi
 */

#ifndef LOG_H_
#define LOG_H_

#include "main.h"

extern int CAER_LOG_FILE_FD;

void caerLogInit(void);
void caerLogDisableConsole(void);

#endif /* LOG_H_ */
