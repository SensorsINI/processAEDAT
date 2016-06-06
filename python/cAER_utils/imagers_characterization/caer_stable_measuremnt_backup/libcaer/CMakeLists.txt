# Init CMake (require at least version 2.6)
CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

# General build settings
IF (NOT CMAKE_BUILD_TYPE)
	SET(CMAKE_BUILD_TYPE "Release" CACHE STRING "Possible build types: None Debug Release RelWithDebInfo MinSizeRel")
ENDIF()

IF (NOT ENABLE_OPENCV)
	SET(ENABLE_OPENCV 0 CACHE BOOL "Enable support for frame enhancements using OpenCV")
ENDIF()

# Project name and version
PROJECT(libcaer C CXX)
SET(PROJECT_VERSION_MAJOR 2)
SET(PROJECT_VERSION_MINOR 0)
SET(PROJECT_VERSION_PATCH 0)
SET(PROJECT_VERSION_NOREV ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH})
IF (NOT PROJECT_REVISION)
	EXECUTE_PROCESS(COMMAND svnversion OUTPUT_VARIABLE PROJECT_REVISION OUTPUT_STRIP_TRAILING_WHITESPACE)
	# EXECUTE_PROCESS(COMMAND git rev-parse HEAD OUTPUT_VARIABLE PROJECT_REVISION OUTPUT_STRIP_TRAILING_WHITESPACE)
ENDIF()
SET(PROJECT_VERSION ${PROJECT_VERSION_NOREV}-r${PROJECT_REVISION})
MESSAGE(STATUS "Project version is: ${PROJECT_VERSION}")

# Define installation paths.
INCLUDE(GNUInstallDirs)

# Set compiler info
SET(CC_CLANG FALSE)
SET(CC_GCC FALSE)
SET(CC_ICC FALSE)
SET(CC_MSVC FALSE)

IF ("${CMAKE_C_COMPILER_ID}" STREQUAL "Clang")
	SET(CC_CLANG TRUE)
ELSEIF ("${CMAKE_C_COMPILER_ID}" STREQUAL "GNU")
	SET(CC_GCC TRUE)
ELSEIF ("${CMAKE_C_COMPILER_ID}" STREQUAL "Intel")
	SET(CC_ICC TRUE)
ELSEIF ("${CMAKE_C_COMPILER_ID}" STREQUAL "MSVC")
	SET(CC_MSVC TRUE)
ENDIF()

# Test if we are on a big-endian architecture
INCLUDE(TestBigEndian)
TEST_BIG_ENDIAN(SYSTEM_BIGENDIAN)

# Check size of various types
INCLUDE(CheckTypeSize)
CHECK_TYPE_SIZE("size_t" SIZEOF_SIZE_T)
CHECK_TYPE_SIZE("void *" SIZEOF_VOID_PTR)

IF (NOT "${SIZEOF_VOID_PTR}" STREQUAL "${SIZEOF_SIZE_T}")
	MESSAGE(SEND_ERROR "Size of void * and size_t must be the same!")
ENDIF()

# Check threads support (almost nobody implements C11 threads yet!)
FIND_PACKAGE(Threads)
SET(HAVE_PTHREADS ${CMAKE_USE_PTHREADS_INIT})
SET(HAVE_WIN32_THREADS ${CMAKE_USE_WIN32_THREADS_INIT})

IF (HAVE_PTHREADS)
	ADD_DEFINITIONS(-DHAVE_PTHREADS=1)

	# POSIX system (Unix, Linux, MacOS X)
	ADD_DEFINITIONS(-D_XOPEN_SOURCE=700)
	ADD_DEFINITIONS(-D_DEFAULT_SOURCE=1)

	IF (APPLE)
		ADD_DEFINITIONS(-D_DARWIN_C_SOURCE=1)
	ENDIF()
ENDIF()

IF (HAVE_WIN32_THREADS)
	ADD_DEFINITIONS(-DHAVE_WIN32_THREADS=1)
