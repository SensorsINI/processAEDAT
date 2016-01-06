function [U, V] = undistort(X_pixel, Y_pixel, calibration_file)
%[U, V] = undistort(X_pixel, Y_pixel, calibration_file)
% 
% Uses the calibration parameters in the file "calibration_file" to map the pixel
% co-ordinates [X_pixel, Y_pixel] to their corresponding locations on the
% normalized undistorted image plane [U, V] (i.e. lens distortion is
% accounted for by this function).
%
% The calibration file can be generated using the Caltech Camera
% Calibration Toolbox available from http://www.vision.caltech.edu/bouguetj/calib_doc/index.html
% See the toolbox documentation for more information on the distortion
% model and calibration parameters.
% 
% For DVS calibration using the Caltech Toolbox, see
% http://www.garrickorchard.com/code/dvs-calibration
% 
% written by Garrick Orchard - October 2015
% garrickorchard@gmail.com

if ~exist('normalize.m', 'file')
    error('This function relies on the Caltech Camera Calibration Toolbox, please make sure it is on your path. The toolbox can be obtained from http://www.vision.caltech.edu/bouguetj/calib_doc/index.html');
    return;
end
%% load the calibration paramters
load(calibration_file); 

%% find the location of the pixel co-ordinate on the normalized image plane, taking into account distortion
% the "normalize" function is in the Caltech Camera Calibration Toolbox
undistorted_coordinates = normalize([X_pixel(:)';Y_pixel(:)'],fc,cc,kc,alpha_c);
U = undistorted_coordinates(1,:);
V = undistorted_coordinates(2,:);

%% reshape the output matrices to match the shape of the inputs
U = reshape(U, size(X_pixel));
V = reshape(V, size(X_pixel));
end