#ifndef PORTABLE_ALIGNED_ALLOC_H_
#define PORTABLE_ALIGNED_ALLOC_H_

#if (!defined(__APPLE__) && (__STDC_VERSION__ >= 201112L || defined(_ISOC11_SOURCE)))
	#include <stdlib.h>

	static inline void *portable_aligned_alloc(size_t alignment, size_t size) {
		return (aligned_alloc(alignment, size));
	}
#elif (_POSIX_C_SOURCE >= 200112L || _XOPEN_SOURCE >= 600)
	#include <stdlib.h>

	static inline void *portable_aligned_alloc(size_t alignment, size_t size) {
		void* mem;

		if (posix_memalign(&mem, alignment, size) == 0) {
			// Success!
			return (mem);
		}

		// Failure.
		return (NULL);
	}
#elif defined(_WIN32) || defined(__CYGWIN__)
	#include <malloc.h>

	static inline void *portable_aligned_alloc(size_t alignment, size_t size) {
		return (_aligned_malloc(size, alignment));
	}
#else
	#error "No portable way of getting aligned memory found."
#endif

#endif	/* PORTABLE_ALIGNED_ALLOC_H_ */
