function retmovie(outFileName, varargin)
%RETMOVIE Create an .avi file from tmpdiff128 AER events
%   RETMOVIE(FILENAME) creates an .avi file with the default parameter
%   values. If FILENAME does not include an extension, then '.avi' will be
%   used.
%
%   RETMOVIE(FILENAME,'PropertyName',VALUE,'PropertyName',VALUE,...)
%   creates the movie with the specified property values.
%
%   RETMOVIE parameters
%
%   FPS - The frames per second for the AVI movie. This parameter
%   must be set before using ADDFRAME. The default is 15 fps.
%
%   PLAYRATE - A multiplier that controls the ration between real time and
%   movie time.
% 
%   COMPRESSION - A string indicating the compressor to use. Default is
%   'None'. Valid values for this parameter on Windows are 'Indeo3',
%   'Indeo5', 'Cinepak', 'MSVC', 'RLE' or 'None'. To use a custom
%   compressor, the value can be the four character code as specified by
%   the codec documentation.
%
%   BGCOLOR - The background color of the movie, given in a 3-element RGB
%   array. Default is black.
%     
%   DATFILENAME - The file name  of the .dat file to load. If not
%   specified, a selection dialog will open.
%     
%   MIXONOFF - A true/false flag that if true with add the values of
%   ONCOLOR and OFFCOLOR when both an on and off event occurs in the same
%   frame.
% 
%   OFFCOLOR - The color of off events, in RGB. Default is red.
% 
%   ONCOLOR - The color of on events, in RGB. Default is green.
% 
%   QUALITY - A number between 0 and 100. This parameter has no effect on
%   uncompressed movies. This parameter must be set before using ADDFRAME.
%   Higher quality numbers result in higher video quality and larger file
%   sizes, where lower quality numbers result in lower video quality and
%   smaller file sizes. The default is 100, which still looks bad.
% 
%   VIDEOPREVIEW - A true/false flag that controls whether or not the video
%   preview window and statusbar appear. Defailt is true.

%   Coded by Ross Maddox
%   $Revision: 1.0 $  $Date: 2007/07/22 16:19:07 $

% set default values
bgColor = [0; 0; 0];
compression = 'none';
fps = 30;
datFileName = [];
mixOnOff = true;
offColor = [1; 0; 0];
onColor = [0; 1; 0];
playRate = 1;
quality = 75;
videoPreview = true;

% add .avi extension if necessary
if ~strcmp(outFileName((end - 3):end), '.avi')
    outFileName = [outFileName '.avi'];
end

% parse properties
if nargin > 1
    for arg = 1:2:(nargin - 1)
        switch lower(varargin{arg})
            case 'bgcolor'
                bgColor = varargin{arg + 1}(:);
            case 'compression'
                compression = varargin{arg + 1};
            case 'datFileName'
                datFileName = varargin{arg + 1};
            case 'fps'
                fps = varargin{arg + 1};
            case 'mixonoff'
                mixOnOff = varargin{arg + 1};
            case 'offcolor'
                offColor = varargin{arg + 1}(:);
            case 'oncolor'
                onColor = varargin{arg + 1}(:);
            case 'playrate'
                playRate = varargin{arg + 1};
            case 'quality'
                quality = varargin{arg + 1};
            case 'videopreview'
                videoPreview = varargin{arg + 1};
            otherwise
                error('Invalid property. Type ''help makeMovieFromRetinaEvents''for the controllable properties.');
        end
    end
end

% read AER data
if isempty(datFileName)
    [a, t] = loadaerdat();
else
    [a, t] = loadaerdat(datFileName);
end
[x, y, pol] = extractRetina128EventsFromAddr(a);
x = x+ 1;
y = y + 1;
t = double(t);
width = 128;
height = 128;
% I had problems with controllalbe size, so it is fixed at 128x128 for now.

timeStep = 1/fps*1e6*playRate; % in us

delete(outFileName);
mov = avifile(outFileName, 'fps', fps, 'compression', compression, 'quality', quality);

try
    frameCount = 0;
    % the value of totalFrames is not right for some reason. This messes up
    % the progress bar, but it's usually the case that it finishes "early."
    totalFrames = ceil((t(end) - t(2))/timeStep);
    mat = zeros(128, 128, 3);
    mat(:,:,1) = bgColor(1); mat(:, :, 2) = bgColor(2); mat(:, :, 3) = bgColor(3);

    if videoPreview
        f = figure('name', 'Preview', 'menubar', 'none', 'dockcontrols', 'off', 'numbertitle', 'off', 'color', [0 0 0], 'position', [400 400 width height]);
    end

    for i = 2:length(t)
        if mod(t(i), timeStep) - mod(t(i - 1), timeStep) >= 0
            mat(128 - y(i) + 1, x(i), :) = (pol(i) > 0)*onColor + (pol(i) < 0)*offColor + squeeze(sum(squeeze(mat(128 - y(i) + 1, x(i), :)) ~= squeeze(bgColor))*mixOnOff*mat(128 - y(i) + 1, x(i), :));
        else
            mat = min(mat, 1);
            mov = addframe(mov, mat);
            if videoPreview
                figure(f)
                mat((height - 1):height, 1:ceil(width*frameCount/totalFrames), :) = 1;
                image(mat)
                axis off image
                set(gca, 'position', [0 0 1 1])
                drawnow
            end

            mat(:,:,1) = bgColor(1); mat(:, :, 2) = bgColor(2); mat(:, :, 3) = bgColor(3);
            frameCount = frameCount + 1;
        end
    end

    if videoPreview
        close(f);
    end
    mov = close(mov);
catch
    warning('off', 'MATLAB:aviclose:noAssociatedFrames')
    mov = close(mov);
    warning('on', 'MATLAB:aviclose:noAssociatedFrames')
    if exist('f', 'var')
        close(f)
    end
    rethrow(lasterror);
end