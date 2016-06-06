# Add all modules
ADD_SUBDIRECTORY(backgroundactivityfilter)
ADD_SUBDIRECTORY(caffeinterface)
ADD_SUBDIRECTORY(cameracalibration)
ADD_SUBDIRECTORY(frameenhancer)
ADD_SUBDIRECTORY(imagegenerator)
ADD_SUBDIRECTORY(imagestreamervisualizer)
ADD_SUBDIRECTORY(ini)
ADD_SUBDIRECTORY(misc)
ADD_SUBDIRECTORY(statistics)
ADD_SUBDIRECTORY(visualizer)

# Support private modules that don't get considered for commit,
# by reserving a directory called PrivateModules with its own
# CMake PrivateModules.txt, and ignoring it.
INCLUDE(PrivateModules/PrivateModules.txt OPTIONAL)

# Propagate to parent scope.
SET(CAER_INCDIRS ${CAER_INCDIRS} PARENT_SCOPE)
SET(CAER_LIBDIRS ${CAER_LIBDIRS} PARENT_SCOPE)
SET(CAER_C_LIBS ${CAER_C_LIBS} PARENT_SCOPE)
SET(CAER_C_SRC_FILES ${CAER_C_SRC_FILES} PARENT_SCOPE)
SET(CAER_CXX_LIBS ${CAER_CXX_LIBS} PARENT_SCOPE)
SET(CAER_CXX_SRC_FILES ${CAER_CXX_SRC_FILES} PARENT_SCOPE)
SET(CAER_COMPILE_DEFINITIONS ${CAER_COMPILE_DEFINITIONS} PARENT_SCOPE)
