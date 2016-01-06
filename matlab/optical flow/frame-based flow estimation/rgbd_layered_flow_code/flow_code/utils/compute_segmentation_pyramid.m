function P = compute_segmentation_pyramid(img, nL, ratio, method, refP)
%%  COMPUTE_IMAGE_PYRAMID computes nL level image pyramid of the input image IMG using filter F 

%   Author: Deqing Sun, Department of Computer Science, Brown University
%   Contact: dqsun@cs.brown.edu
%   $Date: 2007-10-10 $
%   $Revision $

if nargin >=5
    nL = length(refP);
end

if nargin<4 || isempty(method)
    method = 'nearest';
end

P   = cell(nL,1);
tmp = img;
P{1}= tmp;

for m = 2:nL    
    
    if nargin >=5
        sz = [size(refP{m},1), size(refP{m},2)];
    else
        sz  = round([size(tmp,1) size(tmp,2)]*ratio);
    end
    
    tmp = imresize(tmp, sz, method);
    
    if size(img, 4)>1
        tmp = reshape(tmp, [size(tmp,1), size(tmp,2), size(img,3), size(img,4)]);
    end;

    P{m} = tmp;
end;

	


	
	

