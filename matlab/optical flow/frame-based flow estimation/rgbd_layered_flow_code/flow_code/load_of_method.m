function ope = load_of_method(method)
%%
%LOAD_OF_METHOD loads the models for Optical Flow Estimation
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
% All commercial use of this software, whether direct or indirect, is
% strictly prohibited including, without limitation, incorporation into in
% a commercial product, use in a commercial service, or production of other
% artifacts for commercial purposes.     
%
% Permission to use, copy, modify, and distribute this software and its
% documentation for research purposes is hereby granted without fee,
% provided that the above copyright notice appears in all copies and that
% both that copyright notice and this permission notice appear in
% supporting documentation, and that the name of the author and Brown
% University not be used in advertising or publicity pertaining to
% distribution of the software without specific, written prior permission.        
%
% For commercial uses contact the Technology Venture Office of Brown University
% 
% THE AUTHOR AND BROWN UNIVERSITY DISCLAIM ALL WARRANTIES WITH REGARD TO
% THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
% FITNESS FOR ANY PARTICULAR PURPOSE.  IN NO EVENT SHALL THE AUTHOR OR
% BROWN UNIVERSITY BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL
% DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
% PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
% ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
% THIS SOFTWARE.        

median_filter_size = [5 5]; 

switch lower(method)
    

    %%% variant of 'classic+nl_seg-fast'
    case 'classic+nl_seg-fast_gtoccedgeff'
        ope = load_of_method('classic+nl_seg-fast');
        ope.occMethod  = 'gtocc';
        ope.flowEdgeMethod  = 'gtedge';  
        ope.isFusionFlow   = true;
        

    case 'classic+nl_seg-fast_projedge2_mucoccff'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'projectimage2';
        ope.occMethod  = 'mpc';   
        ope.isFusionFlow   = true;
        
    case 'classic+nl_seg-fast_gtoccedge'
        ope = load_of_method('classic+nl_seg-fast');
        ope.occMethod  = 'gtocc';
        ope.flowEdgeMethod  = 'gtedge';        
     
    case 'classic+nl_seg-fast_gtoccedge_lambda10'
        ope = load_of_method('classic+nl_seg-fast');
        ope.occMethod  = 'gtocc';
        ope.flowEdgeMethod  = 'gtedge';        
        ope.lambda = 10;
        ope.lambda_q = 10;
        
    case 'classic+nl_seg-fast_mpocc_gtedge'
        ope = load_of_method('classic+nl_seg-fast');
        ope.occMethod  = 'mp';
        ope.flowEdgeMethod  = 'gtedge';
        
    case 'classic+nl_seg-fast_mpocc_projedge'
        ope = load_of_method('classic+nl_seg-fast');
        ope.occMethod  = 'mp';
        ope.flowEdgeMethod  = 'projectimage';
    
