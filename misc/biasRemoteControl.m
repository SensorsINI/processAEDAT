% this file contains some examples of scripts to control biases in jaer
% chips using the RemoteControl UDP facilities. Instruments (e.g. Keithley 6430 picoammeter source mesaure unit)
% are controlled
% here using the physcmp GPIB package
% http://www.ini.uzh.ch/~tobi/resources/PHYSCMP-03282006.zip

%% open udp connection for controlling biases etc via udp RemoteControl
u=udp('localhost',8995,'inputbuffersize',8000);
fopen(u);

%% test by sending command
fwrite(u,'selectMux_Currents 1');
fprintf('%s',fscanf(u));

%% close the connection
fclose(u);
delete(u);
clear u

%% get the help from jaer
fwrite(u,'help');
fprintf('%s',fscanf(u));
    
%% iterate over biases
vals=(2.^(1:22))-1;
for i=1:length(vals),
    v=vals(i);
    c=sprintf('seti_ifthr %d\n',v);
    fprintf(c,v);
    fwrite(u,c);
    fprintf('%s',fscanf(u));
    pause(.5);
end


%% using a GPIB library (physcmp), read the kiethley 6430 picoammeter SMU
%% current from a chip (DVS320) with fully configurable bias generator
% for each bit bias value and plot results
nmult=(6.8/2.59*2)/(4.8/2.4)*(8/8)*(1.2/1.51*100); % estimated multiplier from bias current to ntest output
pmult=(6.8/2.59*2)/(4.8/2.4)*(8/8)*(.8/.8*100); % ptest multiplier

bitvals=(2.^(0:21));
currents=NaN*zeros(4,length(bitvals)); % each row is a different bias sex/level
sexcmds={'setsex_ifthr N','setsex_ifthr P'};
levelcmds={'setlevel_ifthr Normal','setlevel_ifthr Low'};
flushinput(u); % clear out leftover junk
biassign=-1;
k6430_SourceVolt(.9);
fwrite(u,'setibuf_ifthr 4');
fprintf('%s',fscanf(u));

for j=1:2,
    fwrite(u,sexcmds{j});
    fprintf('%s',fscanf(u));
    
     biassign=-biassign;
    fprintf(u,'selectMux_Currents %d',j-1);
     fprintf('%s',fscanf(u));

    for k=1:2,
        fprintf(u,levelcmds{k});
        fprintf('%s',fscanf(u));
        btype=(j-1)*2+k-1+1; % 1,2,3,4
        
        for i=1:length(bitvals),
            v=bitvals(i);
            c=sprintf('seti_ifthr %d\n',v);
            fprintf(c,v);
            fprintf(u,c);
            fprintf('%s',fscanf(u));
            pause(1);
            currents(btype,i)=biassign*k6430_Take;
            figure(1);
            loglog(bitvals,currents);
            xlabel 'bit value'
            ylabel 'current'
            legend('N','Nlow','P','Plow');
        end
    end
end
currentsscaled=currents;
currentsscaled([1,3],:)=currents(1:2,:)*nmult;
currentsscaled([2,4],:)=currents(1:2,:)*pmult;
           figure(1);
            loglog(bitvals,currentsscaled);
            xlabel 'bit value'
            ylabel 'currents (scaled to estimated internal value)'
            legend('N','Nlow','P','Plow');

k6430_GoToLocal


%% using a GPIB library (physcmp), read the kiethley 6430 picoammeter SMU
%% voltage from a chip (DVS320) with fully configurable bias generator
% for each buffer bit bias value and plot results

bitvals=(2.^(0:6));
voltages=NaN*zeros(4,length(bitvals)); % each row is a different bias sex/level
sexcmds={'setsex_ifthr N','setsex_ifthr P'};
levelcmds={'setlevel_ifthr Normal','setlevel_ifthr Low'};
flushinput(u); % clear out leftover junk
biassign=-1;
k6430_SourceVolt(.9);
fprintf(u,'seti_ifthr 41024');
fprintf('%s',fscanf(u));
k6430_SetMode('V');
for j=1:2,
    fprintf(u,sexcmds{j});
    fprintf('%s',fscanf(u));
    
     biassign=-biassign;
    fprintf(u,'selectMux_Currents %d',j-1);
     fprintf('%s',fscanf(u));

    for k=1:2,
        fprintf(u,levelcmds{k});
        fprintf('%s',fscanf(u));
        btype=(j-1)*2+k-1+1; % 1,2,3,4
        
        for i=1:length(bitvals),
            v=bitvals(i);
            c=sprintf('seti_ifthr %d\n',v);
            fprintf(c,v);
            fprintf(u,c);
            fprintf('%s',fscanf(u));
            pause(1);
            voltages(btype,i)=biassign*k6430_Take;
            figure(1);
            loglog(bitvals,voltages);
            xlabel 'bit value'
            ylabel 'current'
            legend('N','Nlow','P','Plow');
        end
    end
end
k6430_GoToLocal

%% measure a single bias using low current mode over all bias and bias
%% buffer values

bufbitvals=(2.^(0:5));
bitvals=(2.^(0:21));
bitvals=logspace(0,2^22-1,200);
currents=NaN*zeros(length(bufbitvals),length(bitvals)); % each row is a different bias sex/level
sexcmds={'setsex_ifthr N','setsex_ifthr P'};
levelcmds={'setlevel_ifthr Normal','setlevel_ifthr Low'};
flushinput(u); % clear out leftover junk
biassign=1;
k6430_SourceVolt(1);
k6430_SetMode('V');
fprintf(u,sexcmds{1});
fprintf('%s',fscanf(u));
fprintf(u,levelcmds{2});
fprintf('%s',fscanf(u));

for j=1:length(bufbitvals),
    for k=1:length(bitvals),
        v=bitvals(i);
        fprintf(u,'seti_ifthr %d\n',bitvals(k));
        fprintf('%s',fscanf(u));
        fprintf(u,'setibuf_ifthr %d\n',bufbitvals(j));
        fprintf('%s',fscanf(u));
        pause(1);
        currents(j,k)=biassign*k6430_Take;
        figure(1);
        mesh(1:length(bitvals), 1:length(bufbitvals), currents);
        xlabel 'bit value'
        ylabel 'buffer bit value'
        set(gca,'zscale','log');
    end
end

k6430_GoToLocal

%% plots currents
        figure(1);
        mesh(1:length(bitvals), 1:length(bufbitvals), currents);
        xlabel 'bit value'
        ylabel 'buffer bit value'
        set(gca,'zscale','log');
figure(2);
plot(log10(max(0,currents')));
xlabel 'bias bit'
legend(0:5);

%% control smu
while 1,
    fprintf('%-9.2e\r',k6430_take);
end

%% go to local mode for live readings
k6430_GoToLocal

%% select a mux channel example
fprintf(u,'selectMux_AnaMux4 0')
fprintf('%s',fscanf(u));


