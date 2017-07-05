
// input flow field, (u,v) and im, and out-of-boundary value
// output, bilinear interpolation result and 

#include "math.h"
#include "mex.h"

#define TOL 1e-6
#define DOBV 1e6 // default out of boundary value

// Compile using:  mex imwarp_bicubic_mex.cpp

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
    const mxArray *imData;
    double *xValues, *yValues, *oIm, *oImx, *oImy, *im, *imx, *imy, *imxy;

    int rowLen, colLen, nPixels;
    int i,j, floor_x, floor_y, u, v, m,n, offset;
    double alpha_x, alpha_y, x, y;
    double obv; // out-of-boundary value

    obv = mxGetNaN();

    //Get data
    im      = mxGetPr(prhs[0]);
    imx     = mxGetPr(prhs[1]);
    imy     = mxGetPr(prhs[2]);
    imxy    = mxGetPr(prhs[3]);
    xValues = mxGetPr(prhs[4]); // index column    
    yValues = mxGetPr(prhs[5]); // index row
    
    // Get data size
    colLen  = mxGetN(prhs[0]);	// number of columns
    rowLen  = mxGetM(prhs[0]);	// number of rows    
    nPixels = colLen*rowLen;    

    //Allocate memory and assign output pointer
    plhs[0] = mxCreateDoubleMatrix(rowLen, colLen, mxREAL); //mxReal is our data-type
    //Get a pointer to the data space in our newly allocated memory
    oIm  = mxGetPr(plhs[0]);
    if (nlhs > 1)
    {
        plhs[1] = mxCreateDoubleMatrix(rowLen, colLen, mxREAL); 
        plhs[2] = mxCreateDoubleMatrix(rowLen, colLen, mxREAL); 
        oImx = mxGetPr(plhs[1]);
        oImy = mxGetPr(plhs[2]);
    }   
    
    // bicubic interpolation matrix
