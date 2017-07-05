function error=usbaersendimage(h,fname)

fid=fopen(fname);
im=fread(fid,1024*4,'uint8=>double',0);
error=usbaersend(h,im);