function [Xpixel, Ypixel, dXpixel_dt, dYpixel_dt] = distort_motion(U, V, dUdt, dVdt, calibration_file)
%[Xpixel, Ypixel, dX_pixeldt, dY_pixeldt] = distort_motion(U, V, dUdt, dVdt, calibration_file)
% 
% maps normalized non-distorted image plane co-ordinates (U and V) and
% and normalized non-distorted image plane velocities at those points (dU_dt and dV_dt)
% to the distorted pixel locations (Xpixel, Ypixel) and distorted image
% plane velocities (dXpixel_dt and dYpixel_dt) using the calibration
% paramters in the file 'calibration_file'.
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
% 
% 
% LOCATION DISTORTION MODEL... mapping to pixel co-ordinates
% R^2 = U^2 + V^2;
% Udistorted = U * (1 + kc(1)*R^2 + kc(2)*R^4)      +      2*kc(3)*U*V + kc(4)*(R^2 + 2*U^2);
% Vdistorted = V * (1 + kc(1)*R^2 + kc(2)*R^4)      +      kc(3)*(R^2 + 2*V^2) + 2*kc(4)*U*V;
%
% Xpixel = Udistorted*fc(1)+cc(1);
% Ypixel = Vdistorted*fc(2)+cc(2);
%
%
% VELOCITY DISTORTION MODEL... mapping to pixel co-ordinates
% dXpixel/dt = (dUdistorted/dt)*fc(1)+cc(1);
% dYpixel/dt = (dVdistorted/dt)*fc(2)+cc(2);
%
% dUdistorted/dt = (dUdistorted/dU) * (dU/dt) + (dUdistorted/dV) * (dV/dt)
% dVdistorted/dt = (dVdistorted/dU) * (dU/dt) + (dVdistorted/dV) * (dV/dt)
%
% dU/dt and dV/dt are input parameters which can be created using
% 'ground_truth'
%
% dUdistorted/dU, dUdistorted/dV, dVdistorted/dU, and dVdistorted/dV
% can be calculated from the equations for Udistorted and Vdistorted as below
%
% dUdistorted/dU = (1 + kc(1)*(U^2+V^2) + kc(2)*(U^2+V^2)^2) + U*(kc(1)*(2*U) + kc(2)*(4*U^3 + 4*U*V^2)) + 2*kc(3)*V + kc(4)*(2*U + 4*U)
% dUdistorted/dV = U*(kc(1)*(2*V) + kc(2)*(4*V^3+4*U^2*V)) + 2*kc(3)*U + kc(4)*(2*V)
%
% dVdistorted/dU = V*(kc(1)*(2*U) + kc(2)*(4*U^3+4*U*V^2)) + kc(3)*(2*U)  + 2*kc(4)*V;
% dVdistorted/dV = (1 + kc(1)*(U^2+V^2) + kc(2)*(U^2+V^2)^2) + V*(kc(1)*(2*V) + kc(2)*(4*U^2*V + 4*V^3)) + kc(3)*(2*V + 4*V) + 2*kc(4)*U

%% load the calibration paramters
load(calibration_file);

%% use the "distort" function to calculate which pixels the image plane co-ordinates 'U' and 'V' will map to
[Xpixel, Ypixel] = distort(U, V, calibration_file);

%% calculate the distorted velocities in pixel co-ordinates from the normalized image plane velocities [dUdt, dVdt]
dUdistorted_dU = (1 + kc(1)*(U.^2+V.^2) + kc(2)*(U.^2+V.^2).^2) + U.*(kc(1)*(2.*U) + kc(2)*(4*U.^3 + 4*U.*V.^2)) + 2*kc(3).*V + kc(4)*(2.*U + 4.*U);
dUdistorted_dV = U.*(kc(1)*(2.*V) + kc(2)*(4.*V.^3+4*U.^2.*V)) + 2*kc(3).*U + kc(4)*(2.*V);

dVdistorted_dU = V.*(kc(1)*(2.*U) + kc(2)*(4*U.^3+4.*U.*V.^2)) + kc(3)*(2.*U) + 2*kc(4).*V;
dVdistorted_dV = (1 + kc(1)*(U.^2+V.^2) + kc(2)*(U.^2+V.^2).^2) + V.*(kc(1)*(2.*V) + kc(2)*(4*U.^2.*V + 4*V.^3)) + kc(3)*(2.*V + 4.*V) + 2*kc(4).*U;

dUdistorted_dt = (dUdistorted_dU).*(dUdt) + (dUdistorted_dV).*(dVdt);
dVdistorted_dt = (dVdistorted_dU).*(dUdt) + (dVdistorted_dV).*(dVdt);

dXpixel_dt = dUdistorted_dt*fc(1);
dYpixel_dt = dVdistorted_dt*fc(2);

end