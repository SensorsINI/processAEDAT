#ifndef C11THREADS_POSIX_H_
#define C11THREADS_POSIX_H_

#include <stdint.h>
#include <pthread.h>
#include <time.h>
#include <sys/time.h>
#include <sched.h>
#include <errno.h>

typedef pthread_t thrd_t;
typedef pthread_once_t once_flag;
typedef pthread_mutex_t mtx_t;
typedef pthread_rwlock_t mtx_shared_t; // NON STANDARD!
typedef int (*thrd_start_t)(void *);

enum {
	thrd_success = 0, thrd_error = 1, thrd_nomem = 2, thrd_timedout = 3, thrd_busy = 4,
};

enum {
	mtx_plain = 0, mtx_timed = 1, mtx_recursive = 2,
};

#define ONCE_FLAG_INIT PTHREAD_ONCE_INIT

static inline int thrd_create(thrd_t *thr, thrd_start_t func, void *arg) {
	int ret = pthread_create(thr, NULL, (void *(*)(void *)) func, arg);

	switch (ret) {
		case 0:
			return (thrd_success);

		case EAGAIN:
			return (thrd_nomem);

		default:
			return (thrd_error);
	}
}

static inline _Noreturn void thrd_exit(int res) {
	pthread_exit((void*) (intptr_t) res);
}

static inline int thrd_detach(thrd_t thr) {
	if (pthread_detach(thr) != 0) {
		return (thrd_error);
	}

	return (thrd_success);
}

static inline int thrd_join(thrd_t thr, int *res) {
	void *pthread_res;

	if (pthread_join(thr, &pthread_res) != 0) {
		return (thrd_error);
	}

	if (res != NULL) {
		*res = (int) (intptr_t) pthread_res;
	}

	return (thrd_success);
}

static inline int thrd_sleep(const struct timespec *time_point, struct timespec *remaining) {
	if (nanosleep(time_point, remaining) == 0) {
		return (0); // Successful sleep.
	}

	if (errno == EINTR) {
		return (-1); // C11: a signal occurred.
	}

	return (-2); // C11: other negative value if an error occurred.
}

static inline void thrd_yield(void) {
	sched_yield();
}

static inline thrd_t thrd_current(void) {
	return (pthread_self());
}

static inline int thrd_equal(thrd_t lhs, thrd_t rhs) {
	return (pthread_equal(lhs, rhs));
}

static inline void call_once(once_flag *flag, void (*func)(void)) {
	pthread_once(flag, func);
}

static inline int mtx_init(mtx_t *mutex, int type) {
	pthread_mutexattr_t attr;
	if (pthread_mutexattr_init(&attr) != 0) {
		return (thrd_error);
	}

	// TIMED and PLAIN
	pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_NORMAL);

	if (type & 0x02) {
		// RECURSIVE
		pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE);
	}

	if (pthread_mutex_init(mutex, &attr) != 0) {
		pthread_mutexattr_destroy(&attr);
		return (thrd_error);
	}

	pthread_mutexattr_destroy(&attr);
	return (thrd_success);
}

static inline void mtx_destroy(mtx_t *mutex) {
	pthread_mutex_destroy(mutex);
}

static inline int mtx_lock(mtx_t *mutex) {
	if (pthread_mutex_lock(mutex) != 0) {
		return (thrd_error);
	}

	return (thrd_success);
}

static inline int mtx_trylock(mtx_t *mutex) {
	int ret = pthread_mutex_trylock(mutex);

	switch (ret) {
		case 0:
			return (thrd_success);

		case EBUSY:
			return (thrd_busy);

		default:
			return (thrd_error);
	}
}

static inline int mtx_timedlock(mtx_t *restrict mutex, const struct timespec *restrict time_point) {
#if defined(__APPLE__)
	// Emulate on MacOS X.
	struct timespec sleepTime = { .tv_sec = 0, .tv_nsec = 1000000 /* 1ms */ };
	struct timeval currentTime;
	int ret;

	while ((ret = mtx_trylock(mutex)) == thrd_busy) {
		gettimeofday(&currentTime, NULL);

		if (currentTime.tv_sec >= time_point->tv_sec && (currentTime.tv_usec * 1000) >= time_point->tv_nsec) {
			return (thrd_timedout);
		}

		nanosleep(&sleepTime, NULL);
	}

	return (ret);
#elif defined(__unix__) || defined(__UNIX__)
	int ret = pthread_mutex_timedlock(mutex, time_point);

	switch (ret) {
		case 0:
			return (thrd_success);

		case ETIMEDOUT:
			return (thrd_timedout);

		default:
			return (thrd_error);
	}
#endif
}

