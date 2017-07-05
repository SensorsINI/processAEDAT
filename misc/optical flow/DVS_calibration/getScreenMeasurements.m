function [pix_SS, mm_SS] = getScreenMeasurements()
% [pix_SS, mm_SS] = getScreenMeasurements()
% 
% Determines the size of your screen in units of pixels and millimeters.
% Based on Matlab answer here:
% http://www.mathworks.com/matlabcentral/answers/100792-in-matlab-how-do-i-obtain-information-about-my-screen-resolution-and-screen-size
% 
% If you have multiple different screens, make sure it is measuring the
% correct screen!
% 
% RETURNS:
% 'pix_SS' = [pix_x, pix_y]
% The horizontal (pix_x) and vertical (pix_y) size of the screen in units of pixels
% 
% 'mm_SS' = [mm_x, mm_y]
% The horizontal (mm_x) and vertical (mm_y) size of the screen in units of
% millimeters
% 
% 
% written by Garrick Orchard - June 2015
% garrickorchard@gmail.com

%Sets the screen units to pixels
set(0,'units','pixels');

%Get the screen size in pixels
pix_SS = get(0,'screensize');
pix_SS = pix_SS(3:4);

%Sets the screen units to centimeters
set(0,'units','centimeters');

%Get the screen size in centimeters
cm_SS = get(0,'screensize');

mm_SS = 10*cm_SS(3:4);

% %Calculates the resolution (pixels per inch)
% Res = Pix_SS./Inch_SS

