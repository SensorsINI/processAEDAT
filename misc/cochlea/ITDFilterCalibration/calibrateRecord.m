function calibrateRecord( calibrationname, signal, Fs, delays )
%CALIBRATERECORD Summary of this function goes here
%   Detailed explanation goes here

%Open connection to jAER:
u=udp('localhost',8997);
fopen(u);

playtime=length(signal)/Fs;

for trial=1:length(delays)
    commandJAER(u,['startlogging ' pwd '\Recording\' calibrationname '\ITD' num2str(delays(trial)) '.dat'])
    pause(1);
    fprintf('playing now %d delay, %d measurments left \n', delays(trial), length(delays)-trial);
    calibratePlayDelayed( signal, Fs, delays(trial));
    pause(playtime+1);
    commandJAER(u,'stoplogging')
    pause(1);
end

% clean up the UDP connection to jAER:
fclose(u);
delete(u);
clear u

end

