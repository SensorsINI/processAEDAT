function error=usbaersendmappingtable(h,fname,delay,rng,addr)
%Delay in us up to 65535 us of delay

fid=fopen(fname);
im=fread(fid,1024*2048,'uint8=>double',0);
par=zeros(16,1);
par(1)=mod(addr,256);
par(2)=mod(floor(addr/256),256);
par(3)=floor(addr/256/256);
par(4)=mod(delay,256);
par(5)=floor(delay/256);
par(6)=mod(rng,256);
par(7)=floor(rng/256);
error=usbaersend(h,im,par);