function demo_ECCV2014_data
%%

paths.code = cd; 
paths.data = fullfile('data', 'ECCV2014');
paths.result = 'result';

addpath(genpath(paths.code));

model = layered_rgbd_scene_flow;
model = load_layered_rgbd_parameters(model);
model = load_tracking_eccv2014_parameters(model);

%%
seqNum = 20;
factor  = 1; 
[im1, im2, d1, d2, d1In, d2In, valid, camParams] =...
    read_eccv2014_data(seqNum, factor,paths.data);

resultDir = fullfile(paths.result, sprintf('eccv2014_%04d', seqNum));
touchDir(resultDir)

data.im1 = im1;
data.im2 = im2;
data.validZ = valid;
%%% ECCV 2014 data
data.Z   = cat(3, d1In, d2In);

[uvc, uvbc, images, colorImages] = compute_load_cnl_flow_result(resultDir, im1, im2);

[H,W,~] = size(im1);
model.camParams = camParams;
model.color_images = cat(length(size(im1))+1, im1, im2);

nOutIters = 3;
for K= 4
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
    seg = g2seg(layer_g{1});
    seg2 = g2seg(layer_g{2});
    idx3 = repmat(seg, [1 1 3]);
    for k=1:length(layer_uv{1});
        uvw(idx3==k) = layer_uv{1}{k}(idx3==k);
    end
   
    methodInfo = sprintf('%dlayers_', K);
    save_results(resultDir, uvw, seg, seg2, im1, im2, methodInfo);
end;