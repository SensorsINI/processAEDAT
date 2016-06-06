/*
 * ringbuffer.c
 *
 *  Created on: Dec 10, 2013
 *      Author: llongi
 */

#include "ringbuffer.h"
#include "portable_aligned_alloc.h"
#include <stdatomic.h>
#include <stdalign.h> // To get alignas() macro.

// Alignment specification support (with defines for cache line alignment).
#undef CACHELINE_ALIGNED
#undef CACHELINE_ALONE

#if !defined(CACHELINE_SIZE)
	#define CACHELINE_SIZE 64 // Default (big enough for almost all processors).
	// Must be power of two!
#endif

#define CACHELINE_ALIGNED alignas(CACHELINE_SIZE)
#define CACHELINE_ALONE(t, v) CACHELINE_ALIGNED t v; uint8_t PAD_##v[CACHELINE_SIZE - (sizeof(t) & (CACHELINE_SIZE - 1))]

struct ring_buffer {
	CACHELINE_ALONE(size_t, putPos);
	CACHELINE_ALONE(size_t, getPos);
	CACHELINE_ALONE(size_t, size);
	atomic_uintptr_t elements[];
};

RingBuffer ringBufferInit(size_t size) {
	// Force multiple of two size for performance.
	if (size == 0 || (size & (size - 1)) != 0) {
		return (NULL);
	}

	RingBuffer rBuf = portable_aligned_alloc(CACHELINE_SIZE,
		sizeof(struct ring_buffer) + (size * sizeof(atomic_uintptr_t)));
	if (rBuf == NULL) {
		return (NULL);
	}

	// Initialize counter variables.
	rBuf->putPos = 0;
	rBuf->getPos = 0;
	rBuf->size = size;

	// Initialize pointers.
	for (size_t i = 0; i < size; i++) {
		atomic_store_explicit(&rBuf->elements[i], (uintptr_t) NULL, memory_order_relaxed);
	}

	atomic_thread_fence(memory_order_release);

	return (rBuf);
}

void ringBufferFree(RingBuffer rBuf) {
	free(rBuf);
}

bool ringBufferPut(RingBuffer rBuf, void *elem) {
	if (elem == NULL) {
		// NULL elements are disallowed (used as place-holders).
		// Critical error, should never happen -> exit!
		exit(EXIT_FAILURE);
	}

	void *curr = (void *) atomic_load_explicit(&rBuf->elements[rBuf->putPos], memory_order_acquire);

	// If the place where we want to put the new element is NULL, it's still
	// free and we can use it.
	if (curr == NULL) {
		atomic_store_explicit(&rBuf->elements[rBuf->putPos], (uintptr_t ) elem, memory_order_release);

		// Increase local put pointer.
		rBuf->putPos = ((rBuf->putPos + 1) & (rBuf->size - 1));

		return (true);
	}

	// Else, buffer is full.
	return (false);
}

void *ringBufferGet(RingBuffer rBuf) {
	void *curr = (void *) atomic_load_explicit(&rBuf->elements[rBuf->getPos], memory_order_acquire);

	// If the place where we want to get an element from is not NULL, there
	// is valid content there, which we return, and reset the place to NULL.
	if (curr != NULL) {
		atomic_store_explicit(&rBuf->elements[rBuf->getPos], (uintptr_t) NULL, memory_order_release);

		// Increase local get pointer.
		rBuf->getPos = ((rBuf->getPos + 1) & (rBuf->size - 1));

		return (curr);
	}

	// Else, buffer is empty.
	return (NULL);
}

void *ringBufferLook(RingBuffer rBuf) {
	void *curr = (void *) atomic_load_explicit(&rBuf->elements[rBuf->getPos], memory_order_acquire);

	// If the place where we want to get an element from is not NULL, there
	// is valid content there, which we return, without removing it from the
	// ring buffer.
	if (curr != NULL) {
		return (curr);
	}

	// Else, buffer is empty.
	return (NULL);
}
