#include <cmath>
#include <iostream>

#include <vector>

#include "mex.h"

// #define DEBUG_OUTPUT 
// Compile using    mex perform_dense_message_passing_mex.cpp  permutohedral.cpp bipartitedensecrf.cpp densecrf.cpp util.cpp


#define VALS prhs[0]
#define NUM_PX prhs[1]
#define CAN_UV prhs[2]
#define F0 prhs[3]

#define OUT_U plhs[0]
#define OUT_V plhs[1]



void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
    #ifdef DEBUG_OUTPUT
        mexPrintf("\tDEBUG:: Starting... \n");
    #endif    

    const int *val_dim = mxGetDimensions(VALS);
    int valSize = val_dim[0]*val_dim[1];
    
    //int *vals = (int*)mxGetData(VALS);
    //unsigned char *f0 = (unsigned char *)mxGetData(F0);
    double *can_uv = mxGetPr(CAN_UV);
    
    double *vals = (double*)mxGetData(VALS);
    double *f0 = (double *)mxGetData(F0);
    
    int num_px = (int) mxGetScalar(NUM_PX);
    
    OUT_U = mxCreateDoubleMatrix(1,val_dim[1],mxREAL);
    OUT_V = mxCreateDoubleMatrix(1,val_dim[1],mxREAL);
    
    double *out_u = mxGetPr(OUT_U);
    double *out_v = mxGetPr(OUT_V);
    
    //double *u1,*u2,*v1,*v2,*u1p,*u2p,*v1p,*v2p;
    //double *f0p, *f1p;
    double *u1,*u2,*v1,*v2;
    double *uout = out_u;
    double *vout = out_v;
    
    //unsigned char *f0p = f0;
    //unsigned char *f1p = f0 + 1;
    
    //int *val = vals;
    
    double *f0p = f0;
    
    double *val = vals;
    
    for (int i=0; i < valSize; i+=2)
    {
        u1 = can_uv + (int)(*val++) - 1 + (int)(*f0p++)*2*num_px;
        v1 = u1 + num_px;
        
        u2 = can_uv + (int)(*val++) - 1 + (int)(*f0p++) * 2 * num_px;
        v2 = u2 + num_px;
        
        *uout++ = *u1-*u2;
        *vout++ = *v1-*v2;
        
        
        //~ u1 = can_uv + vals[i] -1;
        //~ u2 = can_uv + vals[i+1] - 1;
        //~ v1 = u1 + num_px;
        //~ v2 = u2 + num_px;
        //~ 
        //~ u1p = u1 + (*f0p++ ? 2*num_px : 0);
        //~ u2p = u2 + (*f0p++ ? 2*num_px : 0);
        //~ v1p = v1 + (*f1p++ ? 2*num_px : 0);
        //~ v2p = v2 + (*f1p++ ? 2*num_px : 0);
        //~ 
        //~ *uout++ = *u1-*u2;
        //~ *uout++ = *u1-*u2p;
        //~ *uout++ = *u1p-*u2;
        //~ *uout++ = *u1p-*u2p;
        //~ 
        //~ *vout++ = *v1-*v2;
        //~ *vout++ = *v1-*v2p;
        //~ *vout++ = *v1p-*v2;
        //~ *vout++ = *v1p-*v2p;
    }
        
        

    #ifdef DEBUG_OUTPUT
        printf("return OK\n"); 
    #endif


    return;
}

// It is important to note that the data inside the array is in column major order. 
// Instead of reading a matrix's values across and then down, the values are read down and then across. 
// This is contrary to how C indexing works and means that special care must be taken 
// when accessing the array's elements. To access the data inside of mxArrays, use the API functions (see below)
