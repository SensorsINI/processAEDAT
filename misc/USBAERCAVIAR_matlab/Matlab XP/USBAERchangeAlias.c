#include "mex.h"
#include "USBAERCommon.h"
#define NUM_PARAM_ENTRADA 2
#define NUM_PARAM_SALIDA 1




void mexFunction( int nlhs, mxArray *plhs[],
                  int nrhs, const mxArray *prhs[])
{
  double param1,error=0;
  char buf[64], *DevName;
  int i;
  unsigned long nWrite,longitud;
  
  // comprobacion del numero de parametros de entrada y salida.
  
  if(nrhs != NUM_PARAM_ENTRADA) 
    mexErrMsgTxt("Error. Input parameters don't match: [error] = USBAERchangeAlias(hnd,DeviceName)");
  //if(nlhs != NUM_PARAM_SALIDA) 
  //  mexErrMsgTxt("Error. Output parameters don't match: [error] = USBAERchangeAlias(hnd,DeviceName)");
    
  /* comprueba que el primer argumento es el manejador (un escalar). */
  if(!mxIsDouble(prhs[0]) || mxIsComplex(prhs[0]) || mxGetN(prhs[0])*mxGetM(prhs[0]) != 1 ) {
    mexErrMsgTxt("Parameter 1 is not an escalar.");   
  }  
  
    /* Comprueba que el segundo argumento es una matriz de eventos de 1xN */
  if(mxGetM(prhs[1])!=1 ) {
    mexErrMsgTxt("Parameter 2 is not a 1xM text array.");   
  }  
  
  longitud = mxGetN(prhs[1]);
  param1 = mxGetScalar(prhs[0]); // el manejador
  DevName = mxGetPr(prhs[1]);     // la matriz de eventos

  hDevice=LeerManejadorMatlab(param1);

  if (hDevice!=INVALID_HANDLE_VALUE){
        if(longitud>28)
                {mexErrMsgTxt("Device name is too long");}
        else
        {
        buf[0]='A';
        buf[1]='T';
        buf[2]='C';
        buf[3]= 3;   // comando 3 escribir descriptor
        for(i=4;i<8;i++) {
                buf[i]=(longitud>>(8*(i-4)))&0xff;
                printf("%d\n",buf[i]);
        }        
        buf[8]=2*longitud+2;
        buf[9]= 3; //Desc String

        for (i=0;i<longitud;i++)
               {buf[10+2*i]=DevName[2*i];
                buf[11+2*i]=0;
                printf("%s",buf+10+2*i);
                }                
        i=10+2*i;
        while(i<64)buf[i++]=0;
        WriteFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);
        }
  } else {
      error=1;
  }
  
  plhs[0]=mxCreateScalarDouble((double) error);
}
