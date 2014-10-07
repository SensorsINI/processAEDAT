function [ bins ] = calibrateComputeITDs( calibrationname, maxITD, numOfBins, delay )
%CALIBRATECOMPUTEITDS Summary of this function goes here
%   Detailed explanation goes here

for trial=1:length(delay)
    [trialAddr,trialTs]=loadaerdat([pwd '\Recording\' calibrationname '\ITD' num2str(delay(trial)) '.dat']);
    trialTs=trialTs-trialTs(1);
    
    [trialChan, trialNeuron, filterType, trialSide] = extractAMS1bEventsFromAddr( trialAddr );
    
    %Compute ITDs:
    bins{trial} = computeITDsPerChannel( trialTs, trialChan,trialSide , maxITD, numOfBins );
    bins{trial}=normr(bins{trial});
end


end

