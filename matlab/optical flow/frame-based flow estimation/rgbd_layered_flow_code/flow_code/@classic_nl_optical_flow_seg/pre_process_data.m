function [this data] = pre_process_data(this)
%%
% texture decomposition
% build up pyramid of imgaes, segemntation, flow etc. 

% Preprocess input (gray) sequences
if this.texture
    images  = structure_texture_decomposition_rof( this.images,...
        1/8, 100, this.alp);
elseif this.fc
    % Laplacian in flowfusion
    f = fspecial('gaussian', [5 5], 1.5); % std = 1 is better
    images  = this.images- this.alp*imfilter(this.images, f, 'symmetric');
    images  = scale_image(images, 0, 255);
else
    images  = scale_image(this.images, 0, 255);
end;

sz = size(images);
sz = sz(1:2);

if this.auto_level % Automatic determine pyramid levels
    % largest size around 16
    N1 = 1 + floor( log(max(size(images, 1), size(images,2))/16)/...
        log(this.pyramid_spacing) );
    % smaller size shouldn't be less than 6
    N2 = 1 + floor( log(min(size(images, 1), size(images,2))/6)/...
        log(this.pyramid_spacing) );
    this.pyramid_levels  =  min(N1, N2);
    
    if this.old_auto_level
        this.pyramid_levels  =  1 + floor( log(min(size(images, 1),...
            size(images,2))/16) / log(this.pyramid_spacing) );
    end;
    
    if this.unEqualSampling
        this.pyramid_levels  =  1 + floor( log(max(sz)/16)...
            / log(this.pyramid_spacing) );
        
        tmp = exp(log(min(sz)/max(sz)*this.pyramid_spacing^(this.pyramid_levels-1))...
            /(this.pyramid_levels-1) );
        if sz(1) > sz(2)
            spacing = [this.pyramid_spacing tmp];
        else
            spacing = [tmp this.pyramid_spacing];
        end
        
    end            
    
    if this.display
        fprintf('%d-level pyramid used\n', this.pyramid_levels);
    end;
end;

factor            = sqrt(2);

if this.unEqualSampling
%     fprintf('unequal sampling\n');
    data.pyramid_images    = compute_image_pyramid_unequal(images, ...
        this.pyramid_levels, spacing, factor);
    
    % For segmentation purpose
    data.org_pyramid_images = compute_image_pyramid_unequal(this.images,...
        this.pyramid_levels, spacing, factor, data.pyramid_images);
    data.org_color_pyramid_images = compute_image_pyramid_unequal(...
        this.color_images, this.pyramid_levels, spacing, factor, ...
        data.pyramid_images);
else
    
    % Construct image pyramid, using filter setting in Bruhn et al in
    % "Lucas/Kanade.." (IJCV2005') page 218
    % For gnc stage 1

    smooth_sigma      = sqrt(this.pyramid_spacing)/factor;
    f                 = fspecial('gaussian',...
        2*round(1.5*smooth_sigma) +1, smooth_sigma);
    data.pyramid_images    = compute_image_pyramid(images, f,...
        this.pyramid_levels, 1/this.pyramid_spacing);
    
    % For segmentation purpose
    data.org_pyramid_images = compute_image_pyramid(this.images, f,...
        this.pyramid_levels, 1/this.pyramid_spacing, data.pyramid_images);
    data.org_color_pyramid_images = compute_image_pyramid(this.color_images,...
        f, this.pyramid_levels, 1/this.pyramid_spacing, data.pyramid_images);

end
% For gnc stage 2 to gnc_iters
smooth_sigma      = sqrt(this.gnc_pyramid_spacing)/factor;
f                 = fspecial('gaussian',...
    2*round(1.5*smooth_sigma) +1, smooth_sigma);
data.gnc_pyramid_images= compute_image_pyramid(images,...
    f, this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing);

% For segmentation/weighted median filtering
data.org_gnc_pyramid_images = compute_image_pyramid(this.images,...
    f, this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing, ...
    data.gnc_pyramid_images);
data.org_color_gnc_pyramid_images = compute_image_pyramid(this.color_images,...
    f, this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing, ...
    data.gnc_pyramid_images);

%%%%% GT flow fields
if ~isempty(this.tuv)
    tuv = this.tuv;
else
    tuv = zeros([sz 2]);
end;

% no scaling for consistent edge detection threshold at different levels
data.pyramid_tuv    = compute_flow_pyramid(tuv,...
    this.pyramid_levels, 1/this.pyramid_spacing, 'bicubic', data.pyramid_images);
data.gnc_pyramid_tuv    = compute_flow_pyramid(tuv,...
    this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing, 'bicubic', ...
    data.gnc_pyramid_images);

%%%%% GT flow fields
if ~isempty(this.tocc)
    tocc = this.tocc;
else
    tocc = zeros([sz 2]);
end;

data.pyramid_tocc    = compute_segmentation_pyramid(tocc,...
    this.pyramid_levels, 1/this.pyramid_spacing, [], data.pyramid_images);
data.gnc_pyramid_tocc    = compute_segmentation_pyramid(tocc,...
    this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing, [], ...
    data.gnc_pyramid_images);

%%%%% SLIC segmentation

regionSize = 80 ;
regularizer = .1 ;
seg = vl_slic(single(this.color_images), regionSize, regularizer) ;
data.pyramid_seg    = compute_segmentation_pyramid(seg,...
    this.pyramid_levels, 1/this.pyramid_spacing, [], data.pyramid_images);

if length(data.pyramid_seg) > 4
    % disable the top 3 levels
    for l=length(data.pyramid_seg):-1:length(data.pyramid_seg)-2
        data.pyramid_seg{l} = zeros(size(data.pyramid_seg{l}));
    end
end
data.gnc_pyramid_seg = compute_segmentation_pyramid(seg,...
    this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing, [], ...
    data.gnc_pyramid_images);

