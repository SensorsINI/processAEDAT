% Horn Schunck algorithm based on events
% Author: Min Liu         
% This algorithm is based on classic Horn Schunck based on frames, it is
% implemented on DAVIS just using the events. 
%
% Horn Schunck is a dense
% optical flow algorithms, compared with LK, it can make the get the more
% accurate and more smooth optical flow field. It's a global algorithms
% also menas that it will take more expensive compute cost than KL. Thanks
% to the DVS camera, the tradeoff between the global algorithms and the compute cost
% can get to a high level. The reason is that in event_based HS algorithm,
% we can know the addresses of the intensity-changed pixels very well which
% is very hard for the frame-based camera, so we just need to calculate
% these events and the compute cost is not very expensive again.
%
% References:
% 1. Horn, B.K.P., and Schunck, B.G., Determining Optical FlowDetermining Optical Flow 
% 2. Bodo Rueckauer and Tobi Delbruck, Evaluation of event-based algorithms for
%    optical flow with ground-truth from inertial measurement sensor
% 3. Xavier Clady, Charless Clercq, et al., Asynchronous Visual event-based time-to-contact
% 4. Tobias Brosch, Stephan Tschechne, et al., On event-based optical flow detection
% 5. Ryad Benosman, Charles Clercq, et al., Event-Based Visual Flow
% 6. The matlab source code of frame-based HS by Mohd Kharbat at Cranfield Defence and Security
% December 2015
%
% Notice:  This version is still under test, it may not be stable. If you
% have any questions, please don't hesitate to contact the author.
% Email: minliu@ini.uzh.ch

%% clear all the valuse
clear all
clear

load('dataset.mat')   % The dataset will be test, from Bodo
load mri

t = rot_bars_real(:,4);
x = rot_bars_real(:,1);
y = rot_bars_real(:,2);

%% calcuate the optical flow
t_tmp = t(1);
im1 = im2uint16(zeros(240, 180));    % get the first image
im2 = im2uint16(zeros(240, 180));    % get the second image
movie = im2uint8(zeros(180,240,1,100));
frame_count = 1;

for i=1:1000
    if t(i) - t_tmp < 1000           % set the update interval to 1000us, i.e. 1ms
        im2(x(i), y(i)) = im2(x(i), y(i)) + 1;    
    else
        im2(x(i), y(i)) = im2(x(i), y(i)) + 1;  
        t_tmp = t(i);
        HS_Framebased(im1', im2');
        %movie(:,:,1,frame_count) = im2uint8(HS(im1', im2'));

        frame_count = frame_count + 1;
        im1 = im2;
    end
end

%%  play the video
%mov = immovie(movie,map);
%implay(mov);