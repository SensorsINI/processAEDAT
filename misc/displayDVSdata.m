function [output] = displayDVSdata(x, y, pol, ts, varargin)
%displayDVSdata allows to display dvs data recorded with DAVIS (AEDAT 1.0/2.0).
%4 required inputs are the outputs the getDVSeventsDavis:
%   x = column vector which contains the x addresses of the DVS events
%   y = column vector which contains the y addresses of the DVS events
%   pol = column vector which contains the polarity values of the DVS events
%   ts = column vector which contains the timestamps of the DVS events
%
%Optional arguments can be entered using the format
%displayDVSdata(x,y,pol,ts,'mode', 'scattered', 'sensor', 'DAVIS240','fps',
%200, 'epg', 10000). 
%For more information check the inputParser class on the Mathworks website.
%
%Optional parameters:
%   mode = two types of representation are available:
%           - scattered: data are plotted using the scatter3 matlab function.
%             Pictures are generated in the working folder. By default 20000 events are displayed
%             in each graph.
%
%           - frame: DVS events are rearranged in a 4-D matrix (RGB frames). A video is
%             generated using immovie and implay.
%
%   sensor = it defines the resolution of the video\graph. Currently the
%            following sensors are supported: 
%            DVS128,DAVIS240,DAVIS346,DAVIS640
%
%   fps (frames per second) = it is associated with the frame mode. It 
%         represents the "assumed" frame speed and it is used to determine 
%         the number of frames used to display data.
%
%   epg (events per graph) = it is associated with the scatterd mode. It
%         represents the number of events displayed in each image.
%The output:   
%           - Scattered mode = 1;
%           - Frame mode = movie structure array;
%           - Wrong argument for the type of representation =0;
%Author: Andrea Palombi K1348999@kingston.ac.uk
%Date: 19/04/2016

% inputParser class is used to manage the arguments of the function 
p = inputParser;

%Parameters associated with the optional arguments
defaultMode = 'frame';
validModes = {'frame','scattered'};
checkMode = @(x) any(validatestring(x,validModes));

defaultSensor = 'DAVIS240';
validSensors = {'DVS128','DAVIS240','DAVIS346','DAVIS640'};
checkSensor = @(x) any(validatestring(x,validSensors));

defaultFPS = 60;
checkFPS = @(x) isinteger(x) && (x>0);

defaultEPG = 20000;
checkEPG = @(x) isinteger(x) && (x>0);

%Required arguments 
addRequired(p,'x');
addRequired(p,'y');
addRequired(p,'pol');
addRequired(p,'ts');
%Optional arguments
addOptional(p,'mode',defaultMode,checkMode);
addOptional(p,'sensor',defaultSensor,checkSensor);
addOptional(p,'fps',defaultFPS, checkFPS);
addOptional(p,'epg',defaultEPG, checkEPG);

parse(p,x,y,pol,ts,varargin{:});

%it displays the arguments for which default values are used
if ~isempty(p.UsingDefaults)
   disp('Using defaults: ')
   disp(p.UsingDefaults)
end

%events are divided depending on their polarity 
logical_pol = logical(pol);
                
x_incr = x(logical_pol);
y_incr = y(logical_pol);
ts_incr = ts(logical_pol);

x_decr = x(~logical_pol);
y_decr = y(~logical_pol);
ts_decr = ts(~logical_pol);

if strcmpi(p.Results.sensor, 'DAVIS240')
    res_x = 240;
    res_y = 180;
elseif strcmpi(p.Results.sensor, 'DVS128')
    res_x = 128;
    res_y = 128;
% additional conditions need to be added for DAVIS346, DAVIS640
end

%scattered representation   
if strcmpi(p.Results.mode, 's') || strcmpi(p.Results.mode, 'scattered')    
    work_in_progress = 0;
    for i=ts(1):p.Results.epg:ts(end)
        if work_in_progress==0;
            fprintf('Images are being generated, please wait\n');
            work_in_progress=1;
        end
        fprintf('...');
        %it generates a figure element which is not displayed
        figure('name', 'DVS Scattered Data','Visible','off')
        %it creates a mask to identify the events with polarity = 1, in the 
        %time interval we are going to represent
        incr_mask = ts_incr >= i & ts_incr < i+p.Results.epg;
        %It plots events with polarity = 1
        scatter3(x_incr(incr_mask), ts_incr(incr_mask), y_incr(incr_mask), 1, 'g');
        hold on
        %it creates a mask to identify the events with polarity = 0, in the 
        %time interval we are going to represent
        decr_mask = ts_decr >= i & ts_decr < i+p.Results.epg;
        %It plots events with polarity = 0
        scatter3(x_decr(decr_mask), ts_decr(decr_mask), y_decr(decr_mask), 1, 'r');
        %axes formatting
        axis([0 res_x i i+p.Results.epg-1 0 res_y]);
        strx = sprintf('X Pixel [0 %f]',res_x);
        xlabel(strx);
        ylabel('Timestamps [\mus]');
        strz = sprintf('Y Pixel [0 %f]',res_y);
        zlabel(strz);
        %The graph is saved in the working folder
        filename = ['DVS ' num2str(i) ' to' num2str(i+19999) ' microseconds.jpg'];
        saveas(gcf, filename);
    end
    fprintf('\nImages have been successfully generated\n');
    output = 1;
%frame representation    
elseif strcmpi(p.Results.mode, 'f') || strcmpi(p.Results.mode, 'frame')
    %time interval in seconds
    delta_t = double(ts(end)-ts(1))/1000000;
    %assuming 60FPS (rounded up to the next integer) we determine how many 
    %frames do we need to represent our dvs events
    n_frames = ceil(p.Results.fps*delta_t); 
    %4-D array is generated for the video (first 3 dimensions = RGB image)
    dvs_frames = zeros(res_x,res_y,3,n_frames);
    loop_limit = max(length(x_incr),length(x_decr));    
    for i = 1:loop_limit
        if i<= length(x_incr)
            %coefficient required to associate an event with a frame
            frame_incr = ceil((double(ts_incr(i)-ts(1)))/((double(ts(end)-ts(1)))/n_frames));
            if frame_incr == 0
                frame_incr = 1;
            end
            dvs_frames(x_incr(i)+1,y_incr(i)+1,2,frame_incr) = 255;
        end
        if i<= length(x_decr)
            frame_decr = ceil((double(ts_decr(i)-ts(1)))/((double(ts(end)-ts(1)))/n_frames));
            if frame_decr == 0
                frame_decr = 1;
            end
            dvs_frames(x_decr(i)+1,y_decr(i)+1,1,frame_decr) = 255;
        end
    end
    %movie structure array
    output = immovie(rot90(dvs_frames));
    implay(output);
end %if condition to choose the type of plot

if nargout == 0
    assignin('base','output',output);
end
end %function end
   
 