static inline int mtx_unlock(mtx_t *mutex) {
	if (pthread_mutex_unlock(mutex) != 0) {
		return (thrd_error);
	}

	return (thrd_success);
}

// NON STANDARD! 'int type' argument doesn't make sense here, always timed and recursive.
static inline int mtx_shared_init(mtx_shared_t *mutex) {
	if (pthread_rwlock_init(mutex, NULL) != 0) {
		return (thrd_error);
	}

	return (thrd_success);
}

// NON STANDARD!
static inline void mtx_shared_destroy(mtx_shared_t *mutex) {
	pthread_rwlock_destroy(mutex);
}

// NON STANDARD!
static inline int mtx_shared_lock_exclusive(mtx_shared_t *mutex) {
	if (pthread_rwlock_wrlock(mutex) != 0) {
		return (thrd_error);
	}

	return (thrd_success);
}

// NON STANDARD!
static inline int mtx_shared_trylock_exclusive(mtx_shared_t *mutex) {
	int ret = pthread_rwlock_trywrlock(mutex);

	switch (ret) {
		case 0:
			return (thrd_success);

		case EBUSY:
			return (thrd_busy);

		default:
			return (thrd_error);
	}
}

// NON STANDARD!
static inline int mtx_shared_timedlock_exclusive(mtx_shared_t *restrict mutex,
	const struct timespec *restrict time_point) {
#if defined(__APPLE__)
	// Emulate on MacOS X.
	struct timespec sleepTime = { .tv_sec = 0, .tv_nsec = 1000000 /* 1ms */ };
	struct timeval currentTime;
	int ret;

	while ((ret = mtx_shared_trylock_exclusive(mutex)) == thrd_busy) {
		gettimeofday(&currentTime, NULL);

		if (currentTime.tv_sec >= time_point->tv_sec && (currentTime.tv_usec * 1000) >= time_point->tv_nsec) {
			return (thrd_timedout);
		}

		nanosleep(&sleepTime, NULL);
	}

	return (ret);
#elif defined(__unix__) || defined(__UNIX__)
	int ret = pthread_rwlock_timedwrlock(mutex, time_point);

	switch (ret) {
		case 0:
			return (thrd_success);

		case ETIMEDOUT:
			return (thrd_timedout);

		default:
			return (thrd_error);
	}
#endif
}

// NON STANDARD!
static inline int mtx_shared_unlock_exclusive(mtx_shared_t *mutex) {
	if (pthread_rwlock_unlock(mutex) != 0) {
		return (thrd_error);
	}

	return (thrd_success);
}

// NON STANDARD!
static inline int mtx_shared_lock_shared(mtx_shared_t *mutex) {
	if (pthread_rwlock_rdlock(mutex) != 0) {
		return (thrd_error);
	}

	return (thrd_success);
}

// NON STANDARD!
static inline int mtx_shared_trylock_shared(mtx_shared_t *mutex) {
	int ret = pthread_rwlock_tryrdlock(mutex);

	switch (ret) {
		case 0:
			return (thrd_success);

		case EBUSY:
			return (thrd_busy);

		default:
			return (thrd_error);
	}
}

// NON STANDARD!
static inline int mtx_shared_timedlock_shared(mtx_shared_t *restrict mutex, const struct timespec *restrict time_point) {
#if defined(__APPLE__)
	// Emulate on MacOS X.
	struct timespec sleepTime = { .tv_sec = 0, .tv_nsec = 1000000 /* 1ms */ };
	struct timeval currentTime;
	int ret;

	while ((ret = mtx_shared_trylock_shared(mutex)) == thrd_busy) {
		gettimeofday(&currentTime, NULL);

		if (currentTime.tv_sec >= time_point->tv_sec && (currentTime.tv_usec * 1000) >= time_point->tv_nsec) {
			return (thrd_timedout);
		}

		nanosleep(&sleepTime, NULL);
	}

	return (ret);
#elif defined(__unix__) || defined(__UNIX__)
	int ret = pthread_rwlock_timedrdlock(mutex, time_point);

	switch (ret) {
		case 0:
			return (thrd_success);

		case ETIMEDOUT:
			return (thrd_timedout);

		default:
			return (thrd_error);
	}
#endif
}

// NON STANDARD!
static inline int mtx_shared_unlock_shared(mtx_shared_t *mutex) {
	if (pthread_rwlock_unlock(mutex) != 0) {
		return (thrd_error);
	}

	return (thrd_success);
}

#endif	/* C11THREADS_POSIX_H_ */
