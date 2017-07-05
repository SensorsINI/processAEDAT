function wav2jAER( wavfile, outputfile )
%WAV2JAER This function plays a wav file and simultanously records the
%spikes from jAER.
%
%  Author: Holger Finger
%

if nargin<=1
    [filename,path]=uiputfile('*.dat','Select dat file');
    if filename==0
        return; 
    end
    outputfile=[path,filename];
    if nargin==0
        [filename,path]=uigetfile('*.wav','Select wav file');
        if filename==0
            return; 
        end
        wavfile=[path,filename];
    end
else
    outputfile = [pwd '\' outputfile];
end

[signal,Fs]=wavread(wavfile);

%Open connection to jAER:
u=udp('localhost',8997);
fopen(u);

fprintf(u,['startlogging ' outputfile]);   % send the command
fprintf('%s',fscanf(u)); % print the response

pause(0.1);
soundsc(signal,Fs);
pause(length(signal)/Fs);

pause(0.1);
fprintf(u,'stoplogging');   % send the command
fprintf('%s',fscanf(u)); % print the response

% clean up the UDP connection to jAER:
fclose(u);
delete(u);
clear u

end

