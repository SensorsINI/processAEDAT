%% An example of how account for camera calibration in optical flow
% 
% This work relies heavily on the Calibration Toolbox available from 
% http://www.vision.caltech.edu/bouguetj/calib_doc/index.html
% See the toolbox documentation for more information on the distortion
% model and calibration parameters. 
% 
% For DVS calibration using the Caltech Toolbox, see
% http://www.garrickorchard.com/code/dvs-calibration
% 
% written by Garrick Orchard - October 2015
% garrickorchard@gmail.com

%% load the calibration file created by the Caltech Camera Calibration Toolbox
calibration_file = 'example_Calib_Results.mat'; % an example of a camera calibration file
load(calibration_file);

%% define the pixel co-ordinates at which you want to estimate velocity.
% Remember to start at pixel [0,0] not [1,1] to comply with the Caltech
% Camera Calibration Toolbox convention
% 
% X_pixel and Y_pixel can have arbitrary size and shape (but must have the same size and 
% shape as each other)
% 
% X_pixel and Y_pixel are pixel locations after lens distortion 
sensor_size = [304,240]; %size of the sensor in pixels
[X_pixel, Y_pixel] = meshgrid(0:sensor_size(1)-1, 0:sensor_size(2)-1); 

%% convert the distorted pixel co-ordinates to normalized undistorted image plane co-ordinates
[U, V] = undistort(X_pixel, Y_pixel, calibration_file);

%% define the rotation of the sensor 
% omega = [omega_x, omega_y, omega_z] 
% A right handed rotation convention in radians per second
omega = [0 0 1];

%% calculate the velocity at the normalized undistorted image plane co-ordinates determined above
% pure rotation
[dU_dt, dV_dt] = ground_truth_motion(U, V, omega);

% % or pure translation, but this requires scene depth (Z) to be known for every point on the image plane
% % mixtures of rotation and translation can also be used
% T = [1,0,0]; %camera moving in Z direction at 1m/s
% omega = [0,0,0];
% Z = 5*ones(size(U)); %camera viewing a flat plane at distance of 5m
% [dU_dt, dV_dt] = ground_truth_motion(U, V, omega, T, Z);
%% re-apply the distortion to both the pixel locations and the motion to obtain ground truth estimates of motion 
% We assume that the motion algorithm to be tested does not account for distortion.
% Therefore, the algorithm output will be distorted, and should ideally
% match the distorted (not undistorted) ground truth.
% 
% Image motion varies as a function of location within the image plane. 
% For this reason, the undistorted image plane locations 'U' and 'V' 
% (corresponding to the distorted 'Xpixel' and 'Ypixel' locations) are used to determine the correct locations 
% at which theoretical image motion should be calculated for each pixel.
% 
% Distortion also "stretches" and "squashes" parts of the image, thus the
% image motion needs to be re-distorted to match what we expect the
% imperfect camera and lens to observe
[Xpixel, Ypixel, dXpixel_dt, dYpixel_dt] = distort_motion(U, V, dU_dt, dV_dt, calibration_file);


%% display the results
% display the motion (taking into account distortion) that should be measured at each pixel
quiver(Xpixel, Ypixel, dXpixel_dt, dYpixel_dt);
axis ij image %get the axis directions correct
title('motion field (pixels per second)')
xlabel('X location (pixels)')
ylabel('Y location (pixels)')

% to display the undistorted image motion at the normalized image plane
% locations, you could instead use the lines below
% units are scaled by the physical pixel size (30e-6 for ATIS)
% quiver(U_normalized, V_normalized, dUdt, dVdt);
% axis ij image %get the axis directions correct
% title('motion field (pixels per second)')
% xlabel('X location (pixels)')
% ylabel('Y location (pixels)')


%% Take into account lens distortion when calculating optical flow
% Two possible methods. 
% 
% 1: Apply distortion to the pixel locations before running the optical
% flow algorithm. This is the preferred method. Pseudo code below
% 
% load(calibration_file);
% [U, V] = undistort(TD.x, TD.y, calibration_file);
% TDundistorted.x = U*fc(1) + cc(1);
% TDundistorted.y = V*fc(2) + cc(2);
% ... then run algorithm on TDundistorted where the events are not
% necessarily integer values...
% 
% 
% 2: Run the optical flow algorithm on the original data and then take distortion into account.
% This method is poor because undoing the motion distortion is very noise
% sensitive due to division by small numbers and is likely to result in
% large inaccuracies. 
% [U, V, dU_dt, dV_dt] = undistort_motion(Xpixel, Ypixel, dXpixel_dt, dYpixel_dt, calibration_file);
% % to scale the units back to pixels, but not reapply distortion
% dXpixelUndistorted_dt = dU_dt*fc(1);
% dYpixelUndistorted_dt = dV_dt*fc(2);
% % similarly to find the undistorted pixel co-ordinates
% XpixelUndistorted = U*fc(1) + cc(1);
% YpixelUndistorted = V*fc(2) + cc(2);