function imo = local_smoothed_histogram_filter(im)
%%

% according to paper Kass, M. & Solomon, J. Smoothed local histogram
% filters ACM Trans. Graph., 2010, 29 

% input IM is a grayscale image

% median
sigmaHist = 0.06; %params.sigmaHist;
nBins     = 30; %params.nBins;
sigmaIm   = 6; %params.sigmaIm
antialiasWidth  = 3; 
medianTarget    = 0.5;

[H W] = size(im);

imInt = ones(H, W, nBins);

bins = linspace(min(im(:)), max(im(:)), nBins);

for c =1:nBins
    imInt(:,:,c) = imInt(:,:,c) * bins(c);
end;

imInt = 0.5 * (1 + erf( (imInt - repmat(im, [1 1 nBins])) /sigmaHist/sqrt(2) ) );

% smooth in the x and y direction
f = fspecial('gaussian', [4*round(sigmaIm)+1 1], sigmaIm);
% f = fspecial('average', [2*round(sigmaIm)+1 1]);

% horizontal direction
for c =1:nBins
    imInt(:,:,c) = imfilter(imInt(:,:,c), f, 'replicate');
end;
% vertical direction
for c =1:nBins
    imInt(:,:,c) = imfilter(imInt(:,:,c), f', 'replicate');
end;

%%%%%%%%%%% TO ADD: downsample and then upsample

%%%%%%%%%%% TO ADD: filtering in the intensity direction



% find the point which exceed median Target
mask = double(imInt >= medianTarget);
mask(:,:,1:end-1) = mask(:,:,1:end-1) - mask(:,:,2:end);
% [row col sta] = find(mask==-1);
ind  = find(mask==-1);
[r c s] = ind2sub([H W nBins], ind);

ind2 = sub2ind([H W nBins], r, c, s+1);

tmp = bins(s)' + (medianTarget - imInt(ind))./(imInt(ind2)- imInt(ind)).*...
    (bins(s+1)-bins(s))';
imo = reshape(tmp, H, W);
ind3 = sub2ind([H W], r, c);
imo(ind3) = tmp;