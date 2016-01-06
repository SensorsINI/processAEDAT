function demo_RGBD_tracking_data
%%

paths.code = cd; 
paths.data = fullfile('data', 'tracking');
paths.result = 'result';

addpath(genpath(paths.code));

model = layered_rgbd_scene_flow;
model = load_layered_rgbd_parameters(model);
model = load_tracking_data_parameters(model);
%%
seqName = 'bear_back'; 
frame = 1; 
fprintf('%s \n', seqName);

resultDir = fullfile(paths.result, seqName, sprintf('frame%03d', frame));

factor  = 1; 
[im1, im2, d1, d2, d1In, d2In, valid, camParams] =...
    read_tracking_data(seqName, factor, frame, paths.data);
%%
data.im1 = im1;
data.im2 = im2;
data.validZ = valid;
%%% RGBD tracking data
contZ = 100/8;
data.Z   = cat(3, d1In, d2In)/contZ;
[uvc, uvbc, images, colorImages] = compute_load_cnl_flow_result(...
    resultDir, im1, im2, frame);

[H,W,~] = size(im1);
model.camParams = camParams;
model.color_images = cat(length(size(im1))+1, im1, im2);

nOutIters = 3;
for K=5
    fprintf('%d layers\t', K);
    
    fn = fullfile(resultDir, sprintf('Kmeans%d.mat', K));
    if exist(fn, 'file')
        load(fn);
    else
        [seg, seg2] = compute_cluster_from_depth(data, K, uvc, uvbc);
        save(fn, 'seg', 'seg2');
    end;
    
    [layer_uv, layer_uvb, layer_g] = compute_init_layer_support_flow(...
        seg, seg2, uvc, uvbc, model, data, resultDir);
    
    tic;
    for iter = 1:nOutIters        
        layer_g = update_support_given_motion(model, ...
            layer_uv, layer_uvb, images, colorImages, layer_g);
        [layer_uv, layer_uvb] = update_motion_given_support(model,...
            layer_g, data, images, layer_uv, layer_uvb);        
    end;
    fprintf('%d %3.3f minutes passed\n', K, toc/60);
    
    uvw = zeros(H,W,3);
    seg1 = g2seg(layer_g{1});
    seg2 = g2seg(layer_g{2});
    idx3 = repmat(seg1, [1 1 3]);
    for k=1:length(layer_uv{1});
        uvw(idx3==k) = layer_uv{1}{k}(idx3==k);
    end
   
    methodInfo = sprintf('%dlayers_', K);
    save_results(resultDir, uvw, seg1, seg2, im1, im2, methodInfo);
end;