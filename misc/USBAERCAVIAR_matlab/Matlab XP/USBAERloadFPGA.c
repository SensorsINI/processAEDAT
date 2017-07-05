#include "mex.h"
#include "USBAERCommon.h"
#include <string.h>
//#include "devintf.h"	// DriverWorks
#define NUM_PARAM_ENTRADA 2
#define NUM_PARAM_SALIDA 1


void mexFunction( int nlhs, mxArray *plhs[],
                  int nrhs, const mxArray *prhs[])
{

  DWORD Error=0;
  DWORD param1;
  double man_matlab;
  char DevName[32],*kk,buf[64];
  unsigned int len,i,j,longitud,nWrite,count=0;
  FILE *fileinput;
  // comprobacion del numero de parametros de entrada y salida.
    
  
  if(nrhs != NUM_PARAM_ENTRADA) 
    mexErrMsgTxt("Error. Input parameters don't match: [error] = USBAERloadFPGA(handle,FileName)");
  //if(nlhs != NUM_PARAM_SALIDA) 
  //  mexErrMsgTxt("Error. Output parameters don't match: [error] = USBAERloadFPGA(handle,FileName)");
  if(!mxIsDouble(prhs[0]) || mxIsComplex(prhs[0]) || mxGetN(prhs[0])*mxGetM(prhs[0]) != 1 ) 
    mexErrMsgTxt("Parameter 1 is not a scalar.");   
 
  
  len = mxGetN(prhs[1]);
  if (len > 31) mexErrMsgTxt("Error. Device Name too long. Use a string with 31 characteres as maximum.");

  kk=mxGetPr(prhs[1]);
  param1=mxGetScalar(prhs[0]);
  
  for(i=0,j=0;i<2*len;i+=2,j++){  DevName[j]=kk[i];} // printf("%d, %s\n",len,DevName);}
  DevName[j]=0;
  
  fileinput= fopen(DevName,"rb");
  if (fileinput!=NULL)
    {hDevice=LeerManejadorMatlab(param1);

        if (hDevice!=INVALID_HANDLE_VALUE)
                   {
                        fseek(fileinput,0,SEEK_END);
                        longitud = ftell(fileinput);
                        fseek(fileinput,0,SEEK_SET);

                        buf[0]='A';
                        buf[1]='T';
                        buf[2]='C';
                        buf[3]= 0;   // comando
                        for(i=4;i<8;i++)
                                buf[i]=(longitud>>(8*(i-4)))&0xff;
                        WriteFile(hDevice, buf,(unsigned long) 64, &nWrite, NULL);

                      while(!feof(fileinput))
                        {
                         count += fread( buf, sizeof( char ), 64, fileinput );
	                     WriteFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);
                        if(nWrite != 64)
                                {Error=3;}
                         }    
                   }
           else Error=2;
    }
  else 
    {Error=1;}
     plhs[0]=mxCreateScalarDouble((double) Error);
}
