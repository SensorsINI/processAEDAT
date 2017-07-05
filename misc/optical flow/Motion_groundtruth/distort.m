function [X_pixel, Y_pixel] = distort(U, V, calibration_file)
%[X_pixel, Y_pixel, dX_pixeldt, dY_pixeldt] = distort_motion(U, V, dUdt, dVdt, calibration_file)
% 
% maps normalized undistorted image plane co-ordinates (U and V) and
% and normalized undistorted image plane velocities at those points (dUdt and dVdt)
% to the distorted pixel locations (X_pixel, Y_pixel) and distorted image
% plane velocities (dX_pixeldt and dY_pixeldt) using the calibration
% paramters in the file 'calibration_file'.
%
% LOCATION DISTORTION MODEL... mapping to pixel co-ordinates
% R^2 = U^2 + V^2;
% U_distorted = U * (1 + kc(1)*R^2 + kc(2)*R^4)      +      2*kc(3)*U*V + kc(4)*(R^2 + 2*U^2);
% V_distorted = V * (1 + kc(1)*R^2 + kc(2)*R^4)      +      kc(3)*(R^2 + 2*V^2) + 2*kc(4)*U*V;
%
% X_pixel = U_distorted*fc(1)+cc(1);
% Y_pixel = V_distorted*fc(2)+cc(2);
%
%
% VELOCITY DISTORTION MODEL... mapping to pixel co-ordinates
% dX_pixel/dt = (dU_distorted/dt)*fc(1)+cc(1);
% dY_pixel/dt = (dV_distorted/dt)*fc(2)+cc(2);
%
% dU_distorted/dt = (dU_distorted/dU) * (dU/dt) + (dU_distorted/dV) * (dV/dt)
% dV_distorted/dt = (dV_distorted/dU) * (dU/dt) + (dV_distorted/dV) * (dV/dt)
%
% dU/dt and dV/dt are input parameters which can be created using
% 'ground_truth'
%
% dU_distorted/dU, dU_distorted/dV, dV_distorted/dU, and dV_distorted/dV
% can be calculated from the equations for U_distorted and V_distorted as below
%
% dU_distorted/dU = (1 + kc(1)*(U^2+V^2) + kc(2)*(U^2+V^2)^2) + U*(kc(1)*(2*U) + kc(2)*(4*U^3 + 4*U*V^2)) + 2*kc(3)*V + kc(4)*(2*U + 4*U)
% dU_distorted/dV = U*(kc(1)*(2*V) + kc(2)*(4*V^3+4*U^2*V)) + 2*kc(3)*U + kc(4)*(2*V)
%
% dV_distorted/dU = V*(kc(1)*(2*U) + kc(2)*(4*U^3+4*U*V^2)) + kc(3)*(2*U)  + 2*kc(4)*V;
% dV_distorted/dV = (1 + kc(1)*(U^2+V^2) + kc(2)*(U^2+V^2)^2) + V*(kc(1)*(2*V) + kc(2)*(4*U^2*V + 4*V^3)) + kc(3)*(2*V + 4*V) + 2*kc(4)*U

%% load the calibration paramters
load(calibration_file);

%% calculate the distorted pixel co-ordinates of the normalized image plane points [U;V]
Rsquared = U.^2 + V.^2;
U_distorted = U.*(1 + kc(1).*Rsquared + kc(2).*Rsquared.^2)      +      2*kc(3).*U.*V + kc(4)*(Rsquared + 2*U.^2);
V_distorted = V.*(1 + kc(1).*Rsquared + kc(2).*Rsquared.^2)      +      kc(3)*(Rsquared + 2*V.^2) + 2*kc(4).*U.*V;
X_pixel = U_distorted*fc(1)+cc(1);
Y_pixel = V_distorted*fc(2)+cc(2);

end