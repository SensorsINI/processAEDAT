function donut=generate_donut(x0,y0,r1,r2,M)

xmin=x0-r2;
xmax=x0+r2;
ymin=y0-r2;
ymax=y0+r2;
i=0;
donut=[];
for k=1:M
for x=xmin:xmax
    for y=ymin:ymax
        r=sqrt((x-x0)^2+(y-y0)^2);
        if r>=r1 & r<=r2
            donut= [donut; 2*y x];
        end
    end
end
end
[a,b]=size (donut);
fprintf('Eventos: %d\n',a/M);