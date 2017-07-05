function [images, tuv] = read_image_flow_tune_para_3D(iFile, iStart, iEnd, varargin)

% function [images, tuv] = read_image_flow_tune_para_3D(iFile, nframes, varargin)

% read_image_flow_tune_para reads in two pairs of frames and ground truth
% optical flow specific to the file location in Deqing Sun's computer
% these image and flow are selected to represent various scenes

% if nargin <= 1;
%     nframes = 3;
% end;

% long Urban sequences

switch iFile
    case num2cell([1:8]) 

        iStart = max(iStart, 7);
        iEnd   = min(14, iEnd);
        
%         iStart = max(10 - floor(nframes/2), 7);
%         iEnd   = min(14, iStart+nframes-1);
      
        images = [];
        for i = iStart:iEnd-1
            [im1, im2, tu, tv] = read_image_flow('middle-other-3D', 1, iFile, i);            
            %images{i-iStart+1} = im1;
            images  = cat(4, images, im1);
            tuv{i-iStart+1}    = cat(3, tu, tv);
        end;      
        %images{iEnd-iStart+1} = im2;
        images  = cat(4, images, im2);
        tuv{iEnd-iStart+1}    = nan;
        
    case 9 %'no country for old man'
        
        iStart = max(iStart, 1);
        iEnd   = min(60, iEnd);        
        fndir = '/home/dqsun/Desktop/video_segmentation/video_segmentation/images/nocountryforoldmen/';
        
        images = [];
        for i = iStart:iEnd
            im1 = imread([fndir sprintf('frame_%04d.png', i)]);
            %images{i-iStart+1} = im1;
            images  = cat(4, images, im1);
            tuv{i-iStart+1}    = nan;
        end;              
        
    case 22 % hand
        [im1, im2, tu, tv] = read_image_flow_tune_para(22,1);
        images  = cat(4, im1, im2);
        tuv{1}  = cat(3, tu, tv);
        
    case 10 % flower garden
        [im1, im2, tu, tv] = read_image_flow_tune_para(28,1);
        images  = cat(3, im1, im2);
        tuv{1}  = cat(3, tu, tv);
        
    case 30  % hand reduce by half
        [im1, im2, tu, tv] = read_image_flow_tune_para(22,1);
        
        im1 = imresize(im1, 0.5);
        im2 = imresize(im2, 0.5);
        tu = imresize(tu, 0.5)/2;
        tv = imresize(tv, 0.5)/2;
        
        images  = cat(4, im1, im2);
        tuv{1}  = cat(3, tu, tv);
        
        
    otherwise
        error('read_image_flow_tune_para_3D: incorrect input file number %d!', iFile);
end;        
% for i = 1:nframes
%     %[im1, im2, tu, tv] = read_image_flow('middle-other', 1, 8+i);    
%     [im1, im2, tu, tv] = read_image_flow('urban', 1, 1, 8+i); 
%     images{i} = cat(4, im1, im2);
%     tuv{i}    = cat(3, tu, tv);
% end;
%     
