#include "mex.h"
#include "USBAERCommon.h"
#include <string.h>
//#include "devintf.h"	// DriverWorks
#define NUM_PARAM_ENTRADA 1
#define NUM_PARAM_SALIDA 2

//----------------------------------------------------------------------------------

HANDLE OpenByInterface(
		PDWORD pError,		// address of variable to receive error status
		char *DevName
		)
{
	HANDLE hDev;
	
	hDev = CreateFile(
        DevName, 
		GENERIC_READ | GENERIC_WRITE,
		FILE_SHARE_READ | FILE_SHARE_WRITE,
		NULL,
		OPEN_EXISTING,
		FILE_ATTRIBUTE_NORMAL,
		NULL
		);

	if (hDev == INVALID_HANDLE_VALUE)
		*pError = GetLastError();


    return hDev;
}
//----------------------------------------------------------------------------------


void mexFunction( int nlhs, mxArray *plhs[],
                  int nrhs, const mxArray *prhs[])
{

  DWORD Error=0;
  DWORD direccion_handle;
  double man_matlab;
  char DevName[30],*kk;
  int len,i,j;
  // comprobacion del numero de parametros de entrada y salida.
    
  
  if(nrhs != NUM_PARAM_ENTRADA) 
    mexErrMsgTxt("Error. Input parameters don't match: [hnd, error] = USBAEROpen(DevName)");
  //if(nlhs != NUM_PARAM_SALIDA) 
  //  mexErrMsgTxt("Error. Output parameters don't match: [hnd, error] = USBAEROpen(DevName)");
  len = mxGetN(prhs[0]);
  if (len > 24) mexErrMsgTxt("Error. Device Name too long. Use a string with 24 characteres as maximum.");

  kk=mxGetPr(prhs[0]);
  strcpy(DevName,"\\\\.\\");
  for(i=0,j=4;i<2*len;i+=2,j++){  DevName[j]=kk[i];} // printf("%d, %s\n",len,DevName);}
  DevName[j]=0;
//  printf(DevName+7);
  hDevice = OpenByInterface(&Error,DevName);
  man_matlab=CrearManejadorMatlab(hDevice);
  plhs[0]=mxCreateScalarDouble((double) man_matlab);
  plhs[1]=mxCreateScalarDouble((double) Error);
}
