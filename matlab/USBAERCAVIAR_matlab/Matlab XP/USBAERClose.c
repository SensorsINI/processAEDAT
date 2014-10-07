#include "mex.h"
#include "USBAERCommon.h"
#define NUM_PARAM_ENTRADA 1
#define NUM_PARAM_SALIDA 1




void mexFunction( int nlhs, mxArray *plhs[],
                  int nrhs, const mxArray *prhs[])
{
  double param1,error=0;
  
  // comprobacion del numero de parametros de entrada y salida.
  
  if(nrhs != NUM_PARAM_ENTRADA) 
    mexErrMsgTxt("Error. Input parameters don't match: [error] = USBAERClose(hnd)");
  //if(nlhs != NUM_PARAM_SALIDA) 
  //  mexErrMsgTxt("Error. Output parameters don't match: [error] = USBAERClose(hnd)");
    
  /* comprueba que el primer argumento es el manejador (un escalar). */
  if(!mxIsDouble(prhs[0]) || mxIsComplex(prhs[0]) || mxGetN(prhs[0])*mxGetM(prhs[0]) != 1 ) {
    mexErrMsgTxt("Parameter 1 is not an escalar.");   
  }  
    

  param1 = mxGetScalar(prhs[0]); // el manejador
  
  // recupero la direccion en la que esta la estructura del manejador del dispositivo en memoria.
  hDevice=LeerManejadorMatlab(param1);

  if (hDevice!=INVALID_HANDLE_VALUE){
     CloseHandle(hDevice);
  } else {
      error=1;
  }
  
  plhs[0]=mxCreateScalarDouble((double) error);
}
