function model = classic_nl_rgbd_scene_flow(varargin)
%%
%classic_nl_rgbd_scene_flow   
%       Optical flow computation with Classic formulation descended from
%       Horn & Schunck and Black & Anandan, plut a non-local term that
%       integrates information over a large spatial neighborhoods
%
% References:
% -----------
% Sun, D.; Roth, S. & Black, M. J. "Secrets of Optical Flow Estimation and
%   Their Principles" IEEE Int. Conf. on Comp. Vision & Pattern Recognition, 2010  
%
% Sun, D.; Roth, S. & Black, M. J. "A Quantitative Analysis of Current
%   Practices in Optical Flow Estimation and The Principles Behind Them" 
%   Technical Report Brown-CS-10-03, 2010   
%       
%   classic_nl_rgbd_scene_flow([IMGS]) constructs an  optical flow object
%   with the optional image sequence IMGS ([n x m x 2] array). 
%   classic_nl_rgbd_scene_flow(O) constructs BA optical flow object by copying O.
%  
%   model is a member function of the class 'classic_nl_rgbd_scene_flow'. 
%
% Authors: Deqing Sun, Department of Computer Science, Brown University
% Contact: dqsun@cs.brown.edu
% $Date: $
% $Revision: $
%
% Copyright 2007-2010, Brown University, Providence, RI. USA
% 
%                          All Rights Reserved
% 
% All commercial use of model software, whether direct or indirect, is
% strictly prohibited including, without limitation, incorporation into in
% a commercial product, use in a commercial service, or production of other
% artifacts for commercial purposes.     
%
% Permission to use, copy, modify, and distribute model software and its
% documentation for research purposes is hereby granted without fee,
% provided that the above copyright notice appears in all copies and that
% both that copyright notice and model permission notice appear in
% supporting documentation, and that the name of the author and Brown
% University not be used in advertising or publicity pertaining to
% distribution of the software without specific, written prior permission.        
%
% For commercial uses contact the Technology Venture Office of Brown University
% 
% THE AUTHOR AND BROWN UNIVERSITY DISCLAIM ALL WARRANTIES WITH REGARD TO
% model SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
% FITNESS FOR ANY PARTICULAR PURPOSE.  IN NO EVENT SHALL THE AUTHOR OR
% BROWN UNIVERSITY BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL
% DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
% PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
% ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
% model SOFTWARE.        

error(nargchk(0, 1, length(varargin)));
  
  switch (length(varargin))
    case 0
        
      model.images          = [];              
      model.lambda          = 1;
      model.lambda_q        = 1;    % Quadratic formulation of the objective function
      model.lambda2         = 1e-1;      % weight for coupling term
      model.lambda3         = 1;         % weight for non local term term

      
      model.sor_max_iters   = 1e2;       % 100 seems sufficient
      model.pcg_iters       = 10;
      model.pcg_tol         = 1e-6;
      model.limit_update    = true;      % limit the flow incrment to be less than 1 per linearization step
      model.display         = false;            
      
      model.solver          = 'backslash';   % 'sor' 'pcg' for machines with limited moemory       
      model.deriv_filter    = [1 -8 0 8 -1]/12; % 5-point 7 point [-1 9 -45 0 45 -9 1]/60; 
      
      model.texture         = false;     % use texture component as input
      model.fc              = false;     % use filter constancy

      model.median_filter_size   = []; %[5 5];
      model.interpolation_method = 'bi-cubic';      %'cubic', 'bi-linear
      
      % For Graduated Non-Convexity (GNC) optimization
      model.gnc_iters       = 3;
      model.alpha           = 1;             % change linearly from 1 to 0 through the GNC stages

      model.max_iters       = 10;            % number of warping per pyramid level
      model.max_linear      = 1;             % maximum number of linearization performed per warping, 1 OK for HS
      
      % For GNC stage 1
      model.pyramid_levels  = 4;           
      model.pyramid_spacing = 2;

      % For GNC stage 2 to end
      model.gnc_pyramid_levels     = 2;
      model.gnc_pyramid_spacing    = 1.25;                      
      
      method = 'generalized_charbonnier'; %'lorentzian'
      model.spatial_filters = {[1 -1], [1; -1]};
      a   = 0.45;
      sig = 1e-3;
      for i = 1:length(model.spatial_filters);
          model.rho_spatial_u{i}   = robust_function(method, sig, a);
          model.rho_spatial_v{i}   = robust_function(method, sig, a);
      end;
      model.rho_data        = robust_function(method, sig, a);
      
      model.seg             = [];    % store segementation result
      model.mfT             = 15;    % threshold for intensity-median-filter
      model.imfsz           = [7 7]; % for intensity-median-filter
      model.filter_weight   = [];    % only for the new obj. charbonnier
      model.alp             = 0.95;  % for rof texture decomposition
      
      model.hybrid          = false;  
      model.area_hsz        = 10;    % half window size for the weighted median filter
      model.affine_hsz      = 4;     % half window size for robust affine 
      model.sigma_i         = 7;
      model.sigma_d  = 7;
      model.color_images     = [];
      model.depths           = [];
      model.auto_level       = true;
      model.old_auto_level   = false;
      
      model.input_seg        = [];
      model.input_occ        = [];
      model.isScale          = true;
      
      model.fullVersion      = false;
      model.warpingIncrement = 0;
      model.wmfIters         = 1;
      model.wmfPerLevel      = false;
      model.omitLastLevel    = false;
      model.bf               = false;
      model.useInlinePCG     = false;
      model.unEqualSampling  = false;
      
      model = class(model, 'classic_nl_rgbd_scene_flow');         
      
    case 1
      if isa(varargin{1}, 'classic_nl_rgbd_scene_flow')
        model = varargin{1};        
      else    
          model = classic_nl_rgbd_scene_flow;
          model.images = varargin{1};  
      end
      
    otherwise
      error('Incompatible arguments!');
      
  end