function [uv fp] = fuse_flow_binary_edge_occ(im1, im2, flowEdge, occ, uv1, uv2,params)
                
%%
% given layer segmentation, select flow field for each layer between the
% current continuous flow field and its affine mean flow field
% temporal consistency of layer support, deviation from affine flow fields

sz = size(im1);
H  = sz(1);
W  = sz(2);
images=cat(length(sz)+1, im1, im2);

lambdaForb = 1e3;
minWeight = 1e-4;

invalid = isnan(uv1);
uv1(invalid) = 0;
[It1 tmp1 tmp1 B1] = partial_deriv(images,uv1);
It1(B1) = params.lambdaOcc;
It1(invalid(:,:,1)) = lambdaForb;

invalid = isnan(uv2);
uv2(invalid) = 0;
[It2 tmp1 tmp1 B2] = partial_deriv(images,uv2);
It2(B2) = params.lambdaOcc;
It2(invalid(:,:,1)) = lambdaForb;

cost1 = evaluate(params.rho_data, It1);
cost2 = evaluate(params.rho_data, It2);
cost1 = mean(cost1, 3);
cost2 = mean(cost2, 3);
cost1(occ==1) = params.lambdaOcc;
cost2(occ==1) = params.lambdaOcc;

% spatial term
vert = im2col((reshape(1:H*W,H,W)),[2 1])';
hor  = im2col((reshape(1:H*W,H,W)),[1 2])';

can_uv = cat(4, uv1, uv2);
spatial_func = @(u) compute_pw_spatial_flow_potential(u,...
    can_uv, params);

fp      = ones(H*W,1);

wv = 1-flowEdge(1:end-1,:)+minWeight;
wh = 1-flowEdge(:,1:end-1)+minWeight;
weight = repmat([wv(:)' wh(:)'], [4 1]);

iState = 0;

current_proposal = iState *ones(size(fp));


pairwise_terms   = generateEnergyTable_matlab([vert; hor],...
    spatial_func, current_proposal(1:H*W), fp(1:H*W));

% modulated by color difference
pairwise_terms(3:6,:) = pairwise_terms(3:6,:).*weight;

% singleton data term: mathcing cost
ind = (1:H*W)';

data_unary = [ind'; cost1(:)'; cost2(:)'];

[new_fp,new_energy] = QPBO_all_in_one_prealloc('p', H*W,...
    data_unary, pairwise_terms);

%generate new labeling if it has lower energy
fp = (1-new_fp).* current_proposal+ new_fp .* fp;

% parse collapsed states to individual variables
fp = reshape(fp, [H W]);
uv = composite_final_flow_seg(can_uv, fp+1);
