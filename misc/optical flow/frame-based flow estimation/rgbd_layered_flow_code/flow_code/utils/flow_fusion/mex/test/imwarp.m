function O = imwarp(I, u, v, nopad)
%IMWARP   Warp image with flow field
%   O = IMWARP(I, U, V[, NOPAD]) warps the image I with optical flow field
%   U and V.  The flow field is to be given in the coordinate system of
%   O, i.e. the operation warps I toward O.  If the optional argument
%   NOPAD is given and true, the undefined pixels (source pixel outside
%   the boundary) are given by the nearest boundary pixels, otherwise
%   they are set to NaN.
%
%   Author:  Stefan Roth, Department of Computer Science, Brown University
%   Contact: roth@cs.brown.edu
%   $Date: 2006-07-06 10:30:40 -0400 (Thu, 06 Jul 2006) $
%   $Revision: 160 $

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

  
  % Image size
  sx = size(I, 2); 
  sy = size(I, 1); 

  % Image size w/ padding
  spx = sx + 2;
  spy = sy + 2;
  
  
  if (nargin > 3 & nopad)  
    % Warped image coordinates
    [X, Y] = meshgrid(1:sx, 1:sy);
    XI = reshape(X + u, 1, sx * sy);
    YI = reshape(Y + v, 1, sx * sy);
    
    % Bound coordinates to valid region
    XI = max(1, min(sx - 1E-6, XI));
    YI = max(1, min(sy - 1E-6, YI));
    
    % Perform linear interpolation
    fXI = floor(XI);
    cXI = ceil(XI);
    fYI = floor(YI);
    cYI = ceil(YI);
    
    alpha_x = XI - fXI;
    alpha_y = YI - fYI;
    
    O = (1 - alpha_x) .* (1 - alpha_y) .* I(fYI + sy * (fXI - 1)) + ...
        alpha_x .* (1 - alpha_y) .* I(fYI + sy * (cXI - 1)) + ...
        (1 - alpha_x) .* alpha_y .* I(cYI + sy * (fXI - 1)) + ...
        alpha_x .* alpha_y .* I(cYI + sy * (cXI - 1));
  
  else
    % Pad image with NaNs
    Z = [NaN(1, sx+2); NaN(sy, 1), I, NaN(sy, 1); NaN(1, sx+2)];
    
    % Warped image coordinates in padded image
    [X, Y] = meshgrid(2:sx+1, 2:sy+1);
    XI = reshape(X + u, 1, sx * sy);
    YI = reshape(Y + v, 1, sx * sy);
    
    % Bound coordinates to valid region
    XI = max(1, min(spx - 1E-6, XI));
    YI = max(1, min(spy - 1E-6, YI));
    
    % Perform linear interpolation
    fXI = floor(XI);
    cXI = ceil(XI);
    fYI = floor(YI);
    cYI = ceil(YI);
    
    alpha_x = XI - fXI;
    alpha_y = YI - fYI;
    
    O = (1 - alpha_x) .* (1 - alpha_y) .* Z(fYI + spy * (fXI - 1)) + ...
        alpha_x .* (1 - alpha_y) .* Z(fYI + spy * (cXI - 1)) + ...
        (1 - alpha_x) .* alpha_y .* Z(cYI + spy * (fXI - 1)) + ...
        alpha_x .* alpha_y .* Z(cYI + spy * (cXI - 1));
  end
  
  O = reshape(O, sy, sx);
