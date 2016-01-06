% %%
% clear;
% T = 4;
% nL = 4;
% sz = [10 10];
% 
% params.sigma_i = 7;
% params.Ti2     = 20^2;
% params.g_filters   = {[1 -1], [1; -1]};  
% params.kappa = 0.5;
% params.lambda2 = 1;
% params.lambda3 = 1;  
% params.lambda4 = 1;
% 
% g12  = randn([sz  nL-1 T]);
% g12 = g12(:);
% for t=1:T; colorImages{t} = randn([sz 3]);end;
% % for t=1:T; colorImages{t} = randn([sz]);end;
% for t=1:T-1;
%     for i = 1:nL; layer_uvb{t}{i} = randn([sz 2]); end;
%     for i = 1:nL; layer_uv{t}{i} = randn([sz 2]); end;
%     aIt2{t} = rand([sz nL])*10;
%     aIt2_b{t} = rand([sz nL])*10;
% end;
% 
% 
% %
% 
% d = checkgrad('compute_hidden_field_3D_energy', g12, 1e-3, aIt2, colorImages, aIt2_b, layer_uvb, layer_uv, params)


%%function [e d12] = compute_flow_hidden_field_3D_energy(g12, images, colorImages,  layer_uvb_affine, layer_uv_affine, this)

% Data + smoothness prior + temporal consistency term

% for 2 frames symmetric case, solve g g2 together
% $ Date: 2010-7-26$

%%
clear
T = 2;
nL = 4;
sz = [10 10];

params.sigma_i = 7;
params.Ti2     = 20^2;
params.g_filters   = {[1 -1], [1; -1]};  
params.spatial_filters  = {[1 -1], [1; -1]};  
params.kappa = 0.5;
params.lambda = 1;
params.lambda2 = 1;
params.lambda3 = 1;  
params.lambda4 = 1;
params.lambda5 = 1;
params.nLayers = nL;
params.interpolation_method = 'bi-cubic';  % 'bi-cubic', 'cubic', 'bi-linear'
params.deriv_filter         = [1 -8 0 8 -1]/12;

method = 'quadratic'; %'charbonnier'; %'quadratic'; %'geman_mcclure'; %
a = 1;
for i = 1:length(params.spatial_filters);
    params.rho_spatial_u{i}   = robust_function(method, a); % 0.1
    params.rho_spatial_v{i}   = robust_function(method, a);
end;
params.rho_data        = robust_function(method, a); % 6.3

g  = randn([sz  nL-1 T]);
uv = randn([sz 2 nL T-1]);
uvb= randn([sz 2 nL T-1]);
g12 = [g(:); uv(:); uvb(:)];
% for t=1:T; colorImages{t} = randn([sz 3]);end;
for t=1:T; colorImages{t} = randn([sz]); images(:,:,t) = randn([sz]);end;
for t=1:T-1;
    for i = 1:nL; layer_uvb{t}{i} = randn([sz 2]); end;
    for i = 1:nL; layer_uv{t}{i} = randn([sz 2]); end;
    for i = 1:nL; layer_uvb_affine{t}{i} = randn([sz 2]); end;
    for i = 1:nL; layer_uv_affine{t}{i} = randn([sz 2]); end;
end;

%%
d = checkgrad('compute_flow_hidden_field_3D_energy', g12, 1e-3, images, colorImages,  layer_uvb_affine, layer_uv_affine, params)
