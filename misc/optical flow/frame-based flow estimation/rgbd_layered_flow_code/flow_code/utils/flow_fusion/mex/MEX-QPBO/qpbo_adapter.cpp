#include "mex.h"
#include <stdio.h>
#include <ctime>
#include "QPBO.cpp"
#include "QPBO_maxflow.cpp"
#include "QPBO_postprocessing.cpp"
#include "QPBO_extra.cpp"
#include "ObjectHandle.h"

int unlabeldnodes = 0;
bool firstrun = false;
int probecounter = 0;

//function forward defs
void myQPBO          (int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myAddNode       (int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myAddUnaryTerm       (int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myAddPairwiseTerm   (int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void mySolve        (int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myGetLabel   (int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myAllLabels   (int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myAllSegments(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myCreate_from_theta(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void mySetLabels(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myImprove(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myComputeWeakPersistencies(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myReset(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myAddMultipleNodes       ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] );
void myDestroy       ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] );
void myProbe       ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] );
void myGetEnergy       ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] );
void myMergeParallelEdges       ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] );
void mySave          (int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
void myAddTripleTerm ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] );
void myTestLabelings ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] );
void printAddedPairwiseTerm(int node1,int node2, double E00, double E01, double E10, double E11);
void printAddedUnaryTerm(int node1, double E0, double E1);

void mexFunction( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] )
{
    const char *function;
    function = (char *)mxArrayToString(prhs[0]);
    if(!strcmp(function,"QPBO")){
        //mexPrintf("Will call %s\n",function);
        myQPBO(nlhs,plhs,nrhs,prhs);
        
    }else if(!strcmp(function,"add_node")){
        //mexPrintf("Will call %s\n",function);
        myAddNode(nlhs,plhs,nrhs,prhs);
        
    }else if(!strcmp(function,"add_multiple_nodes")){
        //mexPrintf("Will call %s\n",function);
        myAddNode(nlhs,plhs,nrhs,prhs);
        
    }else if(!strcmp(function,"add_unary_term")){
        //mexPrintf("Will call %s\n",function);
        myAddUnaryTerm(nlhs,plhs,nrhs,prhs);
        
    }else if(!strcmp(function,"add_pairwise_term")){
        //mexPrintf("Will call %s\n",function);
        myAddPairwiseTerm(nlhs,plhs,nrhs,prhs);
        
    }else if(!strcmp(function,"solve")){
        //mexPrintf("Will call %s\n",function);
        mySolve(nlhs,plhs,nrhs,prhs);
        
    }else if(!strcmp(function,"get_label")){
        //mexPrintf("Will call %s\n",function);
        myGetLabel(nlhs,plhs,nrhs,prhs);
        
    }else if(!strcmp(function,"all_labels")){
        //mexPrintf("Will call %s\n",function);
        myAllLabels(nlhs,plhs,nrhs,prhs);
        
    }else if(!strcmp(function,"all_segments")){
        //mexPrintf("Will call %s\n",function);
        myAllSegments(nlhs,plhs,nrhs,prhs);
    }else if(!strcmp(function,"create_from_theta")){
        //mexPrintf("Will call %s\n",function);
        myCreate_from_theta(nlhs,plhs,nrhs,prhs);
        
    }else if(!strcmp(function,"set_labels")){
        //mexPrintf("Will call %s\n",function);
        mySetLabels(nlhs,plhs,nrhs,prhs);
        
    }else if(!strcmp(function,"compute_weak_persistencies")){
        //mexPrintf("Will cal %s\n",function);
        myComputeWeakPersistencies(nlhs,plhs,nrhs,prhs);
    }else if(!strcmp(function,"improve")){
        //mexPrintf("Will cal %s\n",function);
        myImprove(nlhs,plhs,nrhs,prhs);
    }else if(!strcmp(function,"reset")){
        //mexPrintf("Will cal %s\n",function);
        myReset(nlhs,plhs,nrhs,prhs);
    }else if(!strcmp(function,"destroy")){
        //mexPrintf("Will cal %s\n",function);
        myDestroy(nlhs,plhs,nrhs,prhs);
    }else if(!strcmp(function,"probe")){
        //mexPrintf("Will cal %s\n",function);
        myProbe(nlhs,plhs,nrhs,prhs);
    }else if(!strcmp(function,"energy")){
        //mexPrintf("Will cal %s\n",function);
        myGetEnergy(nlhs,plhs,nrhs,prhs);
    }else if(!strcmp(function,"merge")){
        //mexPrintf("Will cal %s\n",function);
        myMergeParallelEdges(nlhs,plhs,nrhs,prhs);
    }else if(!strcmp(function,"save")){
        //mexPrintf("Will cal %s\n",function);
        mySave(nlhs,plhs,nrhs,prhs);
    }else if(!strcmp(function,"test")){
        //mexPrintf("Will cal %s\n",function);
        myTestLabelings(nlhs,plhs,nrhs,prhs);
    }else if(!strcmp(function,"triple")){
        //mexPrintf("Will cal %s\n",function);
        myAddTripleTerm(nlhs,plhs,nrhs,prhs);
    }
    
    
    
}

