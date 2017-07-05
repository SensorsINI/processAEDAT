function occ_map = reason_occlusion_gc(uv, uv2, T)

% Detect (dis)occlusion regions in image 1 by cross checking (unary) and
% smoothness (pairwise)

lambda = 1;

if nargin < 3
    T = 1;
end;

method = 'cubic';

H   = size(uv, 1);
W   = size(uv, 2);

occ_map = ones(H, W);

[x,y]   = meshgrid(1:W,1:H);
x2      = x + uv(:,:,1);        
y2      = y + uv(:,:,2);  

% out-of-boundary pixels
B = (x2>W) | (x2<1) | (y2>H) | (y2<1);
occ_map(B) = 0;
x2(B) = x(B);
y2(B) = y(B);

inv_u = interp2(x,y,uv2(:,:,1),x2,y2,method);
inv_v = interp2(x,y,uv2(:,:,2),x2,y2,method);

% dif   = abs((uv(:,:,1)+inv_u)  + abs(uv(:,:,2)+inv_v).^2);
% dif   = ((uv(:,:,1)+inv_u).^2  + (uv(:,:,2)+inv_v).^2).^2; % bug
dif   = ((uv(:,:,1)+inv_u).^2  + (uv(:,:,2)+inv_v).^2);

% O = sqrt((uv(:,:,1)+inv_u).^2 + (uv(:,:,2)+inv_v).^2) >=T;

% graph cut

% Ising model
pTable = [0 1; 1 0];
prior_func = @(u) pairwise_potential_table(u, pTable);

nL = 2;

m = H;
n = W;

vert = im2col((reshape(1:m*n,m,n)),[2 1])';%vertical
hor  = im2col((reshape(1:m*n,m,n)),[1 2])';%horizontal

current_proposal = repmat(1,m,n);
fp = repmat(2,m,n);

%in case of pairwise mrfs, we do not split the potentials to unary
%and pairwise terms, we simply use the energytable
%[E00,E01,E10,E11], which can be represented by single pairwise
%term

% 0 alpha (occluded)
% 1 fp    (visible)

pt1 = layer_generateEnergyTable(vert, prior_func, current_proposal, fp);
pt2 = layer_generateEnergyTable(hor,  prior_func, current_proposal, fp);

pairwise_terms  = [pt1 pt2];
pairwise_terms(3:end,:) = lambda*pairwise_terms(3:end,:);

%Seteup dataterm, these are only unary terms
Dp_alpha    = repmat(T, m,n); % all pixels are occluded
Dp_fp       = dif;      % all pixels are visible

%Arrange dataterm to a 3xn matrix
data_unary = [(1:m*n)' Dp_alpha(:) Dp_fp(:)]';

[new_fp,new_energy] = QPBO_all_in_one(m*n, data_unary, pairwise_terms);
% [min(new_fp(:)), max(new_fp(:))]  %for debug
occ_map = new_fp == 1;
occ_map = reshape(occ_map, m,n);
occ_map(B) = 0;

%% Generate EnergyTable for pairwise mrfs
% IN: 
%   cliques         -   nx2 matrix of node indices
%   potential_func  -   @function_handle,
%   fp_0,fp_1       -   current labeling and proposal
function [pairwise_terms] = layer_generateEnergyTable(cliques,potential_func,fp_0,fp_1)
mytruthtable=[0 0;0 1;1 0;1 1];
inputV = generatePotentialVectors(fp_0,fp_1,mytruthtable',cliques);
tmp = ones(size(inputV));
tmp(1:4:end, :) = cliques;
tmp(2:4:end, :) = cliques;
tmp(3:4:end, :) = cliques;
tmp(4:4:end, :) = cliques;
pairwise = reshape(potential_func([tmp';inputV']),4,[]);
pairwise_terms = [cliques' ; pairwise];

%%
function out = pairwise_potential_table(vals, pTable)

% Compute the pairwise term for layer segmentaion

% This is a private member function of the class 'layer_optical_flow'.
% 
% Author: Deqing Sun, Department of Computer Science, Brown University
% Contact: dqsun@cs.brown.edu

% no difference between horizontal and vertical cliques
% the potential is symmetric

psz  = size(pTable);
indx = int8((vals(3,:)-1)*psz(1)+vals(4,:));
out  = pTable(indx);