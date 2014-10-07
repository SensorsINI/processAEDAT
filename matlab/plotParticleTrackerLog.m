function plotParticleTrackerLog(file)
% plots paths of clusters logged from RectangularClusterTracker
% call it with plotParticleTrackerLog
persistent filename
if isempty(filename),
    filename='';
end
if nargin==0,
    [filename,path,filterindex]=uigetfile('*.m','Select recorded tracker log file',filename);
    if filename==0, return; end
end
if nargin==1,
    path='';
    filename=file;
end

i=0;
while(1),
    try
        [path]=feval(filename(1:end-2),i);
    catch
        break;
    end
%  i
  if (~isempty(path))
    t=path(:,1); 
    x=path(:,2);
    y=path(:,3);
    nevents=path(:,4);
    figure(1);
    plot3(t,x,y); 
    xlabel t
    ylabel x
    zlabel y
    hold on
  else
      cla;
  end; %if
  drawnow;
  i=i+1;
end; %for