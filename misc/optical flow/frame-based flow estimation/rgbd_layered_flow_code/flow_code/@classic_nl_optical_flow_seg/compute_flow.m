function [uv seg occ flowEdge] = compute_flow(this, init, gt)
%%
%COMPUTE_FLOW   Compute flow field
%   UV = COMPUTE_FLOW(THIS[, INIT]) computes the flow field UV with
%   algorithm THIS and the optional initialization INIT.
%  
%   This is a member function of the class 'classic_nl_optical_flow'. 
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
    if this.display
        tic
    end
  % Frame size
  sz = [size(this.images, 1), size(this.images, 2)];

  % If we have no initialization argument, initialize with all zeros
  if (nargin < 2)
    uv = zeros([sz, 2]);
  else
    uv = init;
  end

  
  [this, data] = pre_process_data(this);
  
    
  % gradually increase non-local term size 
  %nlsz = round(linspace(2, this.area_hsz, this.pyramid_levels));
  %nlsz  = round(logspace(log10(this.area_hsz), log10(2), this.pyramid_levels));
  
  for ignc = 1:this.gnc_iters     
  
      if this.display
          disp(['GNC stage: ', num2str(ignc)])
      end
          
      if ignc == 1
          pyramid_levels = this.pyramid_levels;
          pyramid_spacing = this.pyramid_spacing;
      else
          pyramid_levels = this.gnc_pyramid_levels;
          pyramid_spacing = this.gnc_pyramid_spacing;
      end;      
     
      % Iterate through all pyramid levels starting at the top
      for l = pyramid_levels:-1:1

          if this.display
              disp(['-Pyramid level: ', num2str(l)])
          end

          % Generate copy of algorithm with single pyramid level and the
          % appropriate subsampling
          small = this;
          
          small.max_iters = this.max_iters +...
              this.warpingIncrement * (l-1);
          if this.display
              fprintf('%d warping steps\n', small.max_iters);
          end;
          
          if ignc == 1
              small.images      = data.pyramid_images{l};                            
              small.max_linear  = 1;             
%               im1   = data.org_pyramid_images{l}(:,:,1);
              small.color_images      = data.org_color_pyramid_images{l}; 
              small.tuv               = data.pyramid_tuv{l};
              small.tocc              = data.pyramid_tocc{l};
              small.seg               = data.pyramid_seg{l};
              small.orgImages         = data.org_pyramid_images{l};
          else
              small.images = data.gnc_pyramid_images{l};
%               im1   = data.org_gnc_pyramid_images{l}(:,:,1);
              small.color_images = data.org_color_gnc_pyramid_images{l};
              small.tuv          = data.gnc_pyramid_tuv{l};
              small.tocc         = data.gnc_pyramid_tocc{l};
              small.seg          = data.gnc_pyramid_seg{l};
              small.orgImages    = data.org_gnc_pyramid_images{l};
          end;
          
          nsz   = size(small.images);
          nsz   = nsz(1:2);
          

          
          % Rescale the flow field
          if this.unEqualSampling
              uv = resample_flow_unequal(uv, nsz);
          else
              uv = resample_flow(uv, nsz);
          end

          %small.imLab = im1;      

          if ~isempty(this.flowEdgeMethod)
              small = detect_flow_edges(small, uv);
          end
          
          if ~isempty(this.occMethod)
              small = detect_occlusion(small, uv);
          end
         
          if this.isFusionFlow & (ignc == this.gnc_iters)
             uv  = fuse_flow(small, uv); 
          end
          
%           figure; imagesc(small.occ); colormap gray;
          
          if this.omitLastLevel && l ==1;
              if this.display
                  fprintf('omit level %d', l);
              end;
          else
              % Run flow method on subsampled images
              if small.useInlinePCG
                  uv = compute_flow_base_pcg_inline(small, uv);
              else
                  [uv small] = compute_flow_base(small, uv);
              end;
          end;

% tmp_uv = imresize(uv, sz);
% [aae stdae aepe] = flowAngErrUV(this.tuv, tmp_uv, 0);
% fprintf('%3.3f\n', aepe);

% fn = fullfile('F:\result\tmp\pyramid', sprintf('%d_%d_flow.png', ignc, l));          
% imwrite(flowToColor(uv), fn);
% 
% fn = fullfile('F:\result\tmp\pyramid', sprintf('%d_%d_im1.png', ignc, l));          
% imwrite(uint8(small.images(:,:,1)), fn);
% 
% fn = fullfile('F:\result\tmp\pyramid', sprintf('%d_%d_im2.png', ignc, l));          
% imwrite(uint8(small.images(:,:,2)), fn);
% 
% fn = fullfile('F:\result\tmp\pyramid', sprintf('%d_%d_gtedge.png', ignc, l));          
% imwrite(uint8(small.flowEdges*255), fn);
% 
% fn = fullfile('F:\result\tmp\pyramid', sprintf('%d_%d_gtocc.png', ignc, l));          
% imwrite(uint8(small.tocc*255), fn);



% figure; imshow(flowToColor(uv));          

      end      
            
      % Update GNC parameters (linearly)
      if this.gnc_iters > 1
          new_alpha  = 1 - ignc / (this.gnc_iters-1);
          this.alpha = min(this.alpha, new_alpha);
          this.alpha = max(0, this.alpha);          
      end;

      if this.display
          fprintf('GNC stage %d finished, %3.2f minutes passed \t \t', ignc, toc/60);
          if nargin == 3
              [aae stdae aepe] = flowAngErr(gt(:,:,1), gt(:,:,2), uv(:,:,1), uv(:,:,2), 0);        % ignore 0 boundary pixels
              fprintf('AAE %3.3f STD %3.3f average end point error %3.3f \n', aae, stdae, aepe);
          end;
      end;
  end; 
  
  if nargout >1
      occ = small.occ;
      flowEdge = small.flowEdges;
      seg = small.seg;
  end