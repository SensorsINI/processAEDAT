/*
 * ringbuffer.h
 *
 *  Created on: Dec 10, 2013
 *      Author: llongi
 */

#ifndef RINGBUFFER_H_
#define RINGBUFFER_H_

// Common includes, useful for everyone.
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct ring_buffer *RingBuffer;

RingBuffer ringBufferInit(size_t size);
void ringBufferFree(RingBuffer rBuf);
bool ringBufferPut(RingBuffer rBuf, void *elem);
void *ringBufferGet(RingBuffer rBuf);
void *ringBufferLook(RingBuffer rBuf);

#endif /* RINGBUFFER_H_ */
