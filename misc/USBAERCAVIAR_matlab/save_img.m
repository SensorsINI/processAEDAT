function im=save_img(im,txt)
f=fopen(txt,'wb');
fwrite(f,im,'integer*1');
fclose(f);