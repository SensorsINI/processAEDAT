function model = classic_nl_optical_flow_rgbd(varargin)
%%
error(nargchk(0, 1, length(varargin)));
  
  switch (length(varargin))
    case 0
        
      model.images          = [];              
      model.lambda          = 3;
      model.lambda_q        = 3;    % Quadratic formulation of the objective function
      model.lambda2         = 1e-1;      % weight for coupling term
      model.lambda3         = 1;         % weight for non local term term

      
      model.sor_max_iters   = 1e4;       % 100 seems sufficient

      model.limit_update    = true;      % limit the flow incrment to be less than 1 per linearization step
      model.display         = false;            
      
      model.solver          = 'backslash';   % 'sor' 'pcg' for machines with limited moemory       
      model.deriv_filter    = [1 -8 0 8 -1]/12; % 5-point 7 point [-1 9 -45 0 45 -9 1]/60; 
      
      model.texture         = true;     % use texture component as input
      model.fc              = false;     % use filter constancy

      model.median_filter_size   = [5 5]; %[5 5];
      model.interpolation_method = 'bi-cubic';      %'cubic', 'bi-linear
      
      % For Graduated Non-Convexity (GNC) optimization
      model.gnc_iters       = 3;
      model.alpha           = 1;             % change linearly from 1 to 0 through the GNC stages

      model.max_iters       = 10;            % number of warping per pyramid level
      model.max_linear      = 1;             % maximum number of linearization performed per warping, 1 OK for HS
      
      % For GNC stage 1
      model.pyramid_levels  = {4, 2, 2};           
      model.pyramid_spacing = 2;

      % For GNC stage 2 to last
      model.gnc_pyramid_levels     = 2;
      model.gnc_pyramid_spacing    = 1.25;                      
      
      method = 'generalized_charbonnier'; %'lorentzian'
      model.spatial_filters = {[1 -1], [1; -1]};
      a   = 0.45;
      sig = 1e-3;
      for i = 1:length(model.spatial_filters);
          model.rho_spatial_u{i}   = robust_function(method, sig, a);
          model.rho_spatial_v{i}   = robust_function(method, sig, a);
          model.rho_spatial_w{i}   = robust_function(method, sig, a);
      end;
      model.rho_data        = robust_function(method, sig, a);
      model.rho_data_depth  = robust_function(method, sig, a);
      
      model.seg             = [];    % store segementation result
      model.mfT             = 15;    % threshold for intensity-median-filter
      model.imfsz           = [7 7]; % for intensity-median-filter
      model.filter_weight   = [];    % only for the new obj. charbonnier
      model.alp             = 0.95;  % for rof texture decomposition
    
      model.hybrid          = false;  
      model.area_hsz        = 7;    % half window size for the weighted median filter
      model.affine_hsz      = 4;     % half window size for robust affine 
      model.sigma_i         = 7;
      model.sigma_d  = 7;
      model.color_images     = [];
      model.auto_level       = true;
      model.input_seg        = [];
      model.input_occ        = [];
      model.warpingIncrement = 0;
      
      model.fullVersion      = false;

      model.camParams.cx     = 0;
      model.camParams.cy     = 0;
      model.camParams.fx     = 1;
      model.camParams.fy     = 1;
      
      model.lambdas.depth    = 1;
      model.depths           = [];
      model.reppresentation  = 'uvw';
      model.blend   = 0.5;  % 1 for checking gradient      
      model.lambdas.isWzero     = false;
      model.lambdas.isMrfOnDev  = true;
      model = class(model, 'classic_nl_optical_flow_rgbd');         
      
    case 1
      if isa(varargin{1}, 'classic_nl_optical_flow_rgbd')
        model = varargin{1};        
      else    
          model = classic_nl_optical_flow_rgbd;
          model.images = varargin{1};  
      end
      
    otherwise
      error('Incompatible arguments!');
      
  end