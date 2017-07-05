#include <cmath>
#include <iostream>
#include <cstring>
#include <vector>

#include "mex.h"

// #define DEBUG_OUTPUT 
// Compile using    mex perform_dense_message_passing_mex.cpp  permutohedral.cpp bipartitedensecrf.cpp densecrf.cpp util.cpp


#define IMG prhs[0]
#define THETA prhs[1]
#define TAU prhs[2]
#define EPSILON prhs[3]
#define MAXITER prhs[4]

#define OUT plhs[0]

//#define DEBUG_OUTPUT 1

void dxm(double *in, double *out, int w, int h)
{
    double *in_p = in;
    double *in_p_shift = in;
    double *out_p = out;
    
    // First column: U values, unchanged.
    for (int i=0;i<h;i++)
    {
        *out_p++ = *in_p++;
    }
    
    for (int i=0; i < h*(w-1); i++)
    {
        *out_p++ = *in_p++ - *in_p_shift++;
    }
}


void dym(double *in, double *out, int w, int h)
{
    double *in_p = in;
    double *in_p_shift = in;
    double *out_p = out;
    
    // First row: U values, unchanged.
    for (int i=0;i<w;i++)
    {
        *out_p++ = *in_p++;
        
        for (int j=1;j<h;j++)
            *out_p++ = *in_p++ - *in_p_shift++;
        
        in_p_shift++;
    }
    
}


// computes dxp(IN)
void dxp(double *in, double *out, int w, int h)
{
    double *in_p = in+h;
    double *out_p = out;
    double *in_p_shift = in;
    
    for (int i=0; i < (w-1)*h; i++)
    {
        *out_p++ = *in_p++ - *in_p_shift++;
    }
    
    // Last column
    for (int i=0; i < h; i++)
    {
        *out_p++ = 0;
    }
}

void dyp(double *in, double *out, int w, int h)
{
    double *in_p = in+1;
    double *in_p_shift = in;
    double *out_p = out;
    
    // Last row: 0
    for (int i=0;i<w;i++)
    {
        for (int j=1;j<h;j++)
            *out_p++ = *in_p++ - *in_p_shift++;
        
        *out_p++ = 0;
        in_p++;
        in_p_shift++;
    }
}


// IN_OUT += IN2
void add(double *in_out, double *in2, int w, int h)
{
    double *in_out_p = in_out;
    
    double *in2_p = in2;
    
    for (int i=0;i<w*h;i++)
    {
        *in_out_p += *in2_p++;
        in_out_p++;
    }
}


// OUT = IN1 + A*IN2
void add_mul(double *in1, double *in2, double *out, double A, int w, int h)
{
    double *in1_p = in1;
    double *in2_p = in2;
    
    double *out_p = out;
    
    for (int i=0;i<w*h;i++)
    {
        *out_p++ = *in1_p++ + A* *in2_p++;
    }
}


void add_tau_epsilon(double *pu, double *u, double tau, double epsilon, int w, int h)
{
    double *pu_p = pu;
    double *u_p = u;
    
    for (int i=0;i<w*h;i++)
    {
        *pu_p += tau*(*u_p++ - epsilon * *pu_p);
        pu_p++;
    }
}

void reproject(double *pu1, double *pu2, int w, int h)
{
    double *pu1_p = pu1;
    double *pu2_p = pu2;
    double reg;
    
    for (int i=0;i<w*h;i++)
    {
        reg = *pu1_p * *pu1_p + *pu2_p * *pu2_p;
        reg = reg > 1 ? sqrt(reg) : 1;
        *pu1_p /= reg;
        *pu2_p /= reg;
        pu1_p++;
        pu2_p++;
    }
}


void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
    #ifdef DEBUG_OUTPUT
        mexPrintf("\tDEBUG:: Starting... \n");
    #endif    

    const int *img_dim = mxGetDimensions(IMG);
    int nChannels = img_dim[2];
    int height = img_dim[0];
    int width = img_dim[1];
    
    double *img = mxGetPr(IMG);
    
    
    OUT = mxCreateNumericArray(3, img_dim, mxDOUBLE_CLASS, mxREAL);
    double *out = mxGetPr(OUT);
    
    double theta = (double)mxGetScalar(THETA);
    double tau = (double)mxGetScalar(TAU);
    double epsilon = (double)mxGetScalar(EPSILON);
    double maxIter = (double)mxGetScalar(MAXITER);
    
    
    double *pu1 = (double*)malloc(width*height*sizeof(double));
    double *pu2 = (double*)malloc(width*height*sizeof(double));
    
    double *tmp1 = (double*)malloc(width*height*sizeof(double));
    double *tmp2 = (double*)malloc(width*height*sizeof(double));
    
    double *ux = (double*)malloc(width*height*sizeof(double));
    double *uy = (double*)malloc(width*height*sizeof(double));

    double *u = 0;
    
    
    
    for (int i=0; i < nChannels; i++)
    {
        #ifdef DEBUG_OUTPUT
            mexPrintf("Running channel %d\n",i);
        #endif
        
        u = img + i*width*height;
        
        memset(pu1,0,width*height*sizeof(double));
        memset(pu2,0,width*height*sizeof(double));
        
        for (int j=0; j < maxIter; j++)
        {
            #ifdef DEBUG_OUTPUT
                if (j%10 == 0)
                {
                    mexPrintf("\tRunning iteration %d\n",j);
                }
            #endif

            dxm(pu1,tmp1,width,height);
            dym(pu2,tmp2,width,height);
            
            // tmp1 = dxm(pu_1) + dym(pu_2)
            add(tmp1,tmp2,width,height);
            
            //tmp2 = u+theta*div_u
            add_mul(u,tmp1,tmp2,theta,width,height);
            
            //ux = dxp(tmp2)
            dxp(tmp2,ux,width,height);
            
            // uy = dyp(tmp2)
            dyp(tmp2,uy,width,height);
            
            add_tau_epsilon(pu1,ux,tau,epsilon,width,height);
            add_tau_epsilon(pu2,uy,tau,epsilon,width,height);
            
            reproject(pu1,pu2,width,height);
        }
        // tmp1 = dxm(pu1)
        dxm(pu1,tmp1,width,height);
        // tmp2 = dym(pu2)
        dym(pu2,tmp2,width,height);
        // tmp1 += tmp2
        add(tmp1,tmp2,width,height);
        
        //tmp2 = u + theta * tmp1
        add_mul(u,tmp1,tmp2,theta,width,height);
        memcpy(out,tmp2,width*height*sizeof(double));
        
        out += width*height;
    }
    
    //out = mxGetPr(OUT);
    //u = img;
    
    //memcpy(out,u,2*width*height*sizeof(double));
    //reproject(out,out+width*height,width,height);
        
    free(pu1);
    free(pu2);
    free(tmp1);
    free(tmp2);
    free(ux);
    free(uy);

    #ifdef DEBUG_OUTPUT
        printf("return OK\n"); 
    #endif
    
    //out = mxGetPr(OUT);
    //*out = 1.0;


    return;
}

// It is important to note that the data inside the array is in column major order. 
// Instead of reading a matrix's values across and then down, the values are read down and then across. 
// This is contrary to how C indexing works and means that special care must be taken 
// when accessing the array's elements. To access the data inside of mxArrays, use the API functions (see below)

