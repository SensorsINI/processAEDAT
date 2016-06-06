/*
 * in_net_tcp_server.h
 *
 *  Created on: Nov 6, 2015
 *      Author: brandli, insightness
 */

#ifndef IN_NET_TCP_SERVER_H_
#define IN_NET_TCP_SERVER_H_

#include "in_common.h"
#include <libcaer/events/packetContainer.h>

caerEventPacketContainer caerInputNetTCPServer(uint16_t moduleID);

#endif /* IN_NET_TCP_SERVER_H_ */