//     static int  W[16*16] = { 
//         1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
//         0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,
//         -3,  0,  0,  3,  0,  0,  0,  0, -2,  0,  0, -1,  0,  0,  0,  0,  
//         2,  0,  0, -2,  0,  0,  0,  0,  1,  0,  0,  1,  0,  0,  0,  0,
//         0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
//         0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,
//         0,  0,  0,  0, -3,  0,  0,  3,  0,  0,  0,  0, -2,  0,  0, -1,
//         0,  0,  0,  0,  2,  0,  0, -2,  0,  0,  0,  0,  1,  0,  0,  1,
//         -3,  3,  0,  0, -2, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
//         0,  0,  0,  0,  0,  0,  0,  0, -3,  3,  0,  0, -2, -1,  0,  0,
//         9, -9,  9, -9,  6,  3, -3, -6,  6, -6, -3,  3,  4,  2,  1,  2,
//         -6,  6, -6,  6, -4, -2,  2,  4, -3,  3,  3, -3, -2, -1, -1, -2,
//         2, -2,  0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
//         0,  0,  0,  0,  0,  0,  0,  0,  2, -2,  0,  0,  1,  1,  0,  0,
//         -6,  6, -6,  6, -3, -3,  3,  3, -4,  4,  2, -2, -2, -2, -1, -1,
//         4, -4,  4, -4,  2,  2, -2, -2,  2, -2, -2,  2,  1,  1,  1,  1};

    // the maxtir is column indexed as in Matlab
    for(i=0;i<colLen;i++)
    {
        for(j=0;j<rowLen;j++)
        {
            x = xValues[(i*rowLen) + j];	// horizontal new position
            y = yValues[(i*rowLen) + j]; 	// vertical new position

            if ( (x>0) && (x<=colLen-1) && (y>0) && (y<=rowLen-1) )
            {
                
                floor_x = floor(x);
                floor_y = floor(y);
                alpha_x = x-floor_x;
                alpha_y = y-floor_y;

                int indx[2][2] = {{0,3}, {1, 2}};
                double coef[16];
                double tmpI[16];

                // 0 ->1
                // 3 <-2 
                // Pack a temporary vector
        
                for(m=0;m<=1;m++)
                    for(n=0;n<=1;n++)
                    {
                        u=floor_x+m;
                        v=floor_y+n;
                        offset=(u*rowLen+v);
                        tmpI[0+indx[m][n]] = im[offset];
                        tmpI[4+indx[m][n]] = imx[offset];
                        tmpI[8+indx[m][n]] = imy[offset];
                        tmpI[12+indx[m][n]]= imxy[offset];
                    }
        
                double tmp;
/*                for (m=0;m<16;m++)
                {
                    tmp = 0.0;
                    for (n=0;n<16;n++) tmp += (double)W[m*16+n]*tmpI[n];
                    coef[m] = tmp;        
                }*/
                coef[0] = + tmpI[0];
                coef[1] = + tmpI[8];
                coef[2] =  - 3 *tmpI[0] + 3 *tmpI[3] - 2 *tmpI[8]- tmpI[11];
                coef[3] =  + 2 *tmpI[0] - 2 *tmpI[3]+ tmpI[8]+ tmpI[11];
                coef[4] = + tmpI[4];
                coef[5] = + tmpI[12];
                coef[6] =  - 3 *tmpI[4] + 3 *tmpI[7] - 2 *tmpI[12]- tmpI[15];
                coef[7] =  + 2 *tmpI[4] - 2 *tmpI[7]+ tmpI[12]+ tmpI[15];
                coef[8] =  - 3 *tmpI[0] + 3 *tmpI[1] - 2 *tmpI[4]- tmpI[5];
                coef[9] =  - 3 *tmpI[8] + 3 *tmpI[9] - 2 *tmpI[12]- tmpI[13];
                coef[10] =  + 9 *tmpI[0] - 9 *tmpI[1] + 9 *tmpI[2] - 9 *tmpI[3] + 6 *tmpI[4] + 3 *tmpI[5] - 3 *tmpI[6] - 6 *tmpI[7] + 6 *tmpI[8] - 6 *tmpI[9] - 3 *tmpI[10] + 3 *tmpI[11] + 4 *tmpI[12] + 2 *tmpI[13]+ tmpI[14] + 2 *tmpI[15];
                coef[11] =  - 6 *tmpI[0] + 6 *tmpI[1] - 6 *tmpI[2] + 6 *tmpI[3] - 4 *tmpI[4] - 2 *tmpI[5] + 2 *tmpI[6] + 4 *tmpI[7] - 3 *tmpI[8] + 3 *tmpI[9] + 3 *tmpI[10] - 3 *tmpI[11] - 2 *tmpI[12]- tmpI[13]- tmpI[14] - 2 *tmpI[15];
                coef[12] =  + 2 *tmpI[0] - 2 *tmpI[1]+ tmpI[4]+ tmpI[5];
                coef[13] =  + 2 *tmpI[8] - 2 *tmpI[9]+ tmpI[12]+ tmpI[13];
                coef[14] =  - 6 *tmpI[0] + 6 *tmpI[1] - 6 *tmpI[2] + 6 *tmpI[3] - 3 *tmpI[4] - 3 *tmpI[5] + 3 *tmpI[6] + 3 *tmpI[7] - 4 *tmpI[8] + 4 *tmpI[9] + 2 *tmpI[10] - 2 *tmpI[11] - 2 *tmpI[12] - 2 *tmpI[13]- tmpI[14]- tmpI[15];
                coef[15] =  + 4 *tmpI[0] - 4 *tmpI[1] + 4 *tmpI[2] - 4 *tmpI[3] + 2 *tmpI[4] + 2 *tmpI[5] - 2 *tmpI[6] - 2 *tmpI[7] + 2 *tmpI[8] - 2 *tmpI[9] - 2 *tmpI[10] + 2 *tmpI[11]+ tmpI[12]+ tmpI[13]+ tmpI[14]+ tmpI[15];
        
                tmp = 0.0;		
                
                double pax[4], pay[4];
                for (m=0;m<4;m++)
                {
                    pax[m] = pow(alpha_x,m);
                    pay[m] = pow(alpha_y,m);
                }
                
                
                for (m=0; m<4; m++)
                    for(n=0; n<4; n++)
                        tmp += coef[m*4+n]*pax[m]*pay[n];
                oIm[(i*rowLen+j)] = tmp;
                
                if (nrhs >1)
                {
                    tmp = 0.0;		
                    for (m=1; m<4; m++)
                        for(n=0; n<4; n++)
                            tmp += coef[m*4+n]*pax[m-1]*pay[n]*m;
                    oImx[(i*rowLen+j)] = tmp;

                    tmp = 0.0;		
                    for (m=0; m<4; m++)
                        for(n=1; n<4; n++)
                            tmp += coef[m*4+n]*pax[m]*pay[n-1]*n;
                    oImy[(i*rowLen+j)] = tmp;                    
                }

                
            }  
            else
            {
                 oIm[ (i*rowLen+j) ] = obv;
                oImx[ (i*rowLen+j) ] = obv;
                oImy[ (i*rowLen+j) ] = obv;
            }
        }

    }

   return;
}

