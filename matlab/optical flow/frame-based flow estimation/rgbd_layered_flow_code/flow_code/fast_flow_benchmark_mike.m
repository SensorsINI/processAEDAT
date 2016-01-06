function fast_flow_benchmark_mike

%%
dataDir = 'C:\Users\dqsun\Dropbox\data\mike';

% % method = 'classic+nl-fast-bf-robust-char-iter5'; %'classic+nl-fast-bf-robust-char'; %'classic+nl-fast-bf-full';
% % method = 'classic+nl-fast-bf-robust-gc-iter5';
% % method = 'classic+nl-fast-sor-wi';
% % method = 'classic+nl-char-cubic-fast' ;
% % method = 'classic+nl-fast-pcg-cond';
% % % method = 'classic+nl-pcg-cond-iter20';
% % % method = 'classic+nl-fast';
% % method = 'classic+nl-fast-pcg-inline';
% % method = 'classic+nl-fast-pcg-inline-iter10';
% % method = 'classic+nl-fast-pcg-inline-bilinear-char';
% % method = 'classic+nl-fast-pcg-inline-brightness';
% % method = 'classic+nl-fast-pcg-inline-brightness-nolastlevel';
% % % method = 'classic+nl-fast-pcg-inline-brightness-wmfperlevel';
% % method = 'classic+nl-fast-pcg-inline-brightness-wmfperlevel-nolastlevel';
method = 'classic+nl-fast-mike';

resultDir = fullfile(dataDir, method);
if ~exist(resultDir, 'file');
    mkdir (resultDir);
end;

fns = dir(dataDir);
ratio = 1;

fn = fullfile(dataDir, 'train00555_015.jpg');
im1 = imread(fn);
fn = fullfile(dataDir, 'train00555_016.jpg');
im2 = imread(fn);

sim1 = imresize(im1, ratio);
sim2 = imresize(im2, ratio);

tic;
uv = estimate_flow_interface(sim1, sim2, method);
uv = imresize(uv, [size(im1,1) size(im1,2)])/ratio;
fprintf('%s %3.3f seconds\n', method, toc);
%%
fn = fullfile(resultDir, 'flow.flo');
writeFlowFile(uv, fn);
fn = fullfile(resultDir, ['flow.png']);
imwrite(flowToColor(uv), fn);
% warped image
imw = double(im2);
for c = 1:size(imw,3)
    imw(:,:,c) = imwarp(imw(:,:,c), uv(:,:,1), uv(:,:,2));
end;
fn = fullfile(resultDir, ['warped.png']);
imwrite(uint8(imw), fn);

%% laptop 
% classic+nl-fast 30.644 second
% classic+nl-fast-pcg-inline 5.740 seconds
% classic+nl-fast-pcg-inline-iter10 4.934 seconds
% classic+nl-fast-pcg-inline-bilinear-char 4.821 seconds
% classic+nl-fast-pcg-inline-brightness 3.988 seconds
% classic+nl-fast-pcg-inline-brightness-wmfperlevel 4.002 seconds
% classic+nl-fast-pcg-inline-brightness-wmfperlevel-nolastlevel 2.950 seconds
% downsample by half
% classic+nl-fast-pcg-inline-brightness 1.356 seconds
% classic+nl-fast-pcg-inline-brightness-wmfperlevel 1.302 seconds
% classic+nl-fast-pcg-inline-brightness-nolastlevel 1.425 seconds
% classic+nl-fast-pcg-inline-brightness-wmfperlevel-nolastlevel wmf still on last level 2.759 seconds
% 
%% desktop (windows)
% classic+nl-fast 18.946 seconds
% classic+nl-fast-pcg-inline 5.529 seconds

% on downsampled by half image
% classic+nl-fast-pcg-inline-brightness-wmfperlevel 1.437 seconds