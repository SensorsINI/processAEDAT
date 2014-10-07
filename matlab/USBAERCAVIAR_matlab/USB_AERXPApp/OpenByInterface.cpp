// OpenByIntf.cpp - open device by device interface
// Copyright (c) 1998 Compuware Corporation

// OpenByInterface
//
// Opens the nth device found with the given interface class

#include "OpenByInterface.h"
#include <vcl.h>

HANDLE OpenByInterface(	char* DevName0  )
{
	HANDLE hDev;
        //[28]={"\\\\.\\MAPPERU"};
       /*	CDeviceInterfaceClass DevClass(pClassGuid, pError);

	if (*pError != ERROR_SUCCESS)
		return INVALID_HANDLE_VALUE;

	CDeviceInterface DevInterface(&DevClass, instance, pError);

	if (*pError != ERROR_SUCCESS)
	 	return INVALID_HANDLE_VALUE;
                // "\\\\.\\Mapbul2Device0"
         */
	hDev = CreateFile( DevName0,
		GENERIC_READ | GENERIC_WRITE,
		FILE_SHARE_READ | FILE_SHARE_WRITE,
		NULL,
		OPEN_EXISTING,
		FILE_ATTRIBUTE_NORMAL,
		NULL
		);

	//if (hDev == INVALID_HANDLE_VALUE)
	//	*pError = GetLastError();

	return hDev;
}


 