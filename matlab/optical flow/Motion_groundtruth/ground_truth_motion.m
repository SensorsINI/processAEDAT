function [dU_dt, dV_dt] = ground_truth_motion(U, V, omega, T, Z)
% function [dU_dt, dV_dt] = ground_truth_motion(U, V, omega)
% or with optional translational motion:
% function [dU_dt, dV_dt] = ground_truth_motion(U, V, omega, T, Z)
% 
% 
% TAKES IN
% U:    'x' co-ordinates on the non-distorted and normalized image plane (U = X/Z)
% 
% V:    'y' co-ordinates on the non-distorted and normalized image plane (V = Y/Z)
% 
% omega = [omega_x, omega_y, omega_z]: a vector of the rotational
%       velocities in radians/second describing rotation of the camera 
%       itself around the no-parallax point (the point around which 
%       rotation causes no depth parallax)
%  
% note that [U=0, V=0] is the principal point (the variable 'cc' calculated
% by the camera calibration toolbox
% http://www.vision.caltech.edu/bouguetj/calib_doc/htmls/parameters.html typically near the middle of the image)
%  
% T = [T_x, T_y, T_z]: a vector of the translational velocity of the sensor
%       in units matching the units of depth (per second). 'T' is optional,
%       but if included it must be accompanied by 'Z'
% 
% Z:    The same size as 'U' and 'V' indicating the individual depth for
%       each point on the image plane [U,V]. 'Z' is an optional parameter,
%       only required if 'T' is used.
%  
% RETURNS
% dU_dt: x-direction velocities at the normalized image plane locations given as input
% 
% dV_dt: y-direction velocities at the normalized image plane locations given as input
% 
% co-ordinate axes are as defined in 
% Orchard, G.; and Etienne-Cummings, R. “Bioinspired Visual Motion Estimation” Proceedings of the IEEE, vol.102, no.10, pp.1520–1536, Oct. 2014.
% also available from http://arxiv.org/abs/1511.00096
% 
% written by Garrick Orchard - October 2015
% garrickorchard@gmail.com


omega_x = omega(1);
omega_y = omega(2);
omega_z = omega(3);

if nargin == 3
    dU_dt = - omega_y + omega_z.*V + omega_x.*U.*V - omega_y.*(U.^2);
    dV_dt = + omega_x - omega_z.*U - omega_y.*U.*V + omega_x.*(V.^2);

elseif nargin ==5
    T_x = T(1);
    T_y = T(2);
    T_z = T(3);    
    dU_dt = (T_z.*U-T_x)./Z - omega_y + omega_z.*V + omega_x.*U.*V - omega_y.*(U.^2);
    dV_dt = (T_z.*V-T_y)./Z + omega_x - omega_z.*U - omega_y.*U.*V + omega_x.*(V.^2);
end