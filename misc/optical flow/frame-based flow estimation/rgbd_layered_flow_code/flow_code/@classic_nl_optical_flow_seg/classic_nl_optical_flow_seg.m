function this = classic_nl_optical_flow_seg(varargin)
%%
  
     

error(nargchk(0, 1, length(varargin)));
  
  switch (length(varargin))
    case 0
        
      this.images          = [];              
      this.lambda          = 1;
      this.lambda_q        = 1;    % Quadratic formulation of the objective function
      this.lambda2         = 1e-1;      % weight for coupling term
      this.lambda3         = 1;         % weight for non local term term

      
      this.sor_max_iters   = 1e2;       % 100 seems sufficient
      this.pcg_iters       = 10;
      this.pcg_tol         = 1e-6;
      this.limit_update    = true;      % limit the flow incrment to be less than 1 per linearization step
      this.display         = false;            
      
      this.solver          = 'backslash';   % 'sor' 'pcg' for machines with limited moemory       
      this.deriv_filter    = [1 -8 0 8 -1]/12; % 5-point 7 point [-1 9 -45 0 45 -9 1]/60; 
      
      this.texture         = false;     % use texture component as input
      this.fc              = false;     % use filter constancy

      this.median_filter_size   = []; %[5 5];
      this.interpolation_method = 'bi-cubic';      %'cubic', 'bi-linear
      
      % For Graduated Non-Convexity (GNC) optimization
      this.gnc_iters       = 3;
      this.alpha           = 1;             % change linearly from 1 to 0 through the GNC stages

      this.max_iters       = 10;            % number of warping per pyramid level
      this.max_linear      = 1;             % maximum number of linearization performed per warping, 1 OK for HS
      
      % For GNC stage 1
      this.pyramid_levels  = 4;           
      this.pyramid_spacing = 2;

      % For GNC stage 2 to end
      this.gnc_pyramid_levels     = 2;
      this.gnc_pyramid_spacing    = 1.25;                      
      
      method = 'generalized_charbonnier'; %'lorentzian'
      this.spatial_filters = {[1 -1], [1; -1]};
      a   = 0.45;
      sig = 1e-3;
      for i = 1:length(this.spatial_filters);
          this.rho_spatial_u{i}   = robust_function(method, sig, a);
          this.rho_spatial_v{i}   = robust_function(method, sig, a);
      end;
      this.rho_data        = robust_function(method, sig, a);
      
      this.imLab           = [];    % store segementation result
      this.mfT             = 15;    % threshold for intensity-median-filter
      this.imfsz           = [7 7]; % for intensity-median-filter
      this.filter_weight   = [];    % only for the new obj. charbonnier
      this.alp             = 0.95;  % for rof texture decomposition
      
      this.hybrid          = false;  
      this.area_hsz        = 10;    % half window size for the weighted median filter
      this.affine_hsz      = 4;     % half window size for robust affine 
      this.sigma_i         = 7;
      this.color_images     = [];
      this.auto_level       = true;
      this.old_auto_level   = false;
      
      this.input_seg        = [];
      this.input_occ        = [];
      this.isScale          = true;
      
      this.fullVersion      = false;
      this.warpingIncrement = 0;
      this.wmfIters         = 1;
      this.wmfPerLevel      = false;
      this.omitLastLevel    = false;
      this.bf               = false;
      this.useInlinePCG     = false;
      this.unEqualSampling  = false;
      
      this.tuv              = [];
      this.tocc             = [];
      this.flowEdgeMethod   = [];
      this.occMethod        = [];
      this.flowEdges        = [];
      this.occ              = [];
      this.seg              = [];
      this.minPriorConst = 1e-4; 
      this.minOccConst   = 1e-2;
      this.isFusionFlow  = false;
      this.orgImages     = [];
      
      this = class(this, 'classic_nl_optical_flow_seg');         
      
    case 1
      if isa(varargin{1}, 'classic_nl_optical_flow_seg')
        this = varargin{1};        
      else    
          this = classic_nl_optical_flow_seg;
          this.images = varargin{1};  
      end
      
    otherwise
      error('Incompatible arguments!');
      
  end