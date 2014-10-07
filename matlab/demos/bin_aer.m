function D = bin_aer(filename,dt)
% bins elements of address event data (AER) 
% D.bin.x/y/t/n...x/y/t values and #events in each time bin 
% dt..........length of time bins in seconds

N=128;
D.bin.dt = dt;
dt = uint32(dt*1e6);%us
%[tbins T2]=hist(double(D.t),double((max(D.t)-min(D.t))/dt));
if isstr(filename)
  'load aer data from file...'
  [D.a D.t]=loadaerdat(filename);
  D.id=filename;
  [D.x D.y D.e]=extractRetina128EventsFromAddr(D.a);
  [num2str(D.bin.dt) 's binning...']
  T=min(D.t)+dt/2:dt:max(D.t)+dt/2;
  n=1;
  for t=1:length(T)
      n0=n;
      while (n<=length(D.t) && D.t(n)<(T(t)+dt/2))
	  n=n+1;
      end
      I=n0:n-1;
      D.bin.n(t)=length(I);
      if ~isempty(I)
          D.bin.y{t}=D.y(I);
          D.bin.x{t}=D.x(I);
          D.bin.t{t}=D.t(I);
          D.bin.e{t}=D.e(I);
          D.bin.y_avg(t)=mean(D.y(I));
          D.bin.x_avg(t)=mean(D.x(I));
          %plot
          if 0
          M=zeros(N,N); 
          for i=1:length(D.bin.n(t))
              x=D.bin.x{t}(i); x=round(max(1,min(N,x)));
              y=D.bin.y{t}(i); y=round(max(1,min(N,y)));
              M(round(x(i)),round(y(i)))=M(round(x(i)),round(y(i)))+D.bin.e{t}(i);
          end
          M
          D.bin.x{t}
          D.bin.y{t}
          figure(1);
          image(M*128);
          colormap(gray(256));
          title(['t=' num2str(T(t))*1e-6 's']);
          end
      end
  end
else
  D = [];
end

%D=bin_aer('movies/drumstick_rebound_200_15cm.dat',1e-3);
%D=drumstick(D);
