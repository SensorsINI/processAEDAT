function uvo  = estimate_rgbd_scene_flow_interface(im1, im2, d1, d2, method, params) 
%%
%ESTIMATE_RGBD_SCENE_FLOW_INTERFACE  RGBD Scene flow estimation with various methods

% if first two inputs are filenames
if ischar(im1)
    im1 = imread(im1);    
end;
if ischar(im2)
    im2 = imread(im2);
end;

% Read in arguments
if nargin < 5
    method = 'classic+nl-rgbd-fast';
end;

if (~isdeployed)
    addpath(genpath('utils'));
end

% Load default parameters
ope = load_of_method(method);

if exist('params', 'var')
    ope = parse_input_parameter(ope, params);    
end;

% Uncomment this line if Error using ==> \  Out of memory. Type HELP MEMORY for your option.
%ope.solver    = 'pcg';  

% ope.images  = cat(length(size(tmp1))+1, tmp1, tmp2);

if size(im1, 3) > 1
    tmp1 = double(rgb2gray(uint8(im1)));
    tmp2 = double(rgb2gray(uint8(im2)));
    ope.images  = cat(length(size(tmp1))+1, tmp1, tmp2);
else
    
    if isinteger(im1);
        im1 = double(im1);
        im2 = double(im2);
    end;
    ope.images  = cat(length(size(im1))+1, im1, im2);
end;
ope.depths = cat(3, d1, d2);

% Use color for weighted non-local term
if ~isempty(ope.color_images)    
    if size(im1, 3) > 1        
        % Convert to Lab space       
        im1 = RGB2Lab(im1);          
        for j = 1:size(im1, 3);
            im1(:,:,j) = scale_image(im1(:,:,j), 0, 255);
        end;        
    end;    
    ope.color_images   = im1;
end;

% Compute flow field
uvo   = compute_flow(ope, zeros([size(im1,1) size(im1,2) 2]));