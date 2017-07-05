function [ZI, ZXI, ZYI] = interp2_bicubic_partial_mex(Z, XI, YI, Dxfilter)
% function varargout = interp2_bicubic(Z, XI, YI)

%   Author:  Stefan Roth, Department of Computer Science, TU Darmstadt
%   Contact: sroth@cs.tu-darmstadt.de
%   $Date $
%   $Revision$

% Copyright 2004-2007 Brown University, Providence, RI.
% Copyright 2007-2008 TU Darmstadt, Darmstadt, Germany.
% 
%                         All Rights Reserved
% 
% Permission to use, copy, modify, and distribute this software and its
% documentation for any purpose other than its incorporation into a
% commercial product is hereby granted without fee, provided that the
% above copyright notice appear in all copies and that both that
% copyright notice and this permission notice appear in supporting
% documentation, and that the name of Brown University not be used in
% advertising or publicity pertaining to distribution of the software
% without specific, written prior permission.
% 
% BROWN UNIVERSITY DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
% INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR ANY
% PARTICULAR PURPOSE.  IN NO EVENT SHALL BROWN UNIVERSITY BE LIABLE FOR
% ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
% WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
% ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
% OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

  % Implementation according to Numerical Recipes
  
  % modified by dqsun
  if nargin < 4
      Dxfilter = [-0.5 0 0.5];
  end;
  Dyfilter = Dxfilter';
  Dxyfilter = conv2(Dxfilter, Dyfilter, 'full');  
    
  % x-derivative at 4 neighbors
%   DX = imfilter(Z, [-0.5, 0, 0.5], 'symmetric', 'corr');
  DX = imfilter(Z, Dxfilter, 'symmetric', 'corr'); % modified by dqsun

  % y-derivative at 4 neighbors
%   DY = imfilter(Z, [-0.5, 0, 0.5]', 'symmetric', 'corr'); 
  DY = imfilter(Z, Dyfilter, 'symmetric', 'corr'); % modified by dqsun

  % xy-derivative at 4 neighbors
%   DXY = imfilter(Z, 0.25 * [1, 0, -1; 0 0 0; -1 0 1], 'symmetric', 'corr');
  DXY = imfilter(Z, Dxyfilter, 'symmetric', 'corr'); % modified by dqsun

  
  [ZI, ZXI, ZYI] = imwarp_bicubic_mex(Z, DX, DY, DXY, XI-1, YI-1);