void myQPBO ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    QPBO<double> *qpbo = new QPBO<double>(/*estimated # of nodes*/ 0, /*estimated # of edges*/ 0);
    //     mexPrintf("Pointer before: %#x, ", qpbo);
    ObjectHandle<QPBO<double> > *handle = new ObjectHandle<QPBO<double> >(qpbo);
    //     mexPrintf("Pointer after: %#x\n", qpbo);
    plhs[0] = handle->to_mex_handle();
    
    
}

void myAddNode       ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    plhs[0] = mxCreateNumericMatrix(1,1,mxINT32_CLASS,mxREAL);
    
    if(nrhs == 2){
        int *id = (int*)(mxGetPr(plhs[0]));
        *id = qpbo.AddNode();
        mexPrintf("Adding node with id %d\n",*id);
        mexPrintf("#params %d\n",nrhs);
        
    }else if(nrhs == 3){
        
        int numnodes = static_cast<int>(*(mxGetPr(prhs[2])));
        //mexPrintf("num nodes to add %d\n",numnodes);
        qpbo.AddNode(numnodes);
        //mexPrintf("Adding multiple nodes,first node with id %d\n",id);
        
        
    }else{
        mexPrintf("Wrong number of arguments\n");
    }
    
}


void myAddMultipleNodes       ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    plhs[0] = mxCreateNumericMatrix(1,1,mxINT32_CLASS,mxREAL);
    int numnodes = static_cast<int>(*(mxGetPr(prhs[2])));
    mexPrintf("num nodes to add %d\n",numnodes);
    int id = qpbo.AddNode(numnodes);
    mexPrintf("Adding multiple nodes,first node with id %d\n",id);
}




void myAddUnaryTerm       ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    // mexPrintf("Added unary: node=%d weights=(%f,%f) \n",static_cast<int>(*(mxGetPr(prhs[2]))),*(mxGetPr(prhs[3])),*(mxGetPr(prhs[4])));
    qpbo.AddUnaryTerm(static_cast<int>(*(mxGetPr(prhs[2]))),*(mxGetPr(prhs[3])),*(mxGetPr(prhs[4])));
    
    
}

void myAddPairwiseTerm   ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    int xi=static_cast<int>(*(mxGetPr(prhs[2])));
    int xj=static_cast<int>(*(mxGetPr(prhs[3])));
    double e00=(*(mxGetPr(prhs[4])));
    double e01=(*mxGetPr(prhs[5]));
    double e10=(*mxGetPr(prhs[6]));
    double e11=(*mxGetPr(prhs[7]));
    //mexPrintf("Added pairwise term:nodes=(%d,%d) weights=(%f,%f,%f,%f) \n",xi,xj,e00,e01,e10,e11);
    qpbo.AddPairwiseTerm(xi,xj,e00,e01,e10,e11);
    
    
}

void mySolve        ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    //qpbo.Save("myEnergy.txt");
    qpbo.Solve();
    //mexPrintf("Energy: %f \n",qpbo.ComputeTwiceEnergy());
    
}
void myGetLabel   ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    const int id = static_cast<int>(*(mxGetPr(prhs[2])));
    int *output;
    plhs[0] = mxCreateNumericMatrix(1,1,mxINT32_CLASS,mxREAL);
    output =(int*) mxGetPr(plhs[0]);
    output[0] = qpbo.GetLabel(id);
    
}

void myAllLabels   ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    int numNodes = qpbo.GetNodeNum();
    double *output;
    plhs[0] = mxCreateDoubleMatrix(1,numNodes,mxREAL);
    output =(mxGetPr(plhs[0]));
    
    for(int i = 0;i<numNodes;i++){
        output[i] = static_cast<double>(qpbo.GetLabel(i));
        //mexPrintf("Node %d is in %d\n",i,qpbo.GetLabel(i));
    }
    
    
}