%     case 'classic+nl_seg-fast_mpocc_projedge2'
%         ope = load_of_method('classic+nl_seg-fast');
%         ope.occMethod  = 'mp';
%         ope.flowEdgeMethod  = 'projectimage2';
        
    case 'classic+nl_seg-fast_mpocc'
        ope = load_of_method('classic+nl_seg-fast');
        ope.occMethod  = 'mp';
        
    case 'classic+nl_seg-fast_gtocc'
        ope = load_of_method('classic+nl_seg-fast');
        ope.occMethod  = 'gtocc';

    case 'classic+nl_seg-fast_gtedge'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'gtedge';
  
    case 'classic+nl_seg-fast_projedge'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'projectimage';

    case 'classic+nl_seg-fast_projedge2'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'projectimage2';

    case 'classic+nl_seg-fast_projedge2_gtocc'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'projectimage2';
        ope.occMethod  = 'gtocc';
        
    case 'classic+nl_seg-fast_projedge2_muocc'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'projectimage2';
        ope.occMethod  = 'mp';      

    case 'classic+nl_seg-fast_projedge2_mucocc'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'projectimage2';
        ope.occMethod  = 'mpc';           
        
    case 'classic+nl_seg-fast_projedgeflow'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'projectflow';       
        
    case 'classic+nl_seg-fast_imageedge'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'image';
    
    case 'classic+nl_seg-fast_segedge'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'segedge';

    case 'classic+nl_seg-fast_projsegedge'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'projsegedge';

    case 'classic+nl_seg-fast_projsegedge2'
        ope = load_of_method('classic+nl_seg-fast');
        ope.flowEdgeMethod  = 'projsegedge2';


    case 'classic+nl_seg-fast'
        ope = load_of_method('classic+nl_seg');        
        %ope.display  = true;
        ope.max_iters       = 3;
        ope.gnc_iters       = 2;
       
    case 'classic+nl_seg'
        ope = classic_nl_optical_flow_seg;
        ope.texture  = true;
        ope.median_filter_size   = median_filter_size;
        ope.color_images = ones(1,1,3);
        
    case 'srf+nl-fast-lambda2-lambbdaA8'
        ope = load_of_method('srf+nl-fast-lambda2-lambbdaA2');
        ope.lambdaA  = 8;    
    case 'srf+nl-fast-lambda2-lambbdaA4'
        ope = load_of_method('srf+nl-fast-lambda2-lambbdaA2');
        ope.lambdaA  = 4;        
    case 'srf+nl-fast-lambda2-lambbdaA2'
        ope = load_of_method('srf+nl-fast');
        ope.lambda   = 2;
        ope.lambda_q = ope.lambda;
        ope.lambdaA  = 2;

    case 'srf+nl-fast-lambda4-lambbdaA2'
        ope = load_of_method('srf+nl-fast');
        ope.lambda   = 4;
        ope.lambda_q = ope.lambda;
        ope.lambdaA  = 2;
        
    case 'srf+nl-fast'
        ope = load_of_method('srf+nl');
        ope.max_iters       = 3;
        ope.gnc_iters       = 2;        

    case 'srf+nl-lambda2-lambbdaA8'
        ope = load_of_method('srf+nl-lambda2-lambbdaA2');
        ope.lambdaA  = 8;    
    case 'srf+nl-lambda2-lambbdaA4'
        ope = load_of_method('srf+nl-lambda2-lambbdaA2');
        ope.lambdaA  = 4;        
    case 'srf+nl-lambda2-lambbdaA2'
        ope = load_of_method('srf+nl');
        ope.lambda   = 2;
        ope.lambda_q = ope.lambda;
        ope.lambdaA  = 2;
        
    case 'srf+nl'
        ope = load_of_method('srf++'); 
        ope.filter_choice = 'wmf';
        ope.area_hsz = 7;
        ope.sigma_i  = 7;

    case {'srf++test'}        
        ope = load_of_method('srf++'); 
        % 
        ope.max_iters       = 1;
        ope.gnc_iters       = 2;        
        
    case {'srf++fast'}        
        ope = load_of_method('srf++'); 
        % 
        ope.max_iters       = 3;
        ope.gnc_iters       = 2;        
        
    case 'srf++'
        ope = srf_pc_optical_flow;       
        
        ope.median_filter_size   = median_filter_size;
        ope.texture              = true;       
       
        % interpolation
        %ope.interpolation_method = 'bi-cubic';

        ope.alp = 0.95;
        ope.color_images = ones(1,1,3);
        ope.filter_choice = 'mf';
        
        ope.lambda = 3;
        ope.lambda_q =3;
        
        ope.display          = true;        

    case 'classic+nl-brightness'
        ope = load_of_method('classic+nl');        
        ope.texture         = false;
        
    case 'classic+nl-fast-brightness'
        ope = load_of_method('classic+nl');        
        ope.max_iters       = 3;
        ope.gnc_iters       = 2;
        ope.texture         = false;
    
    case {'classic+nl-fast-bf', 'classic+nl-fast-bf-robust-char', ...
            'classic+nl-fast-bf-robust-char-iter5', ...
            'classic+nl-fast-bf-robust-gc-iter5'}
        ope = load_of_method('classic+nl-fast');        
        ope.bf              = true;
   case 'classic+nl-fast-bf-full'
        ope = load_of_method('classic+nl-fast-bf');        
        ope.fullVersion     = true;
        
    case 'classic+nl-fast'
        ope = load_of_method('classic+nl');        
        ope.max_iters       = 3;
        ope.gnc_iters       = 2;
        %ope.display  = true;
        %ope.solver          = 'pcg'; %'backslash';   % 'sor' 'pcg' for machines with limited moemory
        
    case {'classic+nl-fast-8l', 'classic+nl-fast-8level'}
        ope = load_of_method('classic+nl-fast');  
        ope.auto_level = false;
        ope.pyramid_levels = 8;
        
    case 'classic+nl-fast-wmf2'
        ope = load_of_method('classic+nl-fast');        
        ope.wmfIters        = 2;
  
    case 'classic+nl-fast-char'
        ope = load_of_method('classic+nl-fast');        
        
    case {'classic+nl-fast-pcg-inline', 'classic+nl-faster'}
        ope = load_of_method('classic+nl-fast');
        ope.useInlinePCG = true;
        ope.pcg_iters    = 20;
        ope.pcg_tol      = 1e-6;
        fprintf('pcg_inline, %d iters, tol %3.3e\n', ope.pcg_iters, ope.pcg_tol);

    case {'classic+nl-fast-pcg-inline-iter10'}
        ope = load_of_method('classic+nl-fast-pcg-inline');
        ope.pcg_iters    = 10;
        fprintf('pcg_inline, %d iters, tol %3.3e\n', ope.pcg_iters, ope.pcg_tol);

    case {'classic+nl-fast-pcg-inline-bilinear-char'}
       ope = load_of_method('classic+nl-fast-pcg-inline');
       
       ope.interpolation_method = 'bi-linear';             
       method = 'charbonnier';
       ope.spatial_filters = {[1 -1], [1; -1]};
       for i = 1:length(ope.spatial_filters);
           ope.rho_spatial_u{i}   = robust_function(method, 1e-3);
           ope.rho_spatial_v{i}   = robust_function(method, 1e-3);
       end;
       ope.rho_data        = robust_function(method, 1e-3);
     
    case {'classic+nl-fast-pcg-inline-brightness'}
       ope = load_of_method('classic+nl-fast-pcg-inline');       
       ope.texture  = false;       

       
    case {'classic+nl-fast-pcg-inline-brightness-nolastlevel'}
       ope = load_of_method('classic+nl-fast-pcg-inline');       
       ope.texture  = false;
       ope.omitLastLevel = true;
       ope.display       = false;

    case {'classic+nl-fast-mike2'}
       ope = load_of_method('classic+nl-fast-mike');
       ope.omitLastLevel = false;
       
    case {'classic+nl-fast-mike'}
       ope = load_of_method('classic+nl-fast-pcg-inline');       
       ope.texture  = false;
       ope.omitLastLevel = true;
       ope.display       = false;
