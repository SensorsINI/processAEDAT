% This script takes as input a sequence of images (specified by dataFile)
% and converts them to an aedat-logfile composed of events. 
% It also converts the ground truth of the flow field between two frames 
% (given in a flo-file specified by gtFrame) to event-based ground truth (a
% mat-file gtEvent with three 2D-arrays containing the x- and y- components
% of flow and the corresponding timestamps.

clearvars;

% Load video
addpath('D:/Google Drive/Studium/Masterthese/Code/MATLAB/frame-based flow visualization');
addpath('D:/Google Drive/Studium/Masterthese/Code/jAER-sensors/scripts/matlab');

dataFile = 'D:/Google Drive/Studium/Masterthese/Data/middlebury dataset/grayscale all frames/RubberWhale';
gtFrame = 'D:/Google Drive/Studium/Masterthese/Data/middlebury dataset/ground truth/RubberWhale/flow10.flo';
gtEvent = 'D:/Google Drive/Studium/Masterthese/Data/middlebury dataset/ground truth/RubberWhale/flow10.mat';

thr = 1.5; % contrast threshold
fps = 25; % frame rate
dt = 1e6/fps; 

pngFiles = dir(fullfile(dataFile,'*.png'));
numfiles = length(pngFiles);
dims = [584 388];
video = zeros(dims(1),dims(2),numfiles);

for i = 1:numfiles
    video(:,:,i) = imread(fullfile(dataFile,pngFiles(i).name))';
end

n = 3; % Factor of resolution reduction
dimsRed = [floor(dims(1)/n) floor(dims(2)/n)];
videoRed = zeros(dimsRed(1),dimsRed(2),numfiles);

% Get ground truth velocity
gt = readFlowFile(gtFrame);
vx = gt(:,:,1)';
vy = gt(:,:,2)';
vxRed = zeros(dimsRed(1),dimsRed(2));
vyRed = zeros(dimsRed(1),dimsRed(2));

% There are some unrealistically high (1e8) speeds that have to be
% filtered out.
for i = 1:dims(1)
    for j = 1:dims(2)
        if vx(i,j) > 100
            vx(i,j) = 0;
        end
        if vy(i,j) > 100
            vy(i,j) = 0;
        end
    end
end

% Downsample to appropriate resolution
ii = 1;
jj = 1;
for k = 1:numfiles
    for i = 1:n:dims(1)-n
        for j = 1:n:dims(2)-n
            videoRed(ii,jj,k) = sum(sum(video(i:i+n-1,j:j+n-1,k)))/(n*n);
            vxRed(ii,jj) = fps*sum(sum(vx(i:i+n-1,j:j+n-1)))/(n*n);
            vyRed(ii,jj) = fps*sum(sum(vy(i:i+n-1,j:j+n-1)))/(n*n);
            jj = jj+1;
        end
        jj = 1;
        ii = ii+1;
    end
    ii = 1;
end

% Save ground truth to mat file 
vxGT = vxRed';
vyGT = vyRed';
ts = [dt*numfiles/2 dt*(numfiles/2+1)]; % Timestamp of ground truth velocity at the central and next frame.
save(gtEvent,'vxGT','vyGT','ts')

contrast = diff(videoRed,1,3);

for k = 1:numfiles-1
    for i = 1:dimsRed(1)
        for j = 1:dimsRed(2)
            if log(abs(contrast(i,j,k))) > thr
                contrast(i,j,k) = sign(contrast(i,j,k));
            else contrast(i,j,k) = 0;
            end
        end
    end
end

dim = dimsRed(1)*dimsRed(2)*(numfiles-1);
x = zeros(dim,1);
y = zeros(dim,1);
t = zeros(dim,1);
p = zeros(dim,1);

ii = 1;
for k = 1:numfiles-1
    for i = 1:dimsRed(1)
        for j = 1:dimsRed(2)
            if contrast(i,j,k) ~= 0
                x(ii) = i;
                y(ii) = j;
                t(ii) = (k + rand)*dt;
                p(ii) = contrast(i,j,k);
                ii = ii+1;
            end
        end
    end
end

ind = find(p);
x = x(ind);
y = y(ind);
t = t(ind);
p = p(ind);

[t,I] = sort(t);
x = x(I);
y = y(I);
p = p(I);

for i = 1:size(p,1)
    if p(i) == -1
        p(i) = 0;
    end
end

polShift = 2048; % 2^11 
xShift = 4096; % 2^12
yShift = 4194304; % 2^22
sizeX = 240;
sizeY = 180;

addr = (dimsRed(2)-y)*yShift + (sizeX-x)*xShift + p*polShift;
saveaerdat([int32(t) uint32(addr)])
            
    