void myCreate_from_theta(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    
    double *theta_p = mxGetPr(prhs[2]);
    double *theta_pq = mxGetPr(prhs[3]);
    int m_p = mxGetM(prhs[2]);
    int n_p = mxGetN(prhs[2]);
    int m_pq = mxGetM(prhs[3]);
    int n_pq = mxGetN(prhs[3]);
    //     mexPrintf("Got theta_p with m=%d n=%d\n",m_p,n_p);
    //     mexPrintf("Got theta_pq with m=%d n=%d\n",m_pq,n_pq);
    if (false){////n_p != numNodes || m_p != 2 ){
        mexErrMsgTxt("in create from theta");
    }else{
        int row;
        int column;
        int id;
        if(n_pq > 0){
            
            for(column = 0; column < n_pq ; column++){
                // mexPrintf("Adding pairwise term (%d,%d) (%f,%f,%f,%f)\n",static_cast<int>(theta_pq[column*6]-1),static_cast<int>(theta_pq[column*6+1]-1),(theta_pq[column*6+2]),(theta_pq[column*6+3]),(theta_pq[column*6+4]),(theta_pq[column*6+5]));//(theta_pq[column*6+3]),(theta_pq[column*6+4]),(theta_pq[column*6+5]));
                qpbo.AddPairwiseTerm(static_cast<int>(theta_pq[column*6]-1),static_cast<int>(theta_pq[column*6+1]-1),(theta_pq[column*6+2]),(theta_pq[column*6+3]),(theta_pq[column*6+4]),(theta_pq[column*6+5]));
                //printAddedPairwiseTerm(static_cast<int>(theta_pq[column*6]-1),static_cast<int>(theta_pq[column*6+1]-1),(theta_pq[column*6+2]),(theta_pq[column*6+3]),(theta_pq[column*6+4]),(theta_pq[column*6+5]));
            }
        }
        for(id=0;id<n_p;id++){
            qpbo.AddUnaryTerm(static_cast<int>(theta_p[id*3]-1),(theta_p[id*3+1]),(theta_p[id*3+2]));
            
        }
        
        
    }
    //qpbo.MergeParallelEdges();

}
void mySetLabels(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    double *labels =   mxGetPr(prhs[2]);
    int m_p = mxGetM(prhs[2]);
    int labeling [m_p];
    int id;
    for(id = 0; id <m_p;id++){
        labeling[id]=static_cast<int>(labels[id]);
        //         mexPrintf("Set label (%d) for node (%d)\n",static_cast<int>(labels[id]),id);
        //         qpbo.SetLabel(id,static_cast<int>(labels[id]));
    }
    qpbo.Improve(m_p,labeling);
    plhs[0] = mxCreateDoubleMatrix(1,1,mxREAL);
    double *energy = mxGetPr(plhs[0]);
    energy[0] =     qpbo.ComputeTwiceEnergy(labeling)/2.;
    
    
    
}
void myAllSegments   ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    int numNodes = qpbo.GetNodeNum();
    int *output;
    plhs[0] = mxCreateNumericMatrix(1,numNodes,mxUINT32_CLASS,mxREAL);
    output =(int*) mxGetPr(plhs[0]);
    for(int i = 0;i<numNodes;i++){
        //output[i] = qpbo.what_segment(qpbo.nodes[i]);
        //mexPrintf("Node %d is in %d\n",i,qpbo.what_segment(i));
    }
    
}
void myComputeWeakPersistencies(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    qpbo.ComputeWeakPersistencies();
    
}
void myImprove(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    //init seed
    srand(time(NULL));
    int counter = 0;
    int to = 10;
    while(counter < to){
        qpbo.Improve();
        mexPrintf("improve run %d#%d\n",counter+1,to);
        counter++;
    }
}

void myReset(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    qpbo.Reset();
}


