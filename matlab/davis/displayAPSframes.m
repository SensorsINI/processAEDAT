function displayAPSframes(frames, time_interval)
% diplay frames with a fixed time interval
%   inputs:
%       frames -> required. It is obtained from getAPSframesDavisGS
%       time_interval  -> optional param. time interval between frames
%
%   author federico.corradi@inilabs.com

    if nargin < 2
       time_interval = 0.1
    end

    [chan, x, y, numFrames] = size(frames);     %get infos on frames
    bw_cdsSignal = 3;                           %here are stored the bw values (resetbuffer - readbuffer)
    max_gray = 512;                             %constant?
    
    imshow(rot90(squeeze(frames(bw_cdsSignal,:,:,1))),[0,max_gray]);
    hold on
    for i=1:numFrames
        %check cdsSignal is non negative
        index_neg = frames(bw_cdsSignal,:,:,i) < 0;
        frames(bw_cdsSignal(index_neg),:,:,i) = 0;          %set cdsSignal = 0 if neg
        %all your other code here
        imshow(rot90(squeeze(frames(bw_cdsSignal,:,:,i))),[0,max_gray]);
        pause(time_interval);
    end

end
