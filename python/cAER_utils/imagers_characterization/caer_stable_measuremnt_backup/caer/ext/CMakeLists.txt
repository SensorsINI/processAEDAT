SET(CAER_EXT_FILES
	ext/ringbuffer/ringbuffer.c
	ext/slre/slre.c
	ext/sshs/sshs.c
	ext/sshs/sshs_helper.c
	ext/sshs/sshs_node.c)

SET(CAER_C_SRC_FILES ${CAER_C_SRC_FILES} ${CAER_EXT_FILES} PARENT_SCOPE)
