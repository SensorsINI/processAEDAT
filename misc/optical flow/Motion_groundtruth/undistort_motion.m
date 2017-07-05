function [U, V, dU_dt, dV_dt] = undistort_motion(Xpixel, Ypixel, dXpixel_dt, dYpixel_dt, calibration_file)
%[U, V, dU_dt, dV_dt] = undistort_motion(Xpixel, Ypixel, dXpixel_dt, dYpixel_dt, calibration_file)
% 
% WARNING: Ideally a camera setup will have low distortion, which results 
% in dUdistorted_dV and dVdistorted_dU being zero or very small. This 
% function uses 1/dUdistorted_dV and 1/dVdistorted_dU and is thus very 
% sensitive to errors and even slight numerical approximations. 
% IT IS BEST NOT TO RELY ON THIS FUNCTION!
% 
% maps pixel co-ordinates (Xpixel, Ypixel) and normalized pixel velocities 
% at those points (dXpixel_dt and dYpixel_dt) to corresponding locations (U, V)
% and velocities (dU_dt, dV_dt) on the normalized image plane taking into 
% account distortion using the calibration paramters in the file 'calibration_file'.
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

warning('Ideally a camera setup will have low distortion, which results in dUdistorted_dV and dVdistorted_dU being zero or very small. This function uses 1/dUdistorted_dV and 1/dVdistorted_dU and is thus very sensitive to errors and even slight numerical approximations. It is best not to rely on this function!');

%% load the calibration paramters
load(calibration_file);

%% use the "undistort" function to calculate which image plane co-ordinates the pixels 'X_pixel', 'Y_pixel' will map to
[U, V] = undistort(Xpixel, Ypixel, calibration_file);

%% calculate the undistorted velocities on the normalized image plane [dUdt, dVdt] from the pixel velocities
dUdistorted_dt = dXpixel_dt/fc(1);
dVdistorted_dt = dYpixel_dt/fc(2);

dUdistorted_dU = (1 + kc(1)*(U.^2+V.^2) + kc(2)*(U.^2+V.^2).^2) + U.*(kc(1)*(2.*U) + kc(2)*(4*U.^3 + 4*U.*V.^2)) + 2*kc(3).*V + kc(4)*(2.*U + 4.*U);
dUdistorted_dV = U.*(kc(1)*(2.*V) + kc(2)*(4.*V.^3+4*U.^2.*V)) + 2*kc(3).*U + kc(4)*(2.*V);

dVdistorted_dU = V.*(kc(1)*(2.*U) + kc(2)*(4*U.^3+4.*U.*V.^2)) + kc(3)*(2.*U) + 2*kc(4).*V;
dVdistorted_dV = (1 + kc(1)*(U.^2+V.^2) + kc(2)*(U.^2+V.^2).^2) + V.*(kc(1)*(2.*V) + kc(2)*(4*U.^2.*V + 4*V.^3)) + kc(3)*(2.*V + 4.*V) + 2*kc(4).*U;

dU_dt = (1./dUdistorted_dU).*dUdistorted_dt + (1./dVdistorted_dU).*dVdistorted_dt;
dV_dt = (1./dUdistorted_dV).*dUdistorted_dt + (1./dVdistorted_dV).*dVdistorted_dt;
end