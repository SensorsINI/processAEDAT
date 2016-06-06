# Init CMake (require at least version 2.6)
CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

# General build settings
IF (NOT CMAKE_BUILD_TYPE)
	SET(CMAKE_BUILD_TYPE "Release" CACHE STRING "Possible build types: None Debug Release RelWithDebInfo MinSizeRel")
ENDIF()

IF (NOT USE_TCMALLOC)
	SET(USE_TCMALLOC 0 CACHE BOOL "Link to and use TCMalloc (Google Perftools) to provide faster memory allocation")
ENDIF()

# Project name and version
PROJECT(cAER C CXX)
SET(PROJECT_VERSION_MAJOR 0)
SET(PROJECT_VERSION_MINOR 9)
SET(PROJECT_VERSION_PATCH 12)
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

	# Support for large files (>2GB) on 32-bit systems
	ADD_DEFINITIONS(-D_FILE_OFFSET_BITS=64)
ENDIF()

IF (HAVE_WIN32_THREADS)
	ADD_DEFINITIONS(-DHAVE_WIN32_THREADS=1)
ENDIF()

# Add definitions to recover CMake binary dir and system dirs.
SET(CM_BUILD_DIR ${CMAKE_BINARY_DIR})
SET(CM_SHARE_DIR ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_DATAROOTDIR}/caer)
ADD_DEFINITIONS(-DCM_BUILD_DIR=${CM_BUILD_DIR} -DCM_SHARE_DIR=${CM_SHARE_DIR})

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

# Basic device support and XML configuration
PKG_CHECK_MODULES(LIBCAER REQUIRED libcaer>=2.0.0)
PKG_CHECK_MODULES(MXML REQUIRED mxml>=2.7)

SET(CAER_INCDIRS ${LIBCAER_INCLUDE_DIRS} ${MXML_INCLUDE_DIRS})
SET(CAER_LIBDIRS ${LIBCAER_LIBRARY_DIRS} ${MXML_LIBRARY_DIRS})

SET(CAER_C_LIBS ${LIBCAER_LIBRARIES} ${MXML_LIBRARIES})
SET(CAER_C_SRC_FILES "")

# By default, no C++ support is enabled.
SET(CAER_CXX_LIBS "")
SET(CAER_CXX_SRC_FILES "")

SET(CAER_COMPILE_DEFINITIONS "")

# Add all files and libraries needed, all modules etc.
ADD_SUBDIRECTORY(base)
ADD_SUBDIRECTORY(ext)
ADD_SUBDIRECTORY(modules)

# Add local directory to include and library paths
SET(CAER_INCDIRS ${CAER_INCDIRS} ${CMAKE_SOURCE_DIR}/)
SET(CAER_LIBDIRS ${CAER_LIBDIRS} ${CMAKE_SOURCE_DIR}/)

INCLUDE_DIRECTORIES(${CAER_INCDIRS})
LINK_DIRECTORIES(${CAER_LIBDIRS})
ADD_DEFINITIONS(${CAER_COMPILE_DEFINITIONS})

# Set full RPATH
SET(CMAKE_INSTALL_RPATH ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR})
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
IF (APPLE)
	SET(CMAKE_MACOSX_RPATH TRUE)
ENDIF()

IF (UNIX AND NOT APPLE)
	# Add --as-needed to linker flags for executables.
	SET(CMAKE_EXE_LINKER_FLAGS "-Wl,--as-needed")
ENDIF()

# Add math support
SET(CAER_C_LIBS ${CAER_C_LIBS} m)

# Add realtime support, not needed on MacOS X though
IF (NOT APPLE)
	SET(CAER_C_LIBS ${CAER_C_LIBS} rt)
ENDIF()

# TCMalloc support (fast memory allocation)
IF (USE_TCMALLOC)
	PKG_CHECK_MODULES(LIBTCMALLOC REQUIRED libtcmalloc>=2.2)

	SET(CAER_INCDIRS ${CAER_INCDIRS} ${LIBTCMALLOC_INCLUDE_DIRS})
	SET(CAER_LIBDIRS ${CAER_LIBDIRS} ${LIBTCMALLOC_LIBRARY_DIRS})

	SET(CAER_C_LIBS ${CAER_C_LIBS} ${LIBTCMALLOC_LIBRARIES})
ENDIF()

ADD_EXECUTABLE(caer-bin ${CAER_C_SRC_FILES} ${CAER_CXX_SRC_FILES} main.c)
TARGET_LINK_LIBRARIES(caer-bin ${CMAKE_THREAD_LIBS_INIT} ${CAER_C_LIBS} ${CAER_CXX_LIBS})
INSTALL(TARGETS caer-bin DESTINATION ${CMAKE_INSTALL_BINDIR})

# Compile extra utitilies
ADD_SUBDIRECTORY(utils)