ENDIF()

# C11 standard needed (atomics, threads)
IF (CC_GCC OR CC_CLANG)
	SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c11")
	SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
ENDIF()

# Enable all warnings for GCC / Clang
IF (CC_GCC OR CC_CLANG)
	SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -pedantic -Wall -Wextra")
	SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pedantic -Wall -Wextra")

	IF (CC_GCC)
		# Enable all useful warnings manually in GCC.
		SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wunused -Wundef -Wformat=2 -Winit-self -Wuninitialized")
		SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wpointer-arith -Wcast-qual -Wcast-align -Wwrite-strings")
		SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wstrict-prototypes -Wmissing-prototypes -Wredundant-decls")
		SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wmissing-declarations -Wnested-externs -Wstack-protector")
		SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wshadow -Wbad-function-cast -Wfloat-equal")
		SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wconversion -Wstrict-overflow=2")
		SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wjump-misses-init -Wunsuffixed-float-constants -Wdouble-promotion")
	ENDIF()

	IF (CC_CLANG)
		# Enable all warnings in Clang easily.
		SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Weverything -Wno-packed -Wno-padded -Wno-unreachable-code-break")
		SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wno-disabled-macro-expansion")
	ENDIF()
ENDIF()

# Search for external libraries with pkg-config
INCLUDE(FindPkgConfig)

# Basic USB device support
PKG_CHECK_MODULES(LIBUSB1 REQUIRED libusb-1.0>=1.0.17)
SET(LIBCAER_INCDIRS ${LIBUSB1_INCLUDE_DIRS})
SET(LIBCAER_LIBDIRS ${LIBUSB1_LIBRARY_DIRS})
SET(LIBCAER_LIBS ${LIBUSB1_LIBRARIES})

IF (ENABLE_OPENCV)
	# Require new OpenCV 3.1 at least.
	PKG_CHECK_MODULES(OPENCV3 REQUIRED opencv>=3.1)

	SET(LIBCAER_INCDIRS ${LIBCAER_INCDIRS} ${OPENCV3_INCLUDE_DIRS})
	SET(LIBCAER_LIBDIRS ${LIBCAER_LIBDIRS} ${OPENCV3_LIBRARY_DIRS})
	SET(LIBCAER_LIBS ${LIBCAER_LIBS} ${OPENCV3_LIBRARIES})
ENDIF()

# Threads support
SET(LIBCAER_LIBS ${LIBCAER_LIBS} ${CMAKE_THREAD_LIBS_INIT})

# Add local directory to include paths
SET(LIBCAER_INCDIRS ${LIBCAER_INCDIRS} ${CMAKE_SOURCE_DIR}/include/)

INCLUDE_DIRECTORIES(${LIBCAER_INCDIRS})
LINK_DIRECTORIES(${LIBCAER_LIBDIRS})

# Set full RPATH
SET(CMAKE_INSTALL_RPATH ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR})
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
IF (APPLE)
	SET(CMAKE_MACOSX_RPATH TRUE)
ENDIF()

# Subdirectories
ADD_SUBDIRECTORY(include)
ADD_SUBDIRECTORY(src)

# Generate pkg-config file
FOREACH (LIB ${CMAKE_THREAD_LIBS_INIT})
	SET(PRIVATE_LIBS "${LIB} ${PRIVATE_LIBS}")
ENDFOREACH()

IF (ENABLE_OPENCV)
	# Use different pkg-config file to specify OpenCV support
	CONFIGURE_FILE(libcaer_opencv.pc.in libcaer.pc @ONLY)
ELSE()
	CONFIGURE_FILE(libcaer.pc.in libcaer.pc @ONLY)
ENDIF()

INSTALL(FILES ${CMAKE_BINARY_DIR}/libcaer.pc DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig)

# Automatic documentation generation support
FIND_PACKAGE(Doxygen)

IF (DOXYGEN_FOUND)
	ADD_SUBDIRECTORY(docs)
ENDIF()
