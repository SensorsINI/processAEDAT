clearvars;

addpath('D:/Google Drive/Studium/Masterthese/Code/jAER-sensors/scripts/matlab');
addpath('D:/Google Drive/Studium/Masterthese/Code/jAER-sensors/scripts/matlab/davis');
addpath('D:/Google Drive/Studium/Masterthese/Code/MATLAB/frame-based flow estimation/ijcv_flow_code');
addpath('D:/Google Drive/Studium/Masterthese/Code/MATLAB/frame-based flow estimation/ijcv_flow_code/utils');
addpath('D:/Google Drive/Studium/Masterthese/Code/MATLAB/frame-based flow visualization');
frameDataFile = 'D:/Google Drive/Studium/Masterthese/Data/logged samples/IMU_APS/IMU_pan_boxes_APS.aedat';
gtDataFile = 'D:/Google Drive/Studium/Masterthese/Data/logged samples/IMU_APS/flowExport_pan_boxes.mat';

% Load image sequence
frames = getAPSframesDavisGS(frameDataFile);
im1 = flipud(squeeze(frames(3,:,:,7))');
im2 = flipud(squeeze(frames(3,:,:,8))');
fps = mean(1e6/diff(frames(5,1,end,:),1,4)); % mean frame rate
firstTs = frames(5,1,end,7); % first timestamp of first frame
lastTs = frames(5,end,1,8); % last timestamp of next frame

% Load ground truth
load(gtDataFile);
uvGT(:,:,1) = -flip(vx);
uvGT(:,:,2) = -flip(vy);

% Compute flow vectors
uv = zeros(size(uvGT));
uv(1:end-1,1:end-1,:) = estimate_flow_interface(im1, im2, 'classic+nl-fast');

% Plot image sequence and flow fields
figure; 
subplot(3,2,1);
imshow(mat2gray(im1));
title('Image 1');
subplot(3,2,2);
imshow(mat2gray(im2));
title('Image 2');
subplot(3,2,3);
plotflow(uv);
title('Measured flow');
subplot(3,2,4);
plotflow(uvGT);
title('Ground truth');
subplot(3,2,5);
imshow(flowToColor(uv))
title('Measured flow');
subplot(3,2,6);
imshow(flowToColor(uvGT))
title('Ground truth');

% Compute error statistics
[aae, stdae, aepe, stdepe] = flowAngErrUV(uvGT, uv, 0)
aepe = aepe/fps
stdepe = stdepe/fps