void myDestroy(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    
}
bool probecallback(int unlabeld_num){
    mexPrintf("unlabeld nodes= %d, before %d, count %d\n",unlabeld_num,unlabeldnodes,probecounter);
    if(probecounter > 9){
        probecounter = 0;
        return true;
    }
    //     mexCallMATLAB(NULL,NULL,NULL,NULL,"pause");
    unlabeldnodes = unlabeld_num;
    mexCallMATLAB(NULL,NULL,NULL,NULL,"drawnow");
    probecounter++;
    return false;
}
void myProbe(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
    probecounter = 0;
    unlabeldnodes = 0;
    //     mexPrintf("called probe in adapter\n");
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    //     mexPrintf("got qpbo pointer\n");
    QPBO<double>::ProbeOptions po;
    //     po.callback_fn = &probecallback;
    int nodeNum = qpbo.GetNodeNum();
    int *myMapping = new int[nodeNum];
    for (int i = 0; i < nodeNum; i++){
        myMapping[i] = 2*i;
    }
    
    //       po.directed_constraints=0;
    //      po.weak_persistencies = 0;
    po.dilation = 1;
    //      po.C = 1e20;
    //     po.order_seed=1;
    //     mexPrintf("enter probe\n");
    mexPrintf("numnodes= %d\n",nodeNum);
    mexCallMATLAB(NULL,NULL,NULL,NULL,"drawnow");
    qpbo.Probe(myMapping,po);
    //     mexPrintf("returned from probe\n");
    //for(int i = 0; i< nodeNum;i++){
    //    mexPrintf("Node %d is in %d\n",i,myMapping[i]);
    //}
    
    plhs[0] = mxCreateDoubleMatrix(1,nodeNum,mxREAL);
    double *labels = mxGetPr(plhs[0]);
    for(int i=0; i < nodeNum;i++){
        labels[i] = (myMapping[i]);
    }
    
}

void myGetEnergy       ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    plhs[0] = mxCreateDoubleMatrix(1,1,mxREAL);
    double *energy = mxGetPr(plhs[0]);
    energy[0] = qpbo.ComputeTwiceEnergy()/2.;
}


void myMergeParallelEdges       ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    qpbo.MergeParallelEdges();
    //     mexPrintf("return from merge parallel edges\n");
}



void mySave ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    
    
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    
    qpbo.Save("energy.txt",1);
    
    
}

