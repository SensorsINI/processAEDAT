function [e d]= compute_warping_energy(I, u, v)

% for testing imwarp_grad_im

uv = cat(3, u, v);

I = reshape(I, size(u));
%Iw  = imwarp_grad_im(I, u, v);
Iw  = imwarp_grad_im(uv, I);

Iw(isnan(Iw)) = 0;
e   = sum(Iw(:).^2);
%  e   = sum(Iw(:));
if nargout == 2
    
    %[tmp d] = imwarp_grad_im(uv, I);
    
    [A indx] = imwarpmtx_for(uv);
    
    d = 2 * A'*Iw(:);
    %d = 2*Iw.*d;
    d = d(:);
end;