%        ope.pcg_iters    = 10;
%        ope.interpolation_method = 'bi-linear';             
%        method = 'charbonnier';
%        ope.spatial_filters = {[1 -1], [1; -1]};
%        for i = 1:length(ope.spatial_filters);
%            ope.rho_spatial_u{i}   = robust_function(method, 1e-3);
%            ope.rho_spatial_v{i}   = robust_function(method, 1e-3);
%        end;
%        ope.rho_data        = robust_function(method, 1e-3);
       
    case {'classic+nl-fast-pcg-inline-brightness-wmfperlevel'}
       ope = load_of_method('classic+nl-fast-pcg-inline');       
       ope.texture  = false; 
       ope.wmfPerLevel = true; 
    
    case {'classic+nl-fast-pcg-inline-brightness-wmfperlevel-nolastlevel'}
       ope = load_of_method('classic+nl-fast-pcg-inline');       
       ope.texture       = false; 
       ope.wmfPerLevel   = true; 
       ope.omitLastLevel = true;
       ope.display       = false;
       
    case {'classic+nl-fast-pcg-cond', 'classic+nl-fast-pcg'}
        ope = load_of_method('classic+nl-fast');        
        ope.solver = 'pcg';
        ope.pcg_iters    = 20;
        fprintf('pcg_built_in, %d iters\n', ope.pcg_iters);
        
    case {'classic+nl-fast-pcg-cond-iter20'}
        ope = load_of_method('classic+nl-fast');        
        ope.solver     = 'pcg';
        ope.pcg_iters  = 20;
        
    
    case {'classic+nl-pcg-cond-iter20'}
        ope = load_of_method('classic+nl');        
        ope.solver     = 'pcg';
        ope.pcg_iters  = 20;
        
