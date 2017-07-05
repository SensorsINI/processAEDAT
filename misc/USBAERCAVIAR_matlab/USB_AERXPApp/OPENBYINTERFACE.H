
#define NOCRYPT			// prevent attempt to include missing files
#define _INC_EXCPT		// prevent excpt.h from being included

#include <stdlib.h>
#include <windows.h>
#include <winioctl.h>
//#include <devintf.h>	// DriverWorks
#include <stdio.h>

#define Mapper1Device_CLASS_GUID \
 { 0x97bffdb5, 0x7701, 0x47a7, { 0xb0, 0x5d, 0x64, 0xcc, 0x5d, 0xf, 0xd9, 0x35 } }


 // Handle to device opened in driver.
//
HANDLE	hDevice = INVALID_HANDLE_VALUE;
// Class GUID used to open device
//
GUID ClassGuid = Mapper1Device_CLASS_GUID;

