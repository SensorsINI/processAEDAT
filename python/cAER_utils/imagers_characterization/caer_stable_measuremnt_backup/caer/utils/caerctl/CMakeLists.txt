# Compile cAERCtl
ADD_EXECUTABLE(caer-ctl ../../ext/sshs/sshs_helper.c ../ext/linenoise/linenoise.c caerctl.c)
INSTALL(TARGETS caer-ctl DESTINATION ${CMAKE_INSTALL_BINDIR})
