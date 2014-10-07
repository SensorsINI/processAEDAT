 dev_play='atc15';
  [h1,e]=usbaeropen(dev_play);
  e=usbaerloadfpga(h1,'dataloggerv23.bin');
  fprintf('%s opened as Player. Handle = %d. Error = %d.\n',dev_play,h1,e);
if e==0
X=4;
Y=100;
s=0;
% sync=[0 0 128 0]; %Pulso de sincronización (bit más significativo de coordenada Y)
% sync=[sync ; 255 255 30 0]; % Tiempo de espera tras sincronización
% [6 0] is a wait period of a second, approximatelly.
 donut=generate_donut(32,32,12,13,1);
 events = []; %sync;
fprintf('Generating bursts...\n');
num_burst=10; % 1000*16*2
for i=1:num_burst
    events= [events ; generate_stimulus_matrix(donut,100,40)]; %(num_ev_burst, isi_ev in ns, burst period in ms, Y, X)
end
[a,b]=size(events);
fprintf('Generating wait time...\n');
%events(a-1,:)=events(a-2,:);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 
% cdlujan modifications - 13:30 20/12/07
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%events(a/2,1:2)=255;
%events(a/2,3:4)=[30 0]; % [6 0] is a wait period of a second, approximatelly. 
%events(a,1:3)=255;
%events(a,4)=254;
%events(a+1,1)=0;
%events(a+1,2)=200;
%events(a+1,3)=0;
%events(a+1,4)=0;
%events(a+2,:)=255;

%a=a+2;
events(a+1,:)=255;
a=a+1;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 
% END of cdlujan modifications - 13:30 20/12/07
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if (a<=256*1024)
   n=1;
else
    if (a>256*1024 && a<=2*256*1024)
        n=2;
    else
        if (a>2*256*1024 && a<=3*256*1024)
            n=3;
        else
            n=4;
        end
    end
end
fprintf('Erasing memory...\n');
e=usbaersend(h1,0,6); %Erase the USB-AER external events' memory
fprintf('Memory erased\n');
if n==1
    ev2=reshape(events',a*b,1);
    e=usbaersend(h1,double(ev2),[4 3 0 0 0]'); %Store the sequence of events in the board memory.
else if n==2 
    ev2=reshape(events(1:256*1024,:)',256*1024*b,1);
    e=usbaersend(h1,double(ev2),[4 3 0 0 0]'); %Store the sequence of events in the board memory.
    ev2=reshape(events(256*1024+1:a,:)',(a-256*1024)*b,1);
    e=usbaersend(h1,double(ev2),4); %Store the sequence of events in the board memory.
    else if n==3
        ev2=reshape(events(1:256*1024,:)',256*1024*b,1);
        e=usbaersend(h1,double(ev2),[4 3 0 0 0]'); %Store the sequence of events in the board memory.
        ev2=reshape(events(256*1024+1:2*256*1024,:)',256*1024*b,1);
        e=usbaersend(h1,double(ev2),4); %Store the sequence of events in the board memory.
        ev2=reshape(events(2*256*1024+1:a,:)',(a-2*256*1024)*b,1);
        e=usbaersend(h1,double(ev2),4); %Store the sequence of events in the board memory.
        else
            ev2=reshape(events(1:256*1024,:)',256*1024*b,1);
            e=usbaersend(h1,double(ev2),[4 3 0 0 0]'); %Store the sequence of events in the board memory.
            ev2=reshape(events(256*1024+1:2*256*1024,:)',256*1024*b,1);
            e=usbaersend(h1,double(ev2),4); %Store the sequence of events in the board memory.
            ev2=reshape(events(2*256*1024+1:3*256*1024,:)',2*256*1024*b,1);
            e=usbaersend(h1,double(ev2),4); %Store the sequence of events in the board memory.
            ev2=reshape(events(3*256*1024+1:a,:)',(a-3*256*1024)*b,1);
            e=usbaersend(h1,double(ev2),4); %Store the sequence of events in the board memory.
        end
    end
end
fprintf('Memory initialized from address 0: \n');
events(1:20,:);
pause (1);

e=usbaersend(h1,0,3); %Player starts to transmit
fprintf('Player sending events continously\n');
end