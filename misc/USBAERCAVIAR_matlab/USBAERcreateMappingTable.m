function mt=usbaercreatemappingtable(fname)

mt=zeros(512*1024,4);
j=1;
for xi=0:255
	for yi=0:255 
		for i=0:7
    		if (i==0)
                p=255; % probability of sending out the mapped event
				mt(j,4)=p; %probability
                d=0;   % delay in hundreds of microseconds to be delayed this output event (0 to 127)
                le=0;  % last mapped event control bit for the incoming event
				mt(j,3)=d*2+le; %es el ultimo y sin delay.
				mt(j,2)=yi/2; % The mapped x address
                mt(j,1)=xi; % The mapped y address
                j=j+1;
            end
    		if (i==1)
                p=128; % probability of sending out the mapped event
				mt(j,4)=p; %probability
                d=17;   % delay in hundreds of microseconds to be delayed this output event (0 to 127)
                le=0;  % last mapped event control bit for the incoming event
				mt(j,3)=d*2+le; %es el ultimo y sin delay.
				mt(j,2)=yi/2; % The mapped x address
                mt(j,1)=xi; % The mapped y address
                j=j+1;
            end
    		if (i==2)
                p=255; % probability of sending out the mapped event
				mt(j,4)=p; %probability
                d=0;   % delay in hundreds of microseconds to be delayed this output event (0 to 127)
                le=0;  % last mapped event control bit for the incoming event
				mt(j,3)=d*2+le; %es el ultimo y sin delay.
				mt(j,2)=yi/2; % The mapped x address
                mt(j,1)=xi; % The mapped y address
                j=j+1;
            end
    		if (i==3)
                p=255; % probability of sending out the mapped event
				mt(j,4)=p; %probability
                d=0;   % delay in hundreds of microseconds to be delayed this output event (0 to 127)
                le=1;  % last mapped event control bit for the incoming event
				mt(j,3)=d*2+le; %es el ultimo y sin delay.
				mt(j,2)=yi/2; % The mapped x address
                mt(j,1)=xi; % The mapped y address
                j=j+1;
            end
            if i>3 && i<=7
                mt(j,:)=[0 0 1 255]; % If not mapped be sure that the le bit is one
                j=j+1;
            end
        end
    end
end

fid=fopen(fname,'wb');
kk=reshape(mt',1024*2048,1);
fwrite(fid,kk,'uint8');