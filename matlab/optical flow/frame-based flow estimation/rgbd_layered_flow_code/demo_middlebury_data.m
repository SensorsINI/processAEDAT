%%

paths.code = cd;
paths.data = fullfile('data', 'middleburry');
paths.result = 'result';

addpath(genpath(paths.code));

model = layered_rgbd_scene_flow;
model = load_layered_rgbd_parameters(model);
model = load_middlebury_parameters(model);
%%
iSeq = 2; 
seqNames = {'teddy', 'cones', 'Art', 'Books', 'Dolls',  'Laundry', 'Moebius', 'Reindeer'};
seqName = seqNames{iSeq};
fprintf('%s \n', seqName);
resultDir = fullfile(paths.result, seqName);
touchDir(resultDir)

factor  = 1; 
[im1, im2, d1, d2, tuv1, tuv2, d1In, d2In, data.validZ] =...
    read_MD_stereo_data(seqName, factor, paths.data);
data.im1 = im1;
data.im2 = im2;
data.tuv = tuv1;
data.Z   = 60./cat(3, d1In, d2In); 

%% % 2D cnl & pre_processed images
frame = 1; nLevels = 6;
[uvc, uvbc, images, colorImages] = ...
    compute_load_cnl_flow_result(resultDir, im1, im2, frame, nLevels);
fprintf('Classic+NLP\n');
evaluate_flow_error(uvc, tuv1);
%%
[H,W,~] = size(im1);
model.color_images = cat(length(size(im1))+1, im1, im2);
nOutIters = 3;
for K= 2
    fprintf('layer number %d\t', K);
    
    fn = fullfile(resultDir, sprintf('Kmeans%d.mat', K));
    if exist(fn, 'file')
        load(fn);
    else
        [seg, seg2] = compute_cluster_from_depth(data, K, uvc, uvbc);
        save(fn, 'seg', 'seg2');
    end;
    
    [layer_uv, layer_uvb, layer_g] = compute_init_layer_support_flow(...
        seg, seg2, uvc, uvbc, model, data, resultDir);
    
    methodInfo = sprintf('%dlayers_init_', K);
    save_results(resultDir, uvc, seg, seg2, im1, im2, methodInfo);    
    
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
    evaluate_flow_error(uvw, tuv1);
    
    methodInfo = sprintf('%dlayers_', K);
    save_results(resultDir, uvw, seg1, seg2, im1, im2, methodInfo);
end;