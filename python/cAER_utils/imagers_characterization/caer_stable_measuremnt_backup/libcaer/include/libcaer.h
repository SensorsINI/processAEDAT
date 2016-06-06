/**
 * @file libcaer.h
 *
 * Main libcaer header; provides inclusions for common system functions
 * and definitions for useful macros used often in the code. Also includes
 * the logging functions and definitions and several useful static inline
 * functions for string comparison and byte array manipulation.
 * When including libcaer, please make sure to always use the full path,
 * ie. #include <libcaer/libcaer.h> and not just #include <libcaer.h>.
 */

#ifndef LIBCAER_H_
#define LIBCAER_H_

#ifdef __cplusplus
extern "C" {
#endif

// Common includes, useful for everyone.
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <errno.h>

// Use portable endian conversion functions.
#include "portable_endian.h"

// Include libcaer's log headers always.
#include "log.h"

/**
 * Cast argument to uint8_t (8bit unsigned integer).
 */
#define U8T(X)  ((uint8_t)  (X))
/**
 * Cast argument to uint16_t (16bit unsigned integer).
 */
#define U16T(X) ((uint16_t) (X))
/**
 * Cast argument to uint32_t (32bit unsigned integer).
 */
#define U32T(X) ((uint32_t) (X))
/**
 * Cast argument to uint64_t (64bit unsigned integer).
 */
#define U64T(X) ((uint64_t) (X))
/**
 * Cast argument to int8_t (8bit signed integer).
 */
#define I8T(X)  ((int8_t)  (X))
/**
 * Cast argument to int16_t (16bit signed integer).
 */
#define I16T(X) ((int16_t) (X))
/**
 * Cast argument to int32_t (32bit signed integer).
 */
#define I32T(X) ((int32_t) (X))
/**
 * Cast argument to int64_t (64bit signed integer).
 */
#define I64T(X) ((int64_t) (X))
/**
 * Mask and keep only the lower X bits of a 32bit (unsigned) integer.
 */
#define MASK_NUMBITS32(X) U32T(U32T(U32T(1) << X) - 1)
/**
 * Mask and keep only the lower X bits of a 64bit (unsigned) integer.
 */
#define MASK_NUMBITS64(X) U64T(U64T(U64T(1) << X) - 1)
/**
 * Swap the two values of the two variables X and Y, of a common type TYPE.
 */
#define SWAP_VAR(type, x, y) { type tmpv; tmpv = (x); (x) = (y); (y) = tmpv; }

/**
 * Clear bits given by mask (amount) and shift (position).
 */
//@{
#define CLEAR_NUMBITS32(VAR, SHIFT, MASK) (VAR) &= htole32(~(U32T(U32T(MASK) << (SHIFT))))
#define CLEAR_NUMBITS16(VAR, SHIFT, MASK) (VAR) &= htole16(~(U16T(U16T(MASK) << (SHIFT))))
#define CLEAR_NUMBITS8(VAR, SHIFT, MASK)  (VAR) &= U8T(~(U8T(U8T(MASK) << (SHIFT))))
//@}
/**
 * Set bits given by mask (amount) and shift (position) to a value.
 */
//@{
#define SET_NUMBITS32(VAR, SHIFT, MASK, VALUE) (VAR) |= htole32(U32T((U32T(VALUE) & (MASK)) << (SHIFT)))
#define SET_NUMBITS16(VAR, SHIFT, MASK, VALUE) (VAR) |= htole16(U16T((U16T(VALUE) & (MASK)) << (SHIFT)))
#define SET_NUMBITS8(VAR, SHIFT, MASK, VALUE)  (VAR) |= U8T((U8T(VALUE) & (MASK)) << (SHIFT))
//@}
/**
 * Get value of bits given by mask (amount) and shift (position).
 */
//@{
#define GET_NUMBITS32(VAR, SHIFT, MASK) ((le32toh(VAR) >> (SHIFT)) & (MASK))
#define GET_NUMBITS16(VAR, SHIFT, MASK) ((le16toh(VAR) >> (SHIFT)) & (MASK))
#define GET_NUMBITS8(VAR, SHIFT, MASK)  ((U8T(VAR) >> (SHIFT)) & (MASK))
//@}

/**
 * Compare two strings for equality.
 *
 * @param s1 the first string, cannot be NULL.
 * @param s2 the second string, cannot be NULL.
 *
 * @return true if equal, false otherwise.
 */
static inline bool caerStrEquals(const char *s1, const char *s2) {
	if (s1 == NULL || s2 == NULL) {
		return (false);
	}

	if (strcmp(s1, s2) == 0) {
		return (true);
	}

	return (false);
}

/**
 * Compare two strings for equality, up to a specified maximum length.
 *
 * @param s1 the first string, cannot be NULL.
 * @param s2 the second string, cannot be NULL.
 * @param len maximum comparison length, cannot be zero.
 *
 * @return true if equal, false otherwise.
 */
static inline bool caerStrEqualsUpTo(const char *s1, const char *s2, size_t len) {
	if (s1 == NULL || s2 == NULL || len == 0) {
		return (false);
	}

	if (strncmp(s1, s2, len) == 0) {
		return (true);
	}

	return (false);
}

/**
 * Convert a 32bit unsigned integer into an unsigned byte array of up to four bytes.
 * The integer will be stored in big-endian order, and the length will specify how
 * many bits to convert, starting from the lowest bit.
 *
 * @param integer the integer to convert.
 * @param byteArray pointer to the byte array in which to store the converted values.
 * @param byteArrayLength length of the byte array to convert to.
 */
static inline void caerIntegerToByteArray(uint32_t integer, uint8_t *byteArray, uint8_t byteArrayLength) {
	switch (byteArrayLength) {
		case 4:
			byteArray[0] = U8T(integer >> 24);
			byteArray[1] = U8T(integer >> 16);
			byteArray[2] = U8T(integer >> 8);
			byteArray[3] = U8T(integer);
			break;

		case 3:
			byteArray[0] = U8T(integer >> 16);
			byteArray[1] = U8T(integer >> 8);
			byteArray[2] = U8T(integer);
			break;

		case 2:
			byteArray[0] = U8T(integer >> 8);
			byteArray[1] = U8T(integer);
			break;

		case 1:
			byteArray[0] = U8T(integer);
			break;

		default:
			break;
	}
}

/**
 * Convert an unsigned byte array of up to four bytes into a 32bit unsigned integer.
 * The byte array length decides how many resulting bits in the integer are set,
 * and the single bytes are placed in the integer following big-endian ordering.
 *
 * @param byteArray pointer to the byte array with parts of the value stored.
 * @param byteArrayLength length of the array from which to convert.
 *
 * @return integer representing the value stored in the byte array.
 */
static inline uint32_t caerByteArrayToInteger(uint8_t *byteArray, uint8_t byteArrayLength) {
	uint32_t integer = 0;

	switch (byteArrayLength) {
		case 4:
			integer |= U32T(byteArray[0] << 24);
			integer |= U32T(byteArray[1] << 16);
			integer |= U32T(byteArray[2] << 8);
			integer |= U32T(byteArray[3]);
			break;

		case 3:
			integer |= U32T(byteArray[0] << 16);
			integer |= U32T(byteArray[1] << 8);
			integer |= U32T(byteArray[2]);
			break;

		case 2:
			integer |= U32T(byteArray[0] << 8);
			integer |= U32T(byteArray[1]);
			break;

		case 1:
			integer |= U32T(byteArray[0]);
			break;

		default:
			break;
	}

	return (integer);
}

#ifdef __cplusplus
}
#endif

#endif /* LIBCAER_H_ */
