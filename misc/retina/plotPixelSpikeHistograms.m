% plots histogram for one pixel 

x=[64:70];
y=[64:70];
pol=1
h=[];
% addresses are in a
for xx=x,
    for yy=y,
        raw=getTmpdiff128Addr(xx,yy,pol);
        ind=find(raw==a);
        h=[h,length(ind)];
        % a1=a(ind);
        % t1=t(ind);
    end
end
hi=hist(h,[0:30]);