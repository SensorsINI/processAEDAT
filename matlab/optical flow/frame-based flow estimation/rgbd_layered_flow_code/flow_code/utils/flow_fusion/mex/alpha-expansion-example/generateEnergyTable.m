%% Generate EnergyTable for pairwise mrfs
% IN: 
%   cliques         -   nx2 matrix of node indices
%   potential_func  -   @function_handle,
%   fp_0,fp_1       -   current labeling and proposal

function [pairwise_terms] = generateEnergyTable(cliques,potential_func,fp_0,fp_1)
mytruthtable=[0 0;0 1;1 0;1 1];
inputV = generatePotentialVectors(fp_0,fp_1,mytruthtable',cliques);
pairwise = reshape(potential_func(inputV),4,[]);
pairwise_terms = [cliques' ; pairwise];

