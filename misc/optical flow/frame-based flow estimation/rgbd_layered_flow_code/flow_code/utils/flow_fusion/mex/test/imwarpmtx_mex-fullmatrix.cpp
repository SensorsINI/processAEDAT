#include "math.h"
#include "mex.h"

#define TOL 1e-6

/* Compile using "mex imwarpmtx_mex.c".*/

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
    const mxArray *uData, *vData;
    double *uValues, *vValues, *outMatrix;

    int rowLen, colLen, nPixels, nzmax;
    int i,j, floor_x, floor_y;
    double alpha_x, alpha_y, x, y;


    //Copy input pointer
    uData = prhs[0];
    vData = prhs[1];

    //Get data
    uValues = mxGetPr(uData);
    vValues = mxGetPr(vData);

    colLen  = mxGetN(uData);	// number of columns
    rowLen  = mxGetM(uData);	// number of rows
    nPixels = colLen*rowLen;

    nzmax   = 10*nPixels;
    //Allocate memory and assign output pointer
    plhs[0] = mxCreateDoubleMatrix(nPixels, nPixels, mxREAL); //mxReal is our data-type

    //Get a pointer to the data space in our newly allocated memory
    outMatrix = mxGetPr(plhs[0]);



    // the maxtir is column indexed as in Matlab
    for(i=0;i<colLen;i++)
    {
        for(j=0;j<rowLen;j++)
        {
            x = i+uValues[(i*rowLen) + j];	// horizontal new position
            y = j+vValues[(i*rowLen) + j]; 	// vertical new position
            if ( (x>-TOL) && (x<=colLen-1) && (y>-TOL) && (y<=rowLen-1) )
            {
                floor_x = floor(x);
                floor_y = floor(y);
                alpha_x = x-floor_x;
                alpha_y = y-floor_y;

                outMatrix[ (i*rowLen + j) + (floor_x*rowLen+floor_y)*nPixels ] += (1-alpha_x)*(1-alpha_y);
                outMatrix[ (i*rowLen + j) + ((floor_x+1)*rowLen+floor_y)*nPixels ] += alpha_x*(1-alpha_y);
                outMatrix[ (i*rowLen + j) + (floor_x*rowLen+floor_y+1)*nPixels ] += (1-alpha_x)*alpha_y;
                outMatrix[ (i*rowLen + j) + ((floor_x+1)*rowLen+floor_y+1)*nPixels ] += alpha_x*alpha_y;

            }

        }

    }

   return;
}

