
// input flow field, (u,v) and im
// construct the linear operator matrix A for linear backward interpolation using (u,v)
// adjoint operator: output = A'*im(:)

#include "math.h"
#include "mex.h"

#define TOL 1e-6

// Compile using:  mex imwarp_adjoint_operator.cpp

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
    const mxArray *uData, *vData, *imData;
    double *uValues, *vValues, *outMatrix, *imValues;

    int rowLen, colLen, nPixels, nzmax;
    int i,j, floor_x, floor_y;
    double alpha_x, alpha_y, x, y;


    //Copy input pointer
    uData = prhs[0];
    vData = prhs[1];
    imData = prhs[2];

    //Get data
    uValues = mxGetPr(uData);
    vValues = mxGetPr(vData);
    imValues = mxGetPr(imData);

    colLen  = mxGetN(uData);	// number of columns
    rowLen  = mxGetM(uData);	// number of rows
    nPixels = colLen*rowLen;

    nzmax   = 10*nPixels;
    //Allocate memory and assign output pointer
    plhs[0] = mxCreateDoubleMatrix(rowLen, colLen, mxREAL); //mxReal is our data-type

    //Get a pointer to the data space in our newly allocated memory
    outMatrix = mxGetPr(plhs[0]);



    // the maxtir is column indexed as in Matlab
    for(i=0;i<colLen;i++)
    {
        for(j=0;j<rowLen;j++)
        {
            x = i+uValues[(i*rowLen) + j];	// horizontal new position
            y = j+vValues[(i*rowLen) + j]; 	// vertical new position

//             if ( (x>-TOL) && (x<=colLen-1) && (y>-TOL) && (y<=rowLen-1) ) // bug if x>-TOL & x<0 or y
            if ( (x>0) && (x<=colLen-1) && (y>0) && (y<=rowLen-1) )
            {
                
//                 if ( (x<0) || (y<0) )
//                 {
//                     printf("%d\t %d \t %f \t %f\n", i,j, x, y);
//                 }
                
                floor_x = floor(x);
                floor_y = floor(y);
                alpha_x = x-floor_x;
                alpha_y = y-floor_y;

                outMatrix[ (floor_x*rowLen+floor_y) ] += (1-alpha_x)*(1-alpha_y) * imValues[(i*rowLen) + j];
                outMatrix[ ((floor_x+1)*rowLen+floor_y) ] += alpha_x*(1-alpha_y)* imValues[(i*rowLen) + j];
                outMatrix[ (floor_x*rowLen+floor_y+1) ] += (1-alpha_x)*alpha_y* imValues[(i*rowLen) + j];
                outMatrix[ ((floor_x+1)*rowLen+floor_y+1)] += alpha_x*alpha_y* imValues[(i*rowLen) + j];

            }

        }

    }

   return;
}

