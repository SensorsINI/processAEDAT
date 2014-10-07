#include "mex.h"
#include "USBAERCommon.h"
#define NUM_PARAM_ENTRADA 3
#define NUM_PARAM_SALIDA 1


void mexFunction( int nlhs, mxArray *plhs[],
                  int nrhs, const mxArray *prhs[])
{
  double *a_ipod,*fpar,param1,error=0;
  unsigned short int direccion;
  int mrows, ncols,i,j,nfpar;
  unsigned long count = 0;
  unsigned long nWrite;
  unsigned long longitud, rlongitud;
  char buf[4096];
  char par[16]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  
  // comprobacion del numero de parametros de entrada y salida.
  
  if ((nrhs !=3) && (nrhs !=2)) 
    mexErrMsgTxt("Error. Input parameters don't match: [error] = USBAERSend(hnd,ArrayDat [,ArrayPar])");
  //if(nlhs != NUM_PARAM_SALIDA) 
  //  mexErrMsgTxt("Error. Output parameters don't match: [error] = USBAERSend(hnd,ArrayDat [,ArrayPar])");
    
  /* comprueba que el primer argumento es el manejador (un escalar). */
  if(!mxIsDouble(prhs[0]) || mxIsComplex(prhs[0]) || mxGetN(prhs[0])*mxGetM(prhs[0]) != 1 ) {
    mexErrMsgTxt("Parameter 1 is not an escalar.");   
  }  
  
    /* Comprueba que el segundo argumento es una matriz de eventos de nx1 */
  if(!mxIsDouble(prhs[1]) || mxIsComplex(prhs[1]) || mxGetN(prhs[1])!=1 ) {
    mexErrMsgTxt("Parameter 2 is not a Nx1 numeric matrix.");   
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
     for(i=0;i<nfpar;i++) {par[i]=fpar[i]; //type conversion
       //printf("%d ",fpar[i]);
     }
     }
     
  param1 = mxGetScalar(prhs[0]); // el manejador
  a_ipod = mxGetPr(prhs[1]);     // la matriz de eventos
  mrows = mxGetM(prhs[1]);
  ncols = mxGetN(prhs[1]);
  //if((mrows%64)||(mrows)>4097)
  //      mexErrMsgTxt("Event vector size should be multiple of 64 and less than 4097");
  // recupero la direccion en la que esta la estructura del manejador del dispositivo en memoria.
  hDevice=LeerManejadorMatlab(param1);

  if (hDevice!=INVALID_HANDLE_VALUE){
      // trabajo con los eventos....
  
                        longitud = mrows; if(longitud%64)rlongitud=longitud+(64-(longitud%64));else rlongitud=longitud;
                        buf[0]='A';
                        buf[1]='T';
                        buf[2]='C';
                        buf[3]= 1;   // comando 1 es grabar RAM
                        for(i=4;i<8;i++)
                                buf[i]=(longitud>>(8*(i-4)))&0xff;
                        for(i=8;i<24;i++) {
                                //buf[i]=a_ipod[i-8];
                                buf[i]=par[i-8];
                                //printf("%d ",par[i-8]);
                        }
                        WriteFile(hDevice, buf,(unsigned long) 64, &nWrite, NULL); //Write command
                        //
                       j=0; //number of elements already written.
                       do
                        {if(rlongitud>=4096)
                            {
                            for(i=0;i<4096;i++) buf[i]=a_ipod[i+j];//Type conv
   	                        WriteFile(hDevice, buf, (unsigned long)4096, &nWrite, NULL);
   	                        }
   	                     else
   	                        {
   	                        for(i=0;i<longitud;i++) buf[i]=a_ipod[i+j];//Type conv
   	                        WriteFile(hDevice, buf, (unsigned long)rlongitud, &nWrite, NULL);
   	                        }
   	                        rlongitud-=nWrite;longitud-=nWrite;
   	                        j+=nWrite;
                        }
                        while(rlongitud);
  } else {
      error=1;
  }
  
  plhs[0]=mxCreateScalarDouble((double) error);
}
