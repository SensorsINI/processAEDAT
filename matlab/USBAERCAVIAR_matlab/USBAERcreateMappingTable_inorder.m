function mt=usbaercreatemappingtable(fname)
% Para el firmware de paco d=1 es lo mismo que N=1
mt=zeros(256*1024,4);
mt(:,3)=1;
j=9;
for xi=0:255
	for yi=1:2:255 
		for i=0:7
    		if (i==0)
                if xi==32 
                    p=255; % probability of sending out the mapped event
    				mt(j,4)=p; %probability
                    d=1;   % delay in hundreds of microseconds to be delayed this output event (0 to 127)
                    n=0;
                    le=0;  % last mapped event control bit for the incoming event
                	mt(j,3)=d*32+n*2+le; %es el ultimo y sin delay.
                    mt(j,2)=floor(xi); % The mapped x address
                    mt(j,1)=floor(yi); % The mapped y address
                end
                    j=j+1;
            end
    		if (i==1)
                if xi==32
                    p=255; % probability of sending out the mapped event
        			mt(j,4)=p; %probability
                    d=0;   % delay in hundreds of microseconds to be delayed this output event (0 to 127)
                    n=0;
                    le=1;  % last mapped event control bit for the incoming event
    				mt(j,3)=d*32+n*2+le; %es el ultimo y sin delay.
                    mt(j,2)=floor(xi+1); % The mapped x address
                    mt(j,1)=floor(yi); % The mapped y address
                end
                    j=j+1;
            end
           if (i>1 && i<8)
               j=j+1;
               if i==7
                   j=j+8;
               end
           end
        end
    end
end

fid=fopen(fname,'wb');
kk=reshape(mt',512*2048,1);
fwrite(fid,kk,'uint8');