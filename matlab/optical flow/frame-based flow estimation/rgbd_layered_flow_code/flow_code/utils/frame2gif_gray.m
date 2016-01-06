function frame2gif_gray(volume,videoname,delaytime,resizeRate,height)

% Acoording to Ce LIU's matlab code
if exist('delaytime','var')~=1
    delaytime=0.5;
end
if exist('resizeRate','var')~=1
    resizeRate=1;
end
if exist('height','var')~=1
    height=0;
end

nframes=size(volume,3);

for i=1:nframes
    im=volume(:,:,i);
    if height~=0
        [h,w,nchannels]=size(im);
        resizeRate=height/h;
    end
    if resizeRate<1
        im=imresize(imfilter(im,fspecial('gaussian',5,0.7),'same','replicate'),resizeRate,'bicubic');
    else if resizeRate>1
            im=imresize(im,resizeRate,'bicubic');
        end
    end
    X = im;
    if i==1
        imwrite(uint8(X),videoname,'DelayTime',delaytime,'LoopCount',Inf);
    else
        imwrite(uint8(X),videoname,'WriteMode','append','DelayTime',delaytime);
    end
end