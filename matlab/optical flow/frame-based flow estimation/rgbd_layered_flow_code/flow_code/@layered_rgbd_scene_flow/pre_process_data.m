function [model, data, uv3] = pre_process_data(model, data)
%%

[H, W, ~] = size(data.im1);

if isfield(data, 'uv3') && ~isempty(data.uv3)
    uv3 = data.uv3;
elseif isfield(data, 'uv') && ~isempty(data.uv)
    uv3 = flow2SceneFlow(data.uv, data.Z(:,:,1), data.Z(:,:,2), model.camParams);    
else
    uv3 = zeros([H,W,3]);
end

if size(data.im1, 3) > 1
    tmp1 = double(rgb2gray(uint8(data.im1)));
    tmp2 = double(rgb2gray(uint8(data.im2)));
    grayImages  = cat(length(size(tmp1))+1, tmp1, tmp2);
else    
    grayImages  = cat(length(size(data.im1))+1, double(data.im1), double(data.im2));
end;

images = double(cat(length(size(data.im1))+1, data.im1, data.im2));

% color space 
if size(images,4) > 1
    grayImages = [];
    labImages = [];
    for i = 1:size(images,4)
        grayImages = cat(3, grayImages, double(rgb2gray(uint8(images(:,:,:,i)))) );        
        im1 = RGB2Lab(images(:,:,:,i));
        for j = 1:size(im1, 3);
            im1(:,:,j) = scale_image(im1(:,:,j), 0, 255);
        end;
        labImages = cat(length(size(im1))+1, labImages, im1);
    end;    
%     labImages = double(labImages(:,:,:,1));
else
    grayImages = double(images);
    labImages  = double(images);
%     labImages  = labImages(:,:,1);
end;


% Preprocess input (gray) sequences
if model.texture
    % Perform ROF structure texture decomposition
    images  = structure_texture_decomposition_rof(grayImages, 1/8, 100, model.alp);
else
    images  = scale_image(images, 0, 255);
end;

data.images = images;
data.labImages = labImages;
data.grayImages = grayImages;
% data.labImage1 = labImage1;

if model.auto_level
    % Automatic determine pyramid level for first GNC stage
    model.pyramid_levels{1}  =  1 + floor( log(min(size(images, 1),...
        size(images,2))/16) / log(model.pyramid_spacing) );
end;