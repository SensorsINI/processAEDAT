#include "libcaer.h"
#include <stdatomic.h>
#include <stdarg.h>
#include <time.h>
#include <unistd.h>

static atomic_uint_fast8_t caerLogLevel = ATOMIC_VAR_INIT(CAER_LOG_ERROR);
static atomic_int caerLogFileDescriptor1 = ATOMIC_VAR_INIT(STDERR_FILENO);
static atomic_int caerLogFileDescriptor2 = ATOMIC_VAR_INIT(-1);

void caerLogLevelSet(uint8_t logLevel) {
	atomic_store_explicit(&caerLogLevel, logLevel, memory_order_relaxed);
}

uint8_t caerLogLevelGet(void) {
	return (atomic_load_explicit(&caerLogLevel, memory_order_relaxed));
}

void caerLogFileDescriptorsSet(int fd1, int fd2) {
	if (fd1 == fd2) {
		// If the same fd is passed twice, just disable it the second time.
		fd2 = -1;
	}

	atomic_store_explicit(&caerLogFileDescriptor1, fd1, memory_order_relaxed);
	atomic_store_explicit(&caerLogFileDescriptor2, fd2, memory_order_relaxed);
}

void caerLog(uint8_t logLevel, const char *subSystem, const char *format, ...) {
	// Check that subSystem and format are defined correctly.
	if (subSystem == NULL || format == NULL) {
		caerLog(CAER_LOG_ERROR, "Logger", "Missing subSystem or format strings. Neither can be NULL.");
		return;
	}

	// Only log messages if there is a destination (file-descriptor) to write them to.
	int logFileDescriptor1 = atomic_load_explicit(&caerLogFileDescriptor1, memory_order_relaxed);
	int logFileDescriptor2 = atomic_load_explicit(&caerLogFileDescriptor2, memory_order_relaxed);

	if (logFileDescriptor1 < 0 && logFileDescriptor2 < 0) {
		// Logging is disabled.
		return;
	}

	// Only log messages above the specified severity level.
	if (logLevel > atomic_load_explicit(&caerLogLevel, memory_order_relaxed)) {
		return;
	}

	// First prepend the time.
	time_t currentTimeEpoch = time(NULL);

	// From localtime_r() man-page: "According to POSIX.1-2004, localtime()
	// is required to behave as though tzset(3) was called, while
	// localtime_r() does not have this requirement."
	// So we make sure to call it here, to be portable.
	tzset();

	struct tm currentTime;
	localtime_r(&currentTimeEpoch, &currentTime);

	// Following time format uses exactly 29 characters (8 separators/punctuation,
	// 4 year, 2 month, 2 day, 2 hours, 2 minutes, 2 seconds, 2 'TZ', 5 timezone).
	size_t currentTimeStringLength = 29;
	char currentTimeString[currentTimeStringLength + 1]; // + 1 for terminating NUL byte.
	strftime(currentTimeString, currentTimeStringLength + 1, "%Y-%m-%d %H:%M:%S (TZ%z)", &currentTime);

	// Prepend debug level as a string to format.
	const char *logLevelString;
	switch (logLevel) {
		case CAER_LOG_EMERGENCY:
			logLevelString = "EMERGENCY";
			break;

		case CAER_LOG_ALERT:
			logLevelString = "ALERT";
			break;

		case CAER_LOG_CRITICAL:
			logLevelString = "CRITICAL";
			break;

		case CAER_LOG_ERROR:
			logLevelString = "ERROR";
			break;

		case CAER_LOG_WARNING:
			logLevelString = "WARNING";
			break;

		case CAER_LOG_NOTICE:
			logLevelString = "NOTICE";
			break;

		case CAER_LOG_INFO:
			logLevelString = "INFO";
			break;

		case CAER_LOG_DEBUG:
			logLevelString = "DEBUG";
			break;

		default:
			logLevelString = "UNKNOWN";
			break;
	}

	// Copy all strings into one and ensure NUL termination.
	size_t logLength = (size_t) snprintf(NULL, 0, "%s: %s: %s: %s\n", currentTimeString, logLevelString, subSystem,
		format);
	char logString[logLength + 1];
	snprintf(logString, logLength + 1, "%s: %s: %s: %s\n", currentTimeString, logLevelString, subSystem, format);

	va_list argptr;

	if (logFileDescriptor1 >= 0) {
		va_start(argptr, format);
		vdprintf(logFileDescriptor1, logString, argptr);
		va_end(argptr);
	}

	if (logFileDescriptor2 >= 0) {
		va_start(argptr, format);
		vdprintf(logFileDescriptor2, logString, argptr);
		va_end(argptr);
	}
}
