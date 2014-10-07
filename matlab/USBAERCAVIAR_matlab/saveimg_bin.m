function saveimg_bin(im,txt)

f=fopen(txt,'wb');
fwrite(f,im,'integer*1');
fclose(f);