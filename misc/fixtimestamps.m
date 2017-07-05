% This script fixes timestamps in jAER .aedat files that have non-monotonic or very large
% timetsamps differences that cause pauses in playback of data. These
% timestamp problems are due to early hardware used on early versions of
% the DVS128 camera and in some of the CPLD logic designs.
%
% The maxdt parameter determines max allowed delta time in us. delta times
% larger than maxdt are replaced by zero delta times. Non-monotonic
% timestamps (delta time less than zero) are fixed by removing the
% non-monotonic event.
%
% The script starts by running loadaerdat to load an existing .aedat file.
%
% The results are in the matrix train along with tout (output timestamps) and aout (output addresses)
% saveaerdat is run to save the fixed timestamp file.

maxdt=65e3; % specifies max allowed timestamp difference

[a,t]=loadaerdat;
st=int32(t); % signed times
n=length(a);
tshift=0;
figure(1);
plot(diff(st));
xlabel 'event'
ylabel 'delta time (us)'
title 'original delta times'
drawnow;

tout=t;
k=1;
for i=2:n,
    dt=st(i)-st(i-1);
    if dt<0, 
        fprintf('\ndt(%d)=%d\n',i,dt);
        continue, 
    end;
    if dt>65e3,
         fprintf('\ndt(%d)=%d\n',i,dt);
        t(i:end)=t(i:end)-uint32(dt);
    end
    tout(k)=t(i);
    k=k+1;
    if mod(i,100000)==0, fprintf('.'); end;
end
tout=tout(1:k-1);
aout=a(1:k-1);
plot(diff(st),'r');
hold on;
plot(diff(int32(tout)),'g');
hold off;
xlabel 'event'
ylabel 'delta time (us)'
title 'original (red) and fixed (green) delta times'

train=[int32(tout),int32(aout)];
saveaerdat(train);


