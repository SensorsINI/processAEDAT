function uv3 = compute_flow(model, data, varargin)
%%

[model, data, uv3] = pre_process_data(model, data);
data = build_image_pyramid(model, data);

% initialize segmentation, interpolate flow field for each layer


for ignc = 1:model.gnc_iters
    for l = model.pyramid_levels{ignc}:-1:1

        small = model;                
        % scale camera parameters
        spacing = model.gnc_pyramid_spacing * (ignc>1) + ...
            model.pyramid_spacing * (ignc==1);

        if ignc == 1
            small.max_linear  = 1;           
            [H,W,~] = size(data.pyramid_images{l});
            small.images        = data.pyramid_images{l};
            small.depths        = data.pyramid_depths{l};
            small.color_images  = data.org_color_pyramid_images{l};                 
        else
            [H,W,~] = size(data.gnc_pyramid_images{l});
            small.images        = data.gnc_pyramid_images{l};            
            small.depths        = data.gnc_pyramid_depths{l};     
            small.color_images  = data.org_color_gnc_pyramid_images{l};            
        end;        
        
        uv3 = resample_flow3(uv3, [H,W]);     

        % estimate per-layer scene flow 
        
        if (max(H,W) > 100) && model.lambdas.isOcc       
            data.occ = detect_occlusion(small, uv3, data);
        else
            data.occ = ones(H,W);
        end
        
        if strcmpi(model.reppresentation, 'uvw')
            uv = uv3(:,:,1:2);
        else
            uv = sceneFlow2Flow(uv3, small.depths(:,:,1), small.camParams);
        end
        data.validZ1 = imresize(data.validZ(:,:,1), [H, W], 'nearest');
        validZ2 = imresize(data.validZ(:,:,2), [H, W], 'nearest');
        data.validZW = warp_backward_segmentation(double(validZ2), uv);
            

        data.uv3r = fit_3d_rigid_motion(model, small.depths, uv3, data.occ==0 | data.validZ1==0);
        
        uv3 = compute_flow_base(small, data, uv3);
        
        % refinne layer support
        data.support = estimate_layer_support(model, layer_uv3s, data);

    end  
    
    % Update GNC parameters (linearly)
    if model.gnc_iters > 1
        new_alpha  = 1 - ignc / (model.gnc_iters-1);
        model.alpha = min(model.alpha, new_alpha);
        model.alpha = max(0, model.alpha);
    end;           
end;
