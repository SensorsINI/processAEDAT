#include "mex.h"
#include <math.h>
void mexFunction( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] )
{
    double *f_0 = mxGetPr(prhs[0]);
    double *f_1 = mxGetPr(prhs[1]);
    double *truthtable = mxGetPr(prhs[2]);
    double *cliques = mxGetPr(prhs[3]);
    int numCliques = mxGetM(prhs[3]);
    int order = mxGetN(prhs[3]);
    int truthTableSize = mxGetN(prhs[2]);
    //plhs[0] = mxCreateDoubleMatrix(truthTableSize*numCliques,order,mxREAL);
    int numRows = truthTableSize*numCliques;
    double *out = mxGetPr(prhs[4]);
    
    //we need to run over every clique vec
    for(int i = 0; i < numCliques;i++){
        //and over every truthtable entry
        for(int n = 0; n < truthTableSize; n++){
            
            for(int j = 0; j < order; j++){
                //we assume that the clique vector is arranged to order X numcliques
                int nodeIndex  = static_cast<int>(cliques[i + j*numCliques]);
//                 mexPrintf(" cn: %d ",nodeIndex);
                int ttVal = static_cast<int>(truthtable[j+order*n]);
//                 mexPrintf(" tt %d, real %f",ttVal,(1-ttVal)*f_0[nodeIndex-1] + ttVal*f_1[nodeIndex-1]);
                out[j*numRows+n+i*truthTableSize] = (1-ttVal)*f_0[nodeIndex-1] + ttVal*f_1[nodeIndex-1];
            }
//             mexPrintf(" \n");
            
        }
        
    }
}
