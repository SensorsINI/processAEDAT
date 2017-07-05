function generate_gif_from_folder(fdir, frameRate)
%%

if nargin < 2
    frameRate = 1;
end;

fns = dir(fdir);
fns = fns(3:end);

ims = [];
for i=1:length(fns)
    fn = fullfile(fdir, fns(i).name);
    im = imread(fn);
    ims = cat(length(size(im))+1, ims, im);    
end

fn = fullfile(fdir, 'all.gif');

if size(im,3)==3
    frame2gif(ims, fn, frameRate);
elseif size(im,3)==3
    frame2gif_gray(ims, fn, frameRate);
end