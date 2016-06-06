IF (NOT DOXYGEN_FOUND)
	# Only support call from main cmake.
	RETURN()
ENDIF()

# Doxygen directories and configuration. HTML and Latex are generated.
SET(DOXYGEN_OUTPUT_DIR ${CMAKE_BINARY_DIR}/docs/)
SET(DOXYGEN_CONFIG ${DOXYGEN_OUTPUT_DIR}/libcaer_api.doxy)
SET(DOXYGEN_LATEX_OUTPUT_DIR ${DOXYGEN_OUTPUT_DIR}/latex/)
SET(DOXYGEN_LATEX_OUTPUT ${DOXYGEN_LATEX_OUTPUT_DIR}/refman.tex)
SET(DOXYGEN_HTML_OUTPUT_DIR ${DOXYGEN_OUTPUT_DIR}/html/)
SET(DOXYGEN_HTML_OUTPUT ${DOXYGEN_HTML_OUTPUT_DIR}/index.html)

CONFIGURE_FILE(libcaer_api.doxy.in libcaer_api.doxy @ONLY)

ADD_CUSTOM_COMMAND(
	OUTPUT ${DOXYGEN_LATEX_OUTPUT} ${DOXYGEN_HTML_OUTPUT}
	COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_CONFIG}
	WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/include/
	DEPENDS ${DOXYGEN_CONFIG})

# Generate documentation with 'make doc'.
ADD_CUSTOM_TARGET(doc DEPENDS ${DOXYGEN_LATEX_OUTPUT} ${DOXYGEN_HTML_OUTPUT})

# Automatically generate PDF from Latex.
FIND_PACKAGE(LATEX)

IF (NOT LATEX_COMPILER)
    MESSAGE(STATUS "latex command LATEX_COMPILER not found, but usually required by Doxygen.")
ENDIF()

IF (NOT MAKEINDEX_COMPILER)
    MESSAGE(STATUS "makeindex command MAKEINDEX_COMPILER not found, but usually required by Doxygen.")
ENDIF()

IF (NOT DVIPS_CONVERTER)
    MESSAGE(STATUS "dvips command DVIPS_CONVERTER not found, but usually required by Doxygen.")
ENDIF()

# Generate PDF documentation.
ADD_CUSTOM_COMMAND(
    OUTPUT ${DOXYGEN_LATEX_OUTPUT_DIR}/refman.pdf
    COMMAND make
    WORKING_DIRECTORY ${DOXYGEN_LATEX_OUTPUT_DIR}
    DEPENDS ${DOXYGEN_LATEX_OUTPUT})

# Generate PDF from Latex with 'make pdf'.
ADD_CUSTOM_TARGET(pdf DEPENDS ${DOXYGEN_LATEX_OUTPUT_DIR}/refman.pdf)
