#include "mex.h"
#include "USBAERCommon.h"
#define NUM_PARAM_ENTRADA 2
#define NUM_PARAM_SALIDA 2

void mexFunction( int nlhs, mxArray *plhs[],
                  int nrhs, const mxArray *prhs[])
{
  double param1, *a_bytes,*fpar;
  double error=0,num_b;
  int i,j,end,numbytes,nfpar;
  unsigned char buf[262144];
  unsigned long nWrite;
    char par[16]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};

  // comprobacion del numero de parametros de entrada y salida.
  
  if((nrhs != 2) && (nrhs != 3)) 
    mexErrMsgTxt("Error. Input parameters don't match: [error,Array] = USBAERReceive(hnd,NumBytesToRec)");
 // if(nlhs != NUM_PARAM_SALIDA) 
   // mexErrMsgTxt("Error. Output parameters don't match: [error,Array] = PCIAERReceive(hnd,NumBytesToRec)");
    
  /* comprueba que el primer argumento es el manejador (un escalar). */
  if(!mxIsDouble(prhs[0]) || mxIsComplex(prhs[0]) || mxGetN(prhs[0])*mxGetM(prhs[0]) != 1 ) {
    mexErrMsgTxt("Parameter 1 is not an escalar.");   
  }  

  /* comprueba que el segundo argumento es el numero de eventos (un escalar). */
  if(!mxIsDouble(prhs[1]) || mxIsComplex(prhs[1]) || mxGetN(prhs[1])*mxGetM(prhs[1]) != 1 ) {
    mexErrMsgTxt("Parameter 2 is not an escalar.");   
  }    
  
 /*Checks third parameter if it exists*/
  if (nrhs==3)
    {
    if(!mxIsDouble(prhs[2]) || mxIsComplex(prhs[2]) || mxGetN(prhs[2])!=1 ) 
                mexErrMsgTxt("Parameter 2 is not a Nx1 numeric matrix.");
    nfpar=mxGetM(prhs[2]);            
    if(nfpar>16)
                mexErrMsgTxt("Too many params passed to FPGA");
      fpar=mxGetPr(prhs[2]); //Parameter Vector
     for(i=0;i<nfpar;i++) par[i]=fpar[i]; //type conversion
     }
       param1 = mxGetScalar(prhs[0]); // el manejador
  num_b=mxGetScalar(prhs[1]);
  numbytes=(int) num_b;
  if (numbytes<=0) mexErrMsgTxt("Num of bytes must be greater than zero."); 
  if (numbytes%64!=0) mexErrMsgTxt("Num of bytes must be a multiple of 64.");
  if (numbytes>262144) mexErrMsgTxt("Num of bytes must be less than 262145");
  
  // recupero la direccion en la que esta la estructura del manejador del dispositivo en memoria.
  hDevice=LeerManejadorMatlab(param1);

  if (hDevice!=INVALID_HANDLE_VALUE){
      error=0.0;
      plhs[0]=mxCreateScalarDouble((double) error);  
      plhs[1] = mxCreateDoubleMatrix(num_b,1, mxREAL);
      a_bytes = mxGetPr(plhs[1]);
      
     
        // Enviamos comando
        buf[0]='A';
        buf[1]='T';
        buf[2]='C';
        buf[3]= 2;   // comando 2 es leer RAM
        for(i=4;i<8;i++)
                buf[i]=(numbytes>>(8*(i-4)))&0xff; //longitud.
        for(i=8;i<24;i++)
                                buf[i]=par[i-8];
        WriteFile(hDevice, buf,(unsigned long) 64, &nWrite, NULL);
      
            
             ReadFile(hDevice, buf, (unsigned long)numbytes, &nWrite, NULL);
        for(i=0;i<numbytes;i++)
            a_bytes[i]=buf[i];

  } else {
      error=1;
      plhs[0]=mxCreateScalarDouble((double) error);
      plhs[1] = mxCreateDoubleMatrix(num_b,1, mxREAL);
      a_bytes = mxGetPr(plhs[1]);
      for (i=0; i<numbytes; i++)
        a_bytes[i] = 0.0;      
  }
  

}
