# Compile UDP stream statistics program
ADD_EXECUTABLE(udpststat udpststat.c)
TARGET_LINK_LIBRARIES(udpststat ${LIBCAER_LIBRARIES})
INSTALL(TARGETS udpststat DESTINATION ${CMAKE_INSTALL_BINDIR})
