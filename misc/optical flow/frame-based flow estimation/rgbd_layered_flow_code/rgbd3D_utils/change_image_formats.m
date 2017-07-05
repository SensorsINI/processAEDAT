%%
fdir = 'C:\Users\dqsun\Dropbox\CVPR2015\RGBD\paper\figure\teddy';
fdir = 'C:\Users\dqsun\Dropbox\CVPR2015\RGBD\paper\figure\cones';
odir = fdir;
fns = dir(fdir);

for i=3:length(fns)
    fn = fullfile(fdir, fns(i).name);
    ind = strfind(fn, '.');
    im = imread(fn);
    fn(ind(end)+1:end) = 'png';
    imwrite(im, fn);
end