
#define NOCRYPT			// prevent attempt to include missing files
#define _INC_EXCPT		// prevent excpt.h from being included

#include <stdlib.h>
#include <windows.h>
#include <winioctl.h>

#include <stdio.h>

#define DriverUSBDevice_CLASS_GUID  { 0x97bffdb5, 0x7701, 0x47a7, { 0xb0, 0x5d, 0x64, 0xcc, 0x5d, 0xf, 0xd9, 0x35 } }

// Handle to device opened in driver.
//
HANDLE	hDevice = INVALID_HANDLE_VALUE;
// Class GUID used to open device
//
GUID ClassGuid = DriverUSBDevice_CLASS_GUID;


#define NOMBRE_DISPOSITIVO  "\\\\.\\Mapbul2Device0"

double CrearManejadorMatlab(HANDLE manejador){
    DWORD *direccion_manejador;
    double resultado;
    
    direccion_manejador=(DWORD *) &manejador;
    resultado=(double) *direccion_manejador;
    
    return resultado;
}

HANDLE LeerManejadorMatlab(double man_matlab){
    DWORD direccion_manejador;
    HANDLE resultado;
    
    void **puntero_a_direccion;
    direccion_manejador=(DWORD) man_matlab;
    puntero_a_direccion=&direccion_manejador;
    
    resultado=*puntero_a_direccion;
    return resultado;
}


