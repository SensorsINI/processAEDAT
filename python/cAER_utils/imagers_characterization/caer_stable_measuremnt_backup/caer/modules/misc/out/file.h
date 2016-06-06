#ifndef FILE_H_
#define FILE_H_

#include "out_common.h"

#define DEFAULT_PREFIX "caer_out"

void caerOutputFile(uint16_t moduleID, size_t outputTypesNumber, ...);

#endif /* FILE_H_ */
