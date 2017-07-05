function P = compute_image_pyramid(img, f, nL, ratio, refP)
%%  COMPUTE_IMAGE_PYRAMID computes nL level image pyramid of the input image IMG using filter F 

%   Author: Deqing Sun, Department of Computer Science, Brown University
%   Contact: dqsun@cs.brown.edu
%   $Date: 2007-10-10 $
%   $Revision $

% Copyright 2007-2008, Brown University, Providence, RI.
%
%                         All Rights Reserved
%
% Permission to use, copy, modify, and distribute this software and its
% documentation for any purpose other than its incorporation into a
% commercial product is hereby granted without fee, provided that the
% above copyright notice appear in all copies and that both that
% copyright notice and this permission notice appear in supporting
% documentation, and that the name of the author and Brown University not be used in
% advertising or publicity pertaining to distribution of the software
% without specific, written prior permission.
%
% THE AUTHOR AND BROWN UNIVERSITY DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
% INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR ANY
% PARTICULAR PURPOSE.  IN NO EVENT SHALL THE AUTHOR OR BROWN UxNIVERSITY BE LIABLE FOR
% ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
% WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
% ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
% OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE. 

if nargin >=5
    nL = length(refP);
end

P   = cell(nL,1);
tmp = img;
P{1}= tmp;

% Get version information
%   From http://www.mathworks.com/matlabcentral/fileexchange/17285
v = sscanf (version, '%d.%d.%d') ; v = 10.^(0:-1:-(length(v)-1)) * v ;



for m = 2:nL    
    % Gaussian filtering 
    tmp = imfilter(tmp, f, 'corr', 'symmetric', 'same');           

    if nargin >=5
        sz = [size(refP{m},1), size(refP{m},2)];
    else
        sz  = round([size(tmp,1) size(tmp,2)]*ratio);
    end
    
    if min(sz) < 2
        break;
    end
    
    % IMRESIZE changes default algorithm since version 7.4 (R2007a)
    if v > 7.3
        tmp = imresize(tmp, ratio, 'bilinear', 'Antialiasing', false);   % better than 'nearest'
    else
        tmp = imresize(tmp, sz, 'bilinear', 0); % Disable antialiasing, old version for cluster
    end;
    
    if size(img, 4)>1
        tmp = reshape(tmp, [size(tmp,1), size(tmp,2), size(img,3), size(img,4)]);
    end;

    P{m} = tmp;
end;

	


	
	

