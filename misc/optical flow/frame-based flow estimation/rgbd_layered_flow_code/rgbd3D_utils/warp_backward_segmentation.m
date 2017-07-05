function seg2 = warp_backward_segmentation(seg, uvb)

% Replicate so that out of boundary pixels are assigned

rep = ceil(max(abs(uvb(:))));

pad_seg = padarray(seg, rep*[1 1], 'replicate', 'both');        
pad_uvb(:,:,1) = padarray(uvb(:,:,1), rep*[1 1]);        
pad_uvb(:,:,2) = padarray(uvb(:,:,2), rep*[1 1]);        

pad_seg2 = warp_backward(pad_uvb, pad_seg, 'nearest');

seg2 = pad_seg2(rep+1:end-rep, rep+1:end-rep); 