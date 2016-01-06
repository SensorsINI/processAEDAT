#include "mex.h"
#include <stdio.h>
#include <ctime>
#include "QPBO.cpp"
#include "QPBO_maxflow.cpp"
#include "QPBO_postprocessing.cpp"
#include "QPBO_extra.cpp"

/*
 * ACTION can be one of the following:
 *      'a'     ('alloc') for allocating data. NUM_LATTICES then has to be T
 *      'p'     ('process') to use pre-allocated lattices. Index with the number in NUM_LATTICES.
 *      'd'     ('dealloc') to deallocate all latices.
 */
#define ACTION      prhs[0]


#define ACTION_ALLOCATE 'a'
#define ACTION_PROCESS 'p'
#define ACTION_DEALLOCATE 'd'


#define NUM_NODES prhs[1]
#define UNARY prhs[2]
#define PAIRWISE prhs[3]

//#define DEBUG_OUTPUT 1


// Global definitions
QPBO<double> *qpbo = 0;
int *labels = 0;
int *labels_toOne = 0;

void mexFunction( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] )
{
    char action = ((char*)mxGetChars(ACTION))[0];
    
    if (action==ACTION_ALLOCATE)
    {
        #ifdef DEBUG_OUTPUT
            mexPrintf("======== Starting QPBO Prealloc =========\n");
        #endif
        int numNodes = (int)mxGetScalar(NUM_NODES);        
        
        qpbo = new QPBO<double>(numNodes,numNodes*4);
        labels = new int[numNodes];
        labels_toOne = new int[numNodes];
        
        #ifdef DEBUG_OUTPUT
            mexPrintf("======== Starting QPBO Prealloc Finished =========\n");
        #endif
        
    }
    else if (action==ACTION_PROCESS)
    {
        #ifdef DEBUG_OUTPUT
            mexPrintf("======== Starting QPBO Processing =========\n");
        #endif
        
        int numNodes = (int)mxGetScalar(NUM_NODES);                
        
        qpbo->Reset();
        qpbo->AddNode(numNodes);
        
        #ifdef DEBUG_OUTPUT
            mexPrintf("======== QPBO Re-Init finished =========\n");
        #endif

        
        //int numNodes = static_cast<int>(*mxGetPr(NUM_NODES));
        double *unary = mxGetPr(UNARY);
        double *pairwise = mxGetPr(PAIRWISE);
        int m_unary = mxGetM(UNARY);
        int n_unary = mxGetN(UNARY);
        int m_pairwise = mxGetM(PAIRWISE);
        int n_pairwise = mxGetN(PAIRWISE);
        //mexPrintf("nodes=%d\n",numNodes);
        //mexPrintf("unar_m=%d,unary_n=%d\n",m_unary,n_unary);
        //mexPrintf("pairwise_m=%d,pairwise_n=%d\n",m_pairwise,n_pairwise);

        //add terms
        int column;
        if(n_pairwise > 0){
            for(column = 0; column < n_pairwise ; column++){
    //             mexPrintf("Adding pairwise term (%d,%d) (%f,%f,%f,%f)\n",static_cast<int>(pairwise[column*6]-1),static_cast<int>(pairwise[column*6+1]-1),(pairwise[column*6+2]),(pairwise[column*6+3]),(pairwise[column*6+4]),(pairwise[column*6+5]));//(pairwise[column*6+3]),(pairwise[column*6+4]),(pairwise[column*6+5]));
                qpbo->AddPairwiseTerm(static_cast<int>(pairwise[column*6]-1),static_cast<int>(pairwise[column*6+1]-1),(pairwise[column*6+2]),(pairwise[column*6+3]),(pairwise[column*6+4]),(pairwise[column*6+5]));
            }
        }
        for(column=0;column<n_unary;column++){
    //         mexPrintf("Adding unary term (%d) (%d,%d)\n",static_cast<int>(unary[column*3]-1),static_cast<int>(unary[column*3+1]),static_cast<int>(unary[column*3+2]));
            qpbo->AddUnaryTerm(static_cast<int>(unary[column*3]-1),(unary[column*3+1]),(unary[column*3+2]));
        }
    
        qpbo->MergeParallelEdges();
        qpbo->Solve();
        qpbo->ComputeWeakPersistencies();
    
        for(int i = 0;i<numNodes;i++){
            labels[i] = (qpbo->GetLabel(i));
            //mexPrintf("Node %d is in %d\n",i,qpbo.GetLabel(i));
        }
        double energy_toZero = qpbo->ComputeTwiceEnergy(0);
    

        for(int i = 0;i<numNodes;i++){
            if(labels[i] < 0){
                labels_toOne[i]=1;
            }else{
                labels_toOne[i] = labels[i];
            }
    
        }
        double energy_toOne = qpbo->ComputeTwiceEnergy(labels_toOne);
    
    
    
        //return labeling
        plhs[0] = mxCreateDoubleMatrix(numNodes,1,mxREAL);
        plhs[1] = mxCreateDoubleMatrix(1,1,mxREAL);
        double *output = mxGetPr(plhs[0]);
        double *energy_out = mxGetPr(plhs[1]);
        if(energy_toZero < energy_toOne){
            for(int i = 0;i<numNodes;i++){
                if(labels[i] < 0){
                    output[i]=0.;
                }else{
                    output[i] = static_cast<double>(labels[i]);
                }
            }
            energy_out[0] = energy_toZero;
        }else{
    
            for(int i = 0;i<numNodes;i++){
                output[i] = static_cast<double>(labels_toOne[i]);
            }
            energy_out[0] = energy_toOne;
        }

        #ifdef DEBUG_OUTPUT
            mexPrintf("======== Finished QPBO processing =========\n");
        #endif
        

    }
    else
    {
        #ifdef DEBUG_OUTPUT
            mexPrintf("======== Starting QPBO dealloc =========\n");
        #endif

        if(labels)
        {
            delete [] labels;
            labels = 0;
        }
        if (labels_toOne)
        {
            delete [] labels_toOne;
            labels_toOne = 0;
        }
        if (qpbo)
        {
            delete qpbo;
            qpbo = 0;
        }
        #ifdef DEBUG_OUTPUT
            mexPrintf("======== Finished QPBO dealloc =========\n");
        #endif

    }
    
}


