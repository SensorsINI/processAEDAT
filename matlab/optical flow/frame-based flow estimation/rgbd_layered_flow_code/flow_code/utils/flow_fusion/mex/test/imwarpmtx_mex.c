#include "math.h"
#include "mex.h"

/* Compile using "mex imwarpmtx_mex.c".*/

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
    mxArray *uData, *vData;
    double *uValues, *vValues, *outMatrix;

    int rowLen, colLen, nPixels;
    int i,j;
    double alpha_x, alpha_y, x, y, floor_x, floor_y;


    //Copy input pointer
    uData = prhs[0];
    vData = prhs[0];

    //Get data
    uValues = mxGetPr(uData);
    vValues = mxGetPr(vData);
    rowLen  = mxGetN(uData);
    colLen  = mxGetM(uData);
    nPixels = rowLen*colLen;

    //Allocate memory and assign output pointer
    plhs[0] = mxCreateDoubleMatrix(nPixels, nPixels, mxREAL); //mxReal is our data-type

    //Get a pointer to the data space in our newly allocated memory
    outMatrix = mxGetPr(plhs[0]);

    for(i=0;i<rowLen;i++)
    {
        for(j=0;j<colLen;j++)
        {
            x = j+uValues[(i*colLen) + j];
            y = i+vValues[(i*colLen) + j];
            if ( (x>0) && (x<colLen) && (y>0) && (y<rowLen) )
            {
                floor_x = floor(x);
                floor_y = floor(y);
                alpha_x = x-floor_x;
                alpha_y = x-floor_y;

                outMatrix[ (i*colLen + j)*nPixels + (floor_x*colLen+floor_y) ] += (1-alpha_x)*(1-alpha_y);
                outMatrix[ (i*colLen + j)*nPixels + ((floor_x+1)*colLen+floor_y) ] += alpha_x*(1-alpha_y);
                outMatrix[ (i*colLen + j)*nPixels + (floor_x*colLen+floor_y+1) ] += (1-alpha_x)*alpha_y;
                outMatrix[ (i*colLen + j)*nPixels + ((floor_x+1)**colLen+floor_y+1) ] += alpha_x*alpha_y;

            }


        }
    }

   return;
}

