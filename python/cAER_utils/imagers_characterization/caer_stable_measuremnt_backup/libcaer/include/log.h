/**
 * @file log.h
 *
 * Logging functions to print useful messages for the user.
 */

#ifndef LIBCAER_LOG_H_
#define LIBCAER_LOG_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

//@{
/**
 * Log levels for caerLog() logging function.
 * Log messages only get printed if their log level is equal or
 * above the global system log level, which can be set with
 * caerLogLevelSet().
 * The default log level is CAER_LOG_ERROR.
 * CAER_LOG_EMERGENCY is the most urgent log level and will always
 * be printed, while CAER_LOG_DEBUG is the least urgent log
 * level and will only be delivered if configured by the user.
 */
#define CAER_LOG_EMERGENCY (0)
#define CAER_LOG_ALERT     (1)
#define CAER_LOG_CRITICAL  (2)
#define CAER_LOG_ERROR     (3)
#define CAER_LOG_WARNING   (4)
#define CAER_LOG_NOTICE    (5)
#define CAER_LOG_INFO      (6)
#define CAER_LOG_DEBUG     (7)
//@}

/**
 * Set the system-wide log level.
 * Log messages will only be printed if their level is equal or above
 * this level.
 *
 * @param logLevel the system-wide log level.
 */
void caerLogLevelSet(uint8_t logLevel);

/**
 * Get the current system-wide log level.
 * Log messages are only printed if their level is equal or above
 * this level.
 *
 * @return the current system-wide log level.
 */
uint8_t caerLogLevelGet(void);

/**
 * Set to which file descriptors log messages are sent.
 * Up to two different file descriptors can be configured here.
 * By default logging to STDERR only is enabled.
 * If both file descriptors are identical, logging to it will
 * only happen once, as if the second one was disabled.
 *
 * @param fd1 first file descriptor to log to. A negative value will disable it.
 * @param fd2 second file descriptor to log to. A negative value will disable it.
 */
void caerLogFileDescriptorsSet(int fd1, int fd2);

/**
 * Main logging function.
 * This function takes messages, formats them and sends them out to a file descriptor,
 * respecting the system-wide log level setting and prepending the current time, the
 * log level and a user-specified common string to the actual formatted output.
 * The format is specified exactly as with the printf() family of functions.
 * Please see their manual-page for more information.
 *
 * @param logLevel the message-specific log level.
 * @param subSystem a common, user-specified string to prepend before the message.
 * @param format the message format string (see printf()).
 * @param ... the parameters to be formatted according to the format string (see printf()).
 */
void caerLog(uint8_t logLevel, const char *subSystem, const char *format, ...) __attribute__ ((format (printf, 3, 4)));

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_LOG_H_ */