void myTestLabelings ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    
    
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    double *labeling = mxGetPr(prhs[2]);
    int m = mxGetM(prhs[2]);
    int n = mxGetN(prhs[2]);
    plhs[0] = mxCreateDoubleMatrix(m,1,mxREAL);
    double *energy = mxGetPr(plhs[0]);
    //     mexPrintf("Got labelings with m=%d n=%d\n",m,n);
    for(int i = 0; i < m; i++){
        int lbl[n];
        for(int j = 0; j < n; j++){
            //             mexPrintf("j=%d, i+j*m=%d,label=%d\n",j,i+j*m,static_cast<int>(labeling[j]));
            lbl[j] = static_cast<int>(labeling[i+j*m]);
            //             qpbo.SetLabel(j,static_cast<int>(labeling[i+j*m]));
            //             mexPrintf("%d",lbl[j]);
        }
        //         mexCallMATLAB(NULL,NULL,NULL,NULL,"pause");
        energy[i]=qpbo.ComputeTwiceEnergy(lbl)/2.;
        //         mexPrintf("  energy: %f\n",qpbo.ComputeTwiceEnergy(lbl)/2.);
        //
    }
    
    
    
}
void myLabelingEnergy ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    double *labeling = mxGetPr(prhs[2]);
    int m = mxGetM(prhs[2]);
    int n = mxGetN(prhs[2]);
    //     mexPrintf("Got labelings with m=%d n=%d\n",m,n);
    for(int i = 0; i < m; i++){
        int lbl[n];
        for(int j = 0; j < n; j++){
            lbl[j] = static_cast<int>(labeling[i+j*m]);
            qpbo.SetLabel(j,static_cast<int>(labeling[i+j*m]));
            //             mexPrintf("%d",lbl[j]);
        }
        qpbo.ComputeTwiceEnergy(lbl);
        //         mexPrintf("  energy: %f\n",qpbo.ComputeTwiceEnergy(lbl));
        
    }
    
    
}
void printAddedPairwiseTerm(int node1,int node2, double E00, double E01, double E10, double E11){
    mexPrintf("Added pairwiseterm: (%d,%d) (%f,%f,%f,%f) poly=(%f,%f,%f,%f)\n",node1,node2,E00,E01,E10,E11,E00,E01-E00,E10-E00,E11-(E01-E00)-(E10-E00)-E00);
}
void printAddedUnaryTerm(int node1,double E0, double E1){
    mexPrintf("Added unaryterm: (%d) (%f,%f) poly=(%f,%f)\n",node1,E0,E1,E0,E1-E0);
}
//from ibr_toolbox,Kolmogorov transfromation
void myAddTripleTerm ( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] ){
    QPBO<double>& qpbo = get_object<QPBO<double> >(prhs[1]);
    
    double *theta_pqr = mxGetPr(prhs[2]);
    int m_pqr = mxGetM(prhs[2]);
    int n_pqr = mxGetN(prhs[2]);
    int countIrregular = 0;
//     mexPrintf("Got theta_pqr with m=%d n=%d\n",m_pqr,n_pqr);
    
    for(int column=0;column < n_pqr;column++){

        int node1 = static_cast<int>(theta_pqr[column*11]-1);
        int node2 = static_cast<int>(theta_pqr[column*11+1]-1);
        int	node3 = static_cast<int>(theta_pqr[column*11+2]-1);
        
        double A = theta_pqr[column*11+3]; // E000
        double B = theta_pqr[column*11+4]; // E001
        double C = theta_pqr[column*11+5]; // E010
        double D = theta_pqr[column*11+6]; // E011
        double E = theta_pqr[column*11+7]; // E100
        double F = theta_pqr[column*11+8]; // E101
        double G = theta_pqr[column*11+9]; // E110
        double H = theta_pqr[column*11+10]; // E111
        
        double pi = (A + D + F + G) - (B + C + E + H);
        
        if (pi >= 0) {
            qpbo.AddPairwiseTerm(node1, node2, 0, C-A, 0, G-E);
            //printAddedPairwiseTerm(node1, node2, 0, C-A, 0, G-E);
            if (C-A < G-E)
                countIrregular++;
            qpbo.AddPairwiseTerm(node1, node3, 0, 0, E-A, F-B);
                        //printAddedPairwiseTerm(node1, node3, 0, 0, E-A, F-B);
            if (E-A < F-B)
                countIrregular++;
            qpbo.AddPairwiseTerm(node2, node3, 0, B-A, 0, D-C);
            //printAddedPairwiseTerm(node2, node3, 0, B-A, 0, D-C);
            if (B-A < D-C)
                countIrregular++;
            
            if (pi > 0) {
                // Add node
                int node4 = qpbo.AddNode();
                qpbo.AddUnaryTerm(node4, A, A-pi);
                //printAddedUnaryTerm(node4,A,A-pi);
                qpbo.AddPairwiseTerm(node1, node4, 0, pi, 0, 0);
                //printAddedPairwiseTerm(node1, node4, 0, pi, 0, 0);
                qpbo.AddPairwiseTerm(node2, node4, 0, pi, 0, 0);
                //printAddedPairwiseTerm(node2, node4, 0, pi, 0, 0);
                qpbo.AddPairwiseTerm(node3, node4, 0, pi, 0, 0);
                //printAddedPairwiseTerm(node3, node4, 0, pi, 0, 0);
                
            }
        } else {
            qpbo.AddPairwiseTerm(node1, node2, B-D, 0, F-H, 0);
            //printAddedPairwiseTerm(node1, node2, B-D, 0, F-H, 0);
            if (F-H < B-D)
                countIrregular++;
            qpbo.AddPairwiseTerm(node1, node3, C-G, D-H, 0, 0);
            //printAddedPairwiseTerm(node1, node3, C-G, D-H, 0, 0);
            if (D-H < C-G)
                countIrregular++;
            qpbo.AddPairwiseTerm(node2, node3, E-F, 0, G-H, 0);
            //printAddedPairwiseTerm(node2, node3, E-F, 0, G-H, 0);
            if (G-H < E-F)
                countIrregular++;
            
            // Add node
            int node4 = qpbo.AddNode();
            qpbo.AddUnaryTerm(node4, H+pi, H);
            //printAddedUnaryTerm(node4,H+pi,H);
            qpbo.AddPairwiseTerm(node1, node4, 0, 0, -pi, 0);
            //printAddedPairwiseTerm(node1, node4, 0, 0, -pi, 0);
            qpbo.AddPairwiseTerm(node2, node4, 0, 0, -pi, 0);
            //printAddedPairwiseTerm(node2, node4, 0, 0, -pi, 0);
            qpbo.AddPairwiseTerm(node3, node4, 0, 0, -pi, 0);
            //printmexAddedPairwiseTerm(node3, node4, 0, 0, -pi, 0);
            
        }
    }
    plhs[0] = mxCreateDoubleMatrix(1,1,mxREAL);
    double *nodeNum = mxGetPr(plhs[0]);
    nodeNum[0] = qpbo.GetNodeNum();
//     nodeNum[1] = countIrregular;
}


