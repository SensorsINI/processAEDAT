function uv3  = estimate_rgbd_flow_interface(data, method, varargin) 
%%
%ESTIMATE_RGBD_SCENE_FLOW_INTERFACE  RGBD Scene flow estimation with various methods

% Read in arguments
if nargin < 5
    model = classic_nl_optical_flow_rgbd;    
else
    % Load default parameters
    model = load_of_method(method);
end;

% if exist('params', 'var')
%     model = parse_input_parameter(model, params);    
% end;

% data.im1 = im1;
% data.im2 = im2;
% data.Z   = cat(3, z1, z2);

% Compute flow field
uv3   = compute_flow(model, data);