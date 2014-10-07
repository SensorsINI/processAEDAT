function [ bins ] = calibrateComputeITDs( calibrationname, maxITD, numOfBins, delay )
%CALIBRATECOMPUTEITDS Summary of this function goes here
%   Detailed explanation goes here

for trial=1:length(delay)
    [trialAddr,trialTs]=loadaerdat([pwd '\Recording\' calibrationname '\ITD' num2str(delay(trial)) '.dat']);
    trialTs=trialTs-trialTs(1);
    [trialChan,trialSide]=extractCochleaEventsFromAddr(trialAddr);
    
    %remove channel 1 data: (because too much spikes)
    deleteNotIndices=find(trialChan~=1);
    trialTs=trialTs(deleteNotIndices);
    trialChan=trialChan(deleteNotIndices);
    trialSide=trialSide(deleteNotIndices);
    
    %Compute ITDs:
    bins{trial} = computeITDsPerChannel( trialTs, trialChan,trialSide , maxITD, numOfBins );
    bins{trial}=normr(bins{trial});
end


end