%     case 'classic+nl-fast-sor'
%         ope = load_of_method('classic+nl-fast');        
%         ope.solver = 'sor';
%     case 'classic+nl-fast-sor-wi'
%         ope = load_of_method('classic+nl-fast-sor');        
%         ope.solver = 'sor';       
%         ope.warpingIncrement = 1;
        
    case 'classic+nl-fast-wi'
        % uses more warping at smaller image sizes
        ope = load_of_method('classic+nl-fast');        
        ope.warpingIncrement = 1;

        
    case 'classic+nl-hsz25'
        ope = load_of_method('classic+nl');  
        ope.area_hsz = 25;

    case 'classic+nl-fast-hsz50'
        ope = load_of_method('classic+nl-fast');  
        ope.area_hsz = 50;        
        
    case 'classic+nl-fast-hsz14'
        ope = load_of_method('classic+nl-fast');  
        ope.area_hsz = 14;
    
    case 'classic+nl-fast-hsz14-wi2'
        ope = load_of_method('classic+nl-fast');  
        ope.area_hsz = 14;
        ope.warpingIncrement = 1;
        
    case 'classic+nl-hsz14'
        ope = load_of_method('classic+nl');  
        ope.area_hsz = 14;
        
    case 'classic+nl-hsz14-20w'
        ope = load_of_method('classic+nl');  
        ope.area_hsz = 14;
        ope.max_iters= 20;

    case 'classic+nl-char-cubic-fast'        
        ope = load_of_method('classic+nl-char-cubic');
        ope.max_iters       = 3;
        ope.gnc_iters       = 2;
    case 'classic+nl-char-cubic'        
        ope = load_of_method('classic+nl');  
       
        ope.interpolation_method = 'cubic';     
        
        method = 'charbonnier'; 
        ope.spatial_filters = {[1 -1], [1; -1]};
        for i = 1:length(ope.spatial_filters);
            ope.rho_spatial_u{i}   = robust_function(method, 1e-3);
            ope.rho_spatial_v{i}   = robust_function(method, 1e-3);
        end;
        ope.rho_data        = robust_function(method, 1e-3);
        
        ope.lambda   = 5;
        ope.lambda_q = 5;
        
        
    case 'classic+nl-noscale'        
        ope = load_of_method('classic+nl');  
        
        ope.isScale = false;

    case 'classic+nl-fast2-down0.8'        
        ope = load_of_method('classic+nl-fast');
        ope.pyramid_spacing = 1.25;
        
    case 'classic+nl-fast2'        
        ope = load_of_method('classic+nl-fast');
        ope.unEqualSampling  = true;

    case {'classic+nl-fast2-b', 'classic+nl-fast2-brightness', 'classic+nl-fasta-brightness'}
        ope = load_of_method('classic+nl-fast');
        ope.unEqualSampling  = true;
        ope.texture         = false;
    case 'classic+nl2'        
        ope = load_of_method('classic+nl');
        ope.unEqualSampling  = true;

    case 'hs2'        
        ope = load_of_method('hs');
        ope.unEqualSampling  = true;

    case {'classic++2'}
        ope = load_of_method('classic++');
        ope.unEqualSampling  = true;
    
    case {'classic++3'}
        ope = load_of_method('classic++');
        ope.unEqualSampling  = true;
        ope.display = true;
             
    case {'classic++pcg-inline'}
        ope = load_of_method('classic++');
        ope.useInlinePCG = true;
        ope.pcg_iters    = 20;
        ope.pcg_tol      = 1e-6;
        
    case {'classic++pcg-inline2'}
        ope = load_of_method('classic++pcg-inline');
        ope.unEqualSampling  = true;
        ope.lambda   = 1;
        ope.lambda_q = 1;
        
    case 'classic+nl-fast-old'        
        ope = load_of_method('classic+nl-fast');
        ope.old_auto_level = true;
        
    case 'classic+nl-old'        
        ope = load_of_method('classic+nl');
        ope.old_auto_level = true;
        
    case {'classic+nl'}        
        ope = classic_nl_optical_flow;
        
        ope.texture  = true;
        ope.median_filter_size   = median_filter_size;
        
        ope.alp = 0.95;
        ope.area_hsz = 7;
        ope.sigma_i  = 7;
        ope.color_images = ones(1,1,3);
        
        ope.lambda = 3;
        ope.lambda_q =3;
        %ope.display  = true;        
        
    case 'classic+nl-full'
        ope = load_of_method('classic+nl');
        ope.fullVersion      = true;
       
    case {'hs-brightness'}
        % brightness constancy, with median filtering
        ope = hs_optical_flow;
        ope.median_filter_size   = median_filter_size;
        ope.lambda   = 10;
        ope.lambda_q = 10;        
    case {'hs-old'}
        ope = load_of_method('hs');   
        ope.old_auto_level = true;
    case {'hs'}
        % ROF texture constancy, with median filtering
        ope = hs_optical_flow;
        ope.median_filter_size   = median_filter_size;
        ope.texture              = true;        

        ope.lambda   = 40;
        ope.lambda_q = 40;
        ope.display  = false;       
