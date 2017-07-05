function uvo = estimate_flow_interface(im1, im2, method, outFn, params) 
%%
%ESTIMATE_FLOW_INTERFACE  Optical flow estimation with various methods
%
% Demo program
%     [im1, im2, tu, tv] = read_flow_file('middle-other', 4);
%     uv = estimate_flow_interface(im1, im2, 'classic+nl-fast');
%     [aae stdae aepe] = flowAngErr(tu, tv, uv2(:,:,1), uv2(:,:,2), 0)
%
% For arbitrary two input images
%     im1 = imread('data/other-data/RubberWhale/frame10.png');
%     im2 = imread('data/other-data/RubberWhale/frame11.png');
%     uv = estimate_flow_interface(im1, im2, 'classic+nl-fast');

% if first two inputs are filenames
if ischar(im1)
    im1 = imread(im1);    
end;
if ischar(im2)
    im2 = imread(im2);
end;

% Read in arguments
if nargin < 3
    method = 'classic+nl-fast';
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
uv  = compute_flow(ope, zeros([size(im1,1) size(im1,2) 2]));

if nargout == 1
    uvo = uv;
end;

% save flow field if required
if exist('outFn', 'var') && ~isempty(outFn)
    % for testing energy change vs # warping steps
    writeFlowFile(uv, outFn);    
%     outFn = [outFn(1:end-4) sprintf('_iter%05d.flo', ope.max_iters)];    
%     writeFlowFile(uv, outFn);
    outFn(end-2:end) = 'png';
    imwrite(uint8(flowToColor(uv)), outFn);
end;
