function [freqResponse]=computeFreqResp( calibrationname, frequencies, signallength, record )
%calibrationname is a string used for the foldername to store the files
%frequencies is a vector containing the frequencies to test (in Hz)
%signallength is the playtime of every frequency (in seconds)

%Recordings:
mkdir(['Recording/' calibrationname])
Fs=16000;
numOfCochleaChannels=32;

if record
    %Open connection to jAER:
    u=udp('localhost',8997);
    fopen(u);
    
    for trial=1:length(frequencies)
        signal=sin((1:signallength*Fs)*2*pi*frequencies(trial)/(signallength*Fs));
        commandJAER(u,['startlogging ' pwd '\Recording\' calibrationname '\ITD' num2str(frequencies(trial)) '.dat'])
        pause(0.5);
        fprintf('playing now sine wave with %d Hz, %d measurments left \n', frequencies(trial), length(frequencies)-trial);
        soundsc(signal,Fs);
        pause(signallength+1);
        commandJAER(u,'stoplogging')
        pause(0.5);
    end
    % clean up the UDP connection to jAER:
    fclose(u);
    delete(u);
    clear u
end

freqResponse{1}=zeros(length(frequencies),numOfCochleaChannels);
freqResponse{2}=zeros(length(frequencies),numOfCochleaChannels);
for trial=2:length(frequencies)
    [trialAddr,trialTs]=loadaerdat([pwd '\Recording\' calibrationname '\ITD' num2str(frequencies(trial)) '.dat']);
    [trialChan,trialSide]=extractCochleaEventsFromAddr(trialAddr);
    for chan=2:numOfCochleaChannels
        ind=find(trialChan==chan);
        freqResponse{1}(trial,chan)=length(find(trialSide(ind)==0));
        freqResponse{2}(trial,chan)=length(ind)-freqResponse{1}(trial,chan);
    end
end

figure(1)
surf(1:numOfCochleaChannels,frequencies,freqResponse{1})
set(gca, 'YScale', 'log')
ylabel('Played Frequency');
xlabel('Cochlea Channel');
zlabel('Response');
title('Left Cochlea');

figure(2)
surf(1:numOfCochleaChannels,frequencies,freqResponse{2})
set(gca, 'YScale', 'log')
ylabel('Played Frequency');
xlabel('Cochlea Channel');
zlabel('Response');
title('Right Cochlea');
end