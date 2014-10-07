function mt=usbaercreatemappingtable(fname)
% Para el firmware de paco d=1 es lo mismo que N=1
mt=zeros(512*1024,4);
mt(:,3)=1;
j=9;
for xi=0:255
	for yi=1:2:255 
		for i=0:7
    		if (i==0)
                if (xi==31)% || 2*xi==yi || 2*xi+1==yi || yi==63 || yi==62 || 2*(63-xi)==yi || 2*(63-xi)+1==yi)
                    p=255; % probability of sending out the mapped event
    				mt(j,4)=p; %probability
                    d=0;   % delay in hundreds of microseconds to be delayed this output event (0 to 127)
                    le=0;  % last mapped event control bit for the incoming event
                	mt(j,3)=d*2+le; %es el ultimo y sin delay.
                    mt(j,2)=floor(xi); % The mapped x address
                    mt(j,1)=floor(yi); % The mapped y address
                    j=j+1;
                else
                    mt(j,:)=[0 0 1 0]; % If not mapped be sure that the le bit is one
                    j=j+1;
                end
            end
    		if (i==1)
                if (xi==31) % || 2*xi==yi || 2*xi+1==yi || yi==63 || yi==62 || 2*(63-xi)==yi || 2*(63-xi)+1==yi)
                    p=255; % probability of sending out the mapped event
        			mt(j,4)=p; %probability
                    d=116;   % delay in hundreds of microseconds to be delayed this output event (0 to 127)
                    le=1;  % last mapped event control bit for the incoming event
    				mt(j,3)=d*2+le; %es el ultimo y sin delay.
                    if (xi==31 || 2*xi==yi || 2*xi+1==yi) %|| 2*(63-xi)==yi || 2*(63-xi)+1==yi)
                        mt(j,2)=floor(xi+1); % The mapped x address
                        mt(j,1)=floor(yi); % The mapped y address
                    else 
                        mt(j,2)=floor(xi); % The mapped x address
                        mt(j,1)=floor(yi+2); % The mapped y address
                    end
                    j=j+1;
                else
                    mt(j,:)=[0 0 1 0]; % If not mapped be sure that the le bit is one
                    j=j+1;
                end
            end
           if (i>1 && i<8)
               %mt(j,:)=[0 0 1 0]; % If not mapped be sure that the le bit is one
               j=j+1;
               if (i==7)
                  %mt(j,:)=[0 0 1 0]; % If not mapped be sure that the le bit is one
                  j=j+8;
%                if yi==254
%                    j=j+256*8;
               end
           end
        end
    end
end

fid=fopen(fname,'wb');
kk=reshape(mt',1024*2048,1);
fwrite(fid,kk,'uint8');