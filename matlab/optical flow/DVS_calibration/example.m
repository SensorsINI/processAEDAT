% Create the calibration images, more the better
cd Calibrate
% Use the 'PresentStimulus' function to bring up a calibration pattern on
% the screen. 
rectangleSize_mm = PresentStimulus([10,10], 10);
% and make a recording of the stimulus using ATIS
% (press any key in Matlab to make the stimulus start flashing)

% Read the recordings from ATIS ".val" file and convert to an image using 
% the 'MakeImage' function. 

%% For ATIS
% This script requires some ATIS functions to be on 
% the Matlab Path. These functions can be obtained from
% http://www.garrickorchard.com/code/matlab-AER-functions 
[TD, APS] = ReadAER(filename);
%if using EM events:
image = MakeImage(EM, [304,240], 1);
%if using TD events:
image = MakeImage(TD, [304,240], 0);


%% For DVS
% This script requires some DVS functions to be on 
% the Matlab Path. These functions can be obtained from
% https://svn.code.sf.net/p/jaer/code/scripts/matlab
[allAddr,allTs]=loadaerdat(filename);
[TD.x,TD.y,TD.p]=extractRetina128EventsFromAddr(allAddr);
TD.x = TD.x+1; % difference in convention between DVS and ATIS
TD.y = TD.y+1; % difference in convention between DVS and ATIS
TD.p(TD.p==-1) = 0;

image = MakeImage(TD, [128,128], 0);

%% save to a file
image_number = 0; %which of the images is this (multiple images are required for calibration)
imwrite(image,['CalibrationImages\img', num2str(image_number), '.bmp'], 'bmp')

% now run the Caltech Camera Calibration toolbox and use the generated
% images for calibration. The toolbox is available from:
% http://www.vision.caltech.edu/bouguetj/calib_doc/