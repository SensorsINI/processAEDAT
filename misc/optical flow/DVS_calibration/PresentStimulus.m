function rectangleSize_mm = PresentStimulus(num_rectangles, num_flashes)
% blocksize_mm = PresentStimulus(num_rectangles, num_flashes)
% Creates and presents a checkerboard calibration pattern on the screen.
%
% TAKES IN:
% 'num_rectangles' = [num_rectanglesX; num_rectanglesY]
% A 2x1 vector containing the number of rectangles to display
% in the horizontal and vertical directions respectively
%
% 'num_flashes'
% Dictates how many times the stimulus will be flashed on the
% screen. A negative or zero value creates a static stimulus (if non-DVS
% calibration is to be used). If this paramter is omitted,
% 'num_flashes = 0' is assumed (useful for ATIS or DAVIS calibration using
% snapshot/APS functionality instead of DVS).
%
%
% RETURNS:
% 'rectangleSize_mm' = [size_x, size_y]
% The horizontal (size_x) and vertical (size_y) size of the rectangles displayed
% on the screen, in units of millimeters. This paramter is required for
% calibration using the Caltech Camera Calibration Toolbox available from:
% http://www.vision.caltech.edu/bouguetj/calib_doc/index.html
%
%
% EXAMPLE USE:
% rectangleSize_mm = PresentStimulus([10,10], 0); %display static image
% rectangleSize_mm = PresentStimulus([10,10], 10); %flash ten times
%
% written by Garrick Orchard - June 2015
% garrickorchard@gmail.com

close all;
figure(1)

%% check if the 'num_flashes' variable was passed
if ~exist('num_flashes', 'var')
    num_flashes = 0;
end

%% Obtains the screen size information and use it to determine the rectangle size
[Screen_size_pixels, Screen_size_mm] = getScreenMeasurements();

%fixed parameters of the setup
figure_borderSize = 150; %leave space of 150 pixels on each side of the axes for the figure controls etc
image_borderSize = 10; %within the image, create a border of size 10 pixels to ensure contrast with the outside rectangles

%How big is each rectangle in units of pixels?
rectangleSize_pixels = floor((Screen_size_pixels - 2*(figure_borderSize+image_borderSize))./num_rectangles);

%How big is each rectangle in units of millimeters?
rectangleSize_mm = Screen_size_mm.*rectangleSize_pixels./Screen_size_pixels;

%How big is the checkered part of the image
image_inner_dim = num_rectangles.*rectangleSize_pixels; % the dimenstion of the inside of the image (not including the border)

%Create a black image to fit both the checkerboard and the image border
imgTemplate = zeros(image_inner_dim+2*image_borderSize);

%% create the checkerboar image
img = imgTemplate;
for x = 1:num_rectangles(1)
    for y = (1+rem(x+1,2)):2:num_rectangles(2)
        xloc = image_borderSize + ((1+(x-1)*rectangleSize_pixels(1)):(x*rectangleSize_pixels(1)));
        yloc = image_borderSize + ((1+(y-1)*rectangleSize_pixels(2)):(y*rectangleSize_pixels(2)));
        img(xloc,yloc) = 1;
    end
end

%% display
imshow(img');

if num_flashes>1
    input('Press any button to begin flashing...\n');
    figure(1) %bring the figure to the front (if it is not already in front)
    pause(1) %small pause
    
    % flash 'num_flashes' times
    for i = 1:num_flashes
        imshow(imgTemplate')
        drawnow;
        imshow(img')
        drawnow;
    end
end