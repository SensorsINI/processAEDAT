#ifndef PORTABLE_TIME_H_
#define PORTABLE_TIME_H_

#if defined(__APPLE__)
	#include <time.h>
	#include <sys/time.h>
	#include <mach/mach.h>
	#include <mach/mach_time.h>
	#include <mach/clock.h>
	#include <mach/clock_types.h>
	#include <mach/mach_host.h>
	#include <mach/mach_port.h>

	static inline bool portable_clock_gettime_monotonic(struct timespec *monoTime) {
		kern_return_t kRet;
		clock_serv_t clockRef;
		mach_timespec_t machTime;

		mach_port_t host = mach_host_self();

		kRet = host_get_clock_service(host, SYSTEM_CLOCK, &clockRef);
		mach_port_deallocate(mach_task_self(), host);

		if (kRet != KERN_SUCCESS) {
			errno = EINVAL;
			return (false);
		}

		kRet = clock_get_time(clockRef, &machTime);
		mach_port_deallocate(mach_task_self(), clockRef);

		if (kRet != KERN_SUCCESS) {
			errno = EINVAL;
			return (false);
		}

		monoTime->tv_sec  = machTime.tv_sec;
		monoTime->tv_nsec = machTime.tv_nsec;

		return (true);
	}

	static inline bool portable_clock_gettime_realtime(struct timespec *realTime) {
		kern_return_t kRet;
		clock_serv_t clockRef;
		mach_timespec_t machTime;

		mach_port_t host = mach_host_self();

		kRet = host_get_clock_service(host, CALENDAR_CLOCK, &clockRef);
		mach_port_deallocate(mach_task_self(), host);

		if (kRet != KERN_SUCCESS) {
			errno = EINVAL;
			return (false);
		}

		kRet = clock_get_time(clockRef, &machTime);
		mach_port_deallocate(mach_task_self(), clockRef);

		if (kRet != KERN_SUCCESS) {
			errno = EINVAL;
			return (false);
		}

		realTime->tv_sec  = machTime.tv_sec;
		realTime->tv_nsec = machTime.tv_nsec;

		return (true);
	}
#elif (_POSIX_C_SOURCE >= 200112L || _XOPEN_SOURCE >= 600)
	#include <time.h>

	static inline bool portable_clock_gettime_monotonic(struct timespec *monoTime) {
		return (clock_gettime(CLOCK_MONOTONIC, monoTime) == 0);
	}

	static inline bool portable_clock_gettime_realtime(struct timespec *realTime) {
		return (clock_gettime(CLOCK_REALTIME, realTime) == 0);
	}
#else
	#error "No portable way of getting absolute monotonic time."
#endif

#endif /* PORTABLE_TIME_H_ */
