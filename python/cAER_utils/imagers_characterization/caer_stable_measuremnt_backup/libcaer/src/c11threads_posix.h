#ifndef C11THREADS_POSIX_H_
#define C11THREADS_POSIX_H_

#include <stdint.h>
#include <pthread.h>
#include <time.h>
#include <sched.h>
#include <errno.h>

typedef pthread_t thrd_t;

typedef int (*thrd_start_t)(void *);

enum {
	thrd_success = 0, thrd_busy = 1, thrd_error = 2, thrd_nomem = 3, thrd_timedout = 4,
};

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

static inline int thrd_sleep(const struct timespec *req, struct timespec *rem) {
	if (nanosleep(req, rem) == 0) {
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

static inline int thrd_equal(thrd_t thr1, thrd_t thr2) {
	return (pthread_equal(thr1, thr2));
}

#endif	/* C11THREADS_POSIX_H_ */
