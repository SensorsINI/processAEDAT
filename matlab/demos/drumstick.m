function D = drumstick(D)
% drum stick hit time detection from spiking retina visual event data
% record a drum stick hit movie (stroke direction from top to bottom!) and try
% D... preloaded aer retina data i.e D=bin_aer('drumstick_rebound_200_15cm.dat',1e-3);

doplot =1;
D.bin.y_thres = 75;
D.bin.dn = 30*1e-3/D.bin.dt;
D.bin.y_navg = movavg(D.bin.y_avg,round(D.bin.dn));
bState = false; i0=1;
D.bin.hit = zeros(size(D.bin.n));
D.bin.thit = [];
D.bin.y_var = 100*ones(size(D.bin.n));
for i=2:length(D.bin.y_navg)
  %this is for excluding non-stroke parts of the video, variance
  %of moving average reduced y should be low before real hit
  if i>10
    D.bin.y_var(i) = var(D.bin.y_avg(i-10:i)-D.bin.y_navg(i-10:i));
  end
  %within region of low y_navg? (stick low)
  if D.bin.y_navg(i-1)>D.bin.y_thres && D.bin.y_navg(i)<=D.bin.y_thres
    bState = true;
    i0 = i;
  end
  if D.bin.y_navg(i-1)<=D.bin.y_thres && D.bin.y_navg(i)>D.bin.y_thres
    bState = false;
    %hit is minimum event rate (stick velocity is near zero at the ~2ms of hit)
    %hit is counted at the beginning of the zero velocity period, at lowest velocity
    [dummy thit] = min(D.bin.n(i0:i-1));
    if D.bin.y_var(i0) < 50
      D.bin.hit(i0+thit-1) = 1;
      D.bin.thit(end+1) = (i0+thit-1)*D.bin.dt;
    end
  end
  D.bin.I(i) = bState;
end
[num2str(length(D.bin.thit)) 32 'drum strokes detected']
['mean interval =' 32 num2str(mean(diff(D.bin.thit))) 's']
['std  interval =' 32 num2str(std(diff(D.bin.thit))) 's']
if doplot
  figure;
  plot((1:length(D.bin.n))*1e-3,[D.bin.n; D.bin.y_avg; D.bin.y_navg; D.bin.I*100; D.bin.hit*100]');
  legend({'r(t)','y_{avg}(t)','y_{navg}(t)','I(t)','t_{hit}(t)'});
  title('drum stick rebound task');xlabel('t[s]');
end

function y = movavg(x,dt)
% timeseries x convoluted with even rectangular function,
% with time constant dt

if isvector(x)
  if size(x,1)>1
    x=x';
  end
  csum=cumsum(x);
  a=[csum(dt+1:end) csum(end)*ones(1,dt)];
  b=[zeros(1,dt) csum(1:end-dt)];
  y=(a-b)/(2*dt);
end
