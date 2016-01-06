function uv3 = compute_flow(model, data, varargin)
%%

[model, data, uv3] = pre_process_data(model, data);
data = build_image_pyramid(model, data);

for ignc = 1:model.gnc_iters
    % Iterate through all pyramid levels starting at the top
    for l = model.pyramid_levels{ignc}:-1:1
        % Generate copy of algorithm with single pyramid level 
        small = model;        
%         fprintf('%d %d,', ignc, l);
        
        % scale camera parameters
        spacing = model.gnc_pyramid_spacing * (ignc>1) + ...
            model.pyramid_spacing * (ignc==1);
%         small.camParams.cx     = model.camParams.cx/spacing^(l-1);
%         small.camParams.cy     = model.camParams.cy/spacing^(l-1);
%         small.camParams.fx     = model.camParams.fx/spacing^(l-1);
%         small.camParams.fy     = model.camParams.fy/spacing^(l-1);

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
                
        
        if (max(H,W) > 100) && model.lambdas.isOcc       
            data.occ = detect_occlusion(small, uv3, data);
        else
            data.occ = ones(H,W);
%             data.validZ1 = ones(H,W);
%             data.validZW = ones(H,W);
        end
        
        if strcmpi(model.reppresentation, 'uvw')
            uv = uv3(:,:,1:2);
        else
            uv = sceneFlow2Flow(uv3, small.depths(:,:,1), small.camParams);
        end
        data.validZ1 = imresize(data.validZ(:,:,1), [H, W], 'nearest');
        validZ2 = imresize(data.validZ(:,:,2), [H, W], 'nearest');
        data.validZW = warp_backward_segmentation(double(validZ2), uv);
            
        %if model.lambdas.isMrfOnDev  
        data.uv3r = fit_3d_rigid_motion(model, small.depths, uv3, data.occ==0 | data.validZ1==0);
        %end
        
%         if ignc== model.gnc_iters && l ==1
%             model.median_filter_size = [];
%         end
        
        %uv3 = data.uv3r;
if isfield(data, 'tuv')        
fprintf('%d %d \n', ignc, l);
evaluate_flow_error(data.uv3r, data.tuv, false);
end
        uv3 = compute_flow_base(small, data, uv3);
        
% figure; imagesc(flowToColor(uv3(:,:,1:2)));
    end  
    
    % Update GNC parameters (linearly)
    if model.gnc_iters > 1
        new_alpha  = 1 - ignc / (model.gnc_iters-1);
        model.alpha = min(model.alpha, new_alpha);
        model.alpha = max(0, model.alpha);
    end;           
end;
