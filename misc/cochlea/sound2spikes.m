function [allAddr,allTs] = sound2spikes( soundData, Fs )
%WAV2JAER This function plays a wav file and simultanously records the
%spikes from jAER.
%
%  Author: Holger Finger
%

tempfile='C:\tempSpikes.dat';
%Open connection to jAER:
u=udp('localhost',8997);
fopen(u);

fprintf(u,['startlogging ' tempfile]);   % send the command
fprintf('%s',fscanf(u)); % print the response

pause(0.1);
sound(soundData,Fs);
pause(length(soundData)/Fs);

pause(0.1)
fprintf(u,'stoplogging');   % send the command
fprintf('%s',fscanf(u)); % print the response

% clean up the UDP connection to jAER:
fclose(u);
delete(u);
clear u;

pause(0.1)
[allAddr,allTs]=loadaerdat(tempfile);

end

