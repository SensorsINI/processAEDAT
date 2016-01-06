function [timestamps,meanProcessingTimePacket,sizeIn,sizeOut,meanVx,sdGlobalVx,meanVy,sdGlobalVy,meanRotation,sdGlobalRotation] = getMotionStatistics(varargin)
    if nargin == 0
        [filename, pathname] = uigetfile('D:/Google Drive/Studium/Masterthese/Data/Statistics/*.txt');
        oldPath = cd;
        cd(pathname);
    else
        filename = varargin{1};
    end
    A = dlmread(filename,'',5,0);
    A(:,1) = A(:,1)/1e6;
    timestamps = A(:,1)-A(1,1);
    meanProcessingTimePacket = A(:,2);
%     sizeIn = A(:,3);
%     sizeOut = A(:,4);
%     meanVx = A(:,5);
%     sdGlobalVx = A(:,6);
%     meanVy = A(:,7);
%     sdGlobalVy = A(:,8);
%     meanRotation = A(:,9);
%     sdGlobalRotation = A(:,10);
    
    if nargin == 0
        cd(oldPath);
    end