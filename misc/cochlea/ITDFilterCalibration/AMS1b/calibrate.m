function calibrate( calibrationname, wavfile, ITDmax, numOfBins )
% This function plays a wavfile with different ITDs and records with jAER at the same time.
% Then it evaluates these recordings and creates a calibration.xml file for the ITDFilter.
%
% calibrationname is an arbitrary string to specify the folder name to which it records.
% wavfile is the filename of the wavfile which is used for the calibration
% ITDmax is the maximum ITD to compute in us (for example 800)
% numOfBins is the number of ITD Bins which should be used later by the ITDFilter

delays=linspace(-ITDmax+ITDmax/numOfBins,ITDmax-ITDmax/numOfBins,numOfBins);

%Recordings:
if 1
    mkdir(['Recording/' calibrationname])
    [signal,Fs]=wavread(wavfile);
    calibrateRecord( calibrationname, signal, Fs, delays );
end

%Compute ITDs in Bins:
bins = calibrateComputeITDs( calibrationname, ITDmax, numOfBins, delays );

%Fit Gaussians:
[Ampl,Mu,Sigma,gof] = calibrateEvaluateBins( bins, delays);

%Save Data:
save(['Recording/' calibrationname '/calibration.dat'])

%Write the calibration file:
calibrateWriteCalibrationFile( Mu, Sigma, ITDmax, ['Recording/' calibrationname '/calibration.xml'] )


end