%         ope.solver          = 'pcg'; %'backslash';   % 'sor' 'pcg' for machines with limited moemory

    case {'ba-brightness'}        
        % B&A brightness constancy model
        
        ope = ba_optical_flow;
        ope.median_filter_size   = median_filter_size;
        
        method = 'lorentzian'; %'geman_mcclure'; 
        ope.spatial_filters = {[1 -1], [1; -1]};
        for i = 1:length(ope.spatial_filters);
            ope.rho_spatial_u{i}   = robust_function(method, 0.1); 
            ope.rho_spatial_v{i}   = robust_function(method, 0.1);
        end;
        ope.rho_data        = robust_function(method, 3.5);
        
        ope.lambda = 0.045;
        ope.lambda_q = 0.045 ;        
       
    case {'classic-l', 'ba'}
        
        ope = load_of_method('ba-brightness');               
        ope.median_filter_size   = median_filter_size;
        ope.texture              = true;        
       
        method = 'lorentzian'; %'geman_mcclure'; 
        ope.spatial_filters = {[1 -1], [1; -1]};
        for i = 1:length(ope.spatial_filters);
            ope.rho_spatial_u{i}   = robust_function(method, 0.03); 
            ope.rho_spatial_v{i}   = robust_function(method, 0.03);
        end;
        ope.rho_data        = robust_function(method, 1.5);        
      
        ope.lambda = 0.06;
        ope.lambda_q = 0.06 ;
        
    case 'classic-c-a'
        ope = alt_ba_optical_flow;            
        ope.median_filter_size   = median_filter_size;
        ope.texture              = true;
        method = 'charbonnier'; 
        ope.spatial_filters = {[1 -1], [1; -1]};
        for i = 1:length(ope.spatial_filters);
            ope.rho_spatial_u{i}   = robust_function(method, 1e-3);
            ope.rho_spatial_v{i}   = robust_function(method, 1e-3);
        end;
        ope.rho_data        = robust_function(method, 1e-3);
        ope.display         = false;
        
        ope.lambda2         = 1e2;    
        ope.lambda3         = 1;      
        
        ope.weightRatio     = ope.lambda2/ope.lambda3;     % lambda2/lambda3
        ope.itersLO         = 5;     % # Li & Osher median formula iteration
        
        ope.lambda   = 5;
        ope.lambda_q = 5;
        
    case {'classic-c-brightness'}
        %charbonnier penalty function
        ope = ba_optical_flow;
        ope.median_filter_size   = median_filter_size;
        ope.texture              = false;        
        method = 'charbonnier'; 
        ope.spatial_filters = {[1 -1], [1; -1]};
        for i = 1:length(ope.spatial_filters);
            ope.rho_spatial_u{i}   = robust_function(method, 1e-3); 
            ope.rho_spatial_v{i}   = robust_function(method, 1e-3);
        end;
        ope.rho_data        = robust_function(method, 1e-3); 
        
        ope.lambda   = 3;
        ope.lambda_q = 3;
        
    case {'classic-c'}
        ope = load_of_method('classic-c-brightness');
        ope.texture            = true;        
        ope.lambda   = 5;
        ope.lambda_q = 5;

    case {'classic-c-noMF'}
        ope = load_of_method('classic-c');
        ope.median_filter_size = [];

    case {'classic-c-noMF-lastlevel'}
        ope = load_of_method('classic-c');
        ope.noMFlastlevel = true;
        
    case {'classic++'}
        ope = ba_optical_flow;
        ope.median_filter_size = median_filter_size;
        ope.texture            = true;
        ope.interpolation_method = 'bi-cubic';        
        
        method = 'generalized_charbonnier'; 
        ope.spatial_filters = {[1 -1], [1; -1]};
        a   = 0.45;
        sig = 1e-3;
        for i = 1:length(ope.spatial_filters);
            ope.rho_spatial_u{i}   = robust_function(method, sig, a);
            ope.rho_spatial_v{i}   = robust_function(method, sig, a);
        end;
        ope.rho_data        = robust_function(method, sig, a);                
        
        ope.lambda = 3;
        ope.lambda_q =3;
        ope.display = false;
    case {'classic++-old'}
        ope = load_of_method('classic++');
        ope.old_auto_level = true;
      
    case 'classic+nl-rgbd'        
        ope = classic_nl_rgbd_scene_flow;
        
        ope.texture  = true;
        ope.median_filter_size   = median_filter_size;
        
        ope.alp = 0.95;
        ope.area_hsz = 7;
        ope.sigma_i  = 7;
        ope.color_images = ones(1,1,3);
        
        ope.lambda = 3;
        ope.lambda_q =3;
        ope.sigma_d  = 7/4;

    case 'classic+nl-rgbd-fast'
            ope = load_of_method('classic+nl-rgbd');        
            ope.max_iters       = 3;
            ope.gnc_iters       = 2;
    otherwise
        error('unknown optical flow estimation method!');
end;
