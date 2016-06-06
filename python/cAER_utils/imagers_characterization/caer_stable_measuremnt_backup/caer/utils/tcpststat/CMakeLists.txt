# Compile TCP stream statistics program
ADD_EXECUTABLE(tcpststat tcpststat.c)
TARGET_LINK_LIBRARIES(tcpststat ${LIBCAER_LIBRARIES})
INSTALL(TARGETS tcpststat DESTINATION ${CMAKE_INSTALL_BINDIR})
