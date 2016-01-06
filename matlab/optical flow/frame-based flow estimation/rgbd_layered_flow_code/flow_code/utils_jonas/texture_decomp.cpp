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
    

        

    #ifdef DEBUG_OUTPUT
        printf("return OK\n"); 
    #endif


    return;
}

// It is important to note that the data inside the array is in column major order. 
// Instead of reading a matrix's values across and then down, the values are read down and then across. 
// This is contrary to how C indexing works and means that special care must be taken 
// when accessing the array's elements. To access the data inside of mxArrays, use the API functions (see below)
