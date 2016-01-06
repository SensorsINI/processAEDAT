function uv  = fuse_flow(this, uv)
%%

im1 = (this.images(:,:,1));
im2 = (this.images(:,:,2));

% if size(this.orgImages,4) == 1
%     im1 = single(this.orgImages(:,:,1));
%     im2 = single(this.orgImages(:,:,2));
% else
%     im1 = single(rgb2gray(uint8(this.orgImages(:,:,:,1))));
%     im2 = single(rgb2gray(uint8(this.orgImages(:,:,:,2))));
% end

%%% generate proposal from sift feature matching
can_uv = compute_sift_candidate(this.orgImages, uv);

if isempty(can_uv)
    return;
end

%%% fuse flow

% close all;
params.lambdaAff = 1e-4;
params.lambdaFlow = 3;
params.lambdaIncon = 3;
params.rho_data = robust_function('generalized_charbonnier', 1e-3, 0.45);
params.rho_spatial = robust_function('generalized_charbonnier', 1e-3, 0.45);
params.useAaffine = false;
params.T2_lab = 1600;
params.sigma_lab = 10;
params.lambdaOcc = 9;


% figure; imshow(flowToColor(uvfuse));
[H W ~] = size(im1);
QPBO_all_in_one_prealloc('a',H*W);

%%
for i=1:size(can_uv,4);
    uv = fuse_flow_binary_edge_occ(im1, im2, this.flowEdges, this.occ,...
        uv, can_uv(:,:,:,i),params);
end;
%%
QPBO_all_in_one_prealloc('d');