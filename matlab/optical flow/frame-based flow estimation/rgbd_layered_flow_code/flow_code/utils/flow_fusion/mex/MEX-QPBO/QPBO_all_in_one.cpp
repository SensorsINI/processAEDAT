#include "mex.h"
#include <stdio.h>
#include <ctime>
#include "QPBO.cpp"
#include "QPBO_maxflow.cpp"
#include "QPBO_postprocessing.cpp"
#include "QPBO_extra.cpp"
void mexFunction( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] )
{
    int numNodes = static_cast<int>(*mxGetPr(prhs[0]));
    double *unary = mxGetPr(prhs[1]);
    double *pairwise = mxGetPr(prhs[2]);
    int m_unary = mxGetM(prhs[1]);
    int n_unary = mxGetN(prhs[1]);
    int m_pairwise = mxGetM(prhs[2]);
    int n_pairwise = mxGetN(prhs[2]);
    //mexPrintf("nodes=%d\n",numNodes);
    //mexPrintf("unar_m=%d,unary_n=%d\n",m_unary,n_unary);
    //mexPrintf("pairwise_m=%d,pairwise_n=%d\n",m_pairwise,n_pairwise);
    QPBO<double> *qpbo = new QPBO<double>(numNodes,numNodes*4);
    
    qpbo->AddNode(numNodes);
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
    
        int *labels = new int[numNodes];
        for(int i = 0;i<numNodes;i++){
            labels[i] = (qpbo->GetLabel(i));
            //mexPrintf("Node %d is in %d\n",i,qpbo.GetLabel(i));
        }
        double energy_toZero = qpbo->ComputeTwiceEnergy(0);
    
        int *labels_toOne = new int[numNodes];
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
    
        delete [] labels;
        delete [] labels_toOne;
        delete qpbo;
    
}


