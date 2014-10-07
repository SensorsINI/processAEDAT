function S=retinaSim(video,cfg)
% Given a video sequence of underlying images, simulate the resulting
% spike-train from the retina.
%
% video is an size [sizeX sizeY nFrames] matrix.
% 
% cfg is a structure containing fields
% 
% Field     Default     Meaning
% vdt        -           The time of one frame of video, in ms
% onRise    0.005       Onset time of the ON cells
% onAdapt   2           Adaptation time constant of the on cells
% onThresh  1           Firing threshold of on units
% onTC      .05;        Time Constant of ON-units
% offRise   0.005       Onset time of the ON cells
% offAdapt  2           Adaptation time of the OFF cells
% offTC     .05         Time Constant of OFF-units
% offThresh 1           Firing threshold of off units
% dims      [size(video,1),size(video,2)]   Pixel-array size.
% ndt       1           Time resolution of the retina, in ms
%
% S is an output structure with fields:
%
% Field     Dims        Meaning
% 

%% Step 1: Interpolate the image onto the sensor resolution

if isfield(cfg,'thresh')
    [cfg.onThresh cfg.offThresh]=deal(cfg.thresh);
end
if isfield(cfg,'rise')
    [cfg.onRise cfg.offRise]=deal(cfg.rise);
end
if isfield(cfg,'adapt')
    [cfg.onAdapt cfg.offAdapt]=deal(cfg.adapt);
end
if isfield(cfg,'TC')
    [cfg.onTC cfg.offTC]=deal(cfg.TC);
end



setdef('onRise',5);
setdef('onAdapt',2000);
setdef('onThresh',1);
setdef('onTC',100);
setdef('offRise',5);
setdef('offAdapt',2000);
setdef('offThresh',1);
setdef('offTC',100);
setdef('dims',[size(video,1),size(video,2)]);
setdef('ndt',1);
assert(isfield(cfg,'vdt'),'Must specify the video frame rate!');


ypoints=1:size(video,1)/cfg.dims(1):size(video,1);
xpoints=1:size(video,2)/cfg.dims(2):size(video,2);
tpoints=1:cfg.ndt/cfg.vdt:size(video,3)-100*eps;

[X Y]=meshgrid(ypoints,xpoints);
T=nan(size(Y));

% [Y X T]=ndgrid(ypoints,xpoints,tpoints);

% stim=interpn(video,Y,X,T);



%% Step 2: Transform that the stim into an activation matrix.

% [von voff]=deal(nan(length(ypoints),length(xpoints),length(tpoints),'single'));

[von voff riseOn adaptOn riseOff adaptOff]=deal(zeros(length(ypoints),length(xpoints),'single'));


cOnRise=exp(-cfg.ndt/cfg.onRise);
cOffRise=exp(-cfg.ndt/cfg.offRise);
cOnAdapt=exp(-cfg.ndt/cfg.onAdapt);
cOffAdapt=exp(-cfg.ndt/cfg.offAdapt);

cOnTC=exp(-cfg.ndt/cfg.onTC);
cOffTC=exp(-cfg.ndt/cfg.offTC);

% [von voff]=deal(nan(size(stim)));

geosum=@(r)1/(1-r);

scaledOnThresh=cfg.onThresh*(geosum(cOnAdapt)-geosum(cOnRise));
scaledOffThresh=cfg.onThresh*(geosum(cOffAdapt)-geosum(cOffRise));


% tmpDiff=diff(stim,[],3);
T(:)=1;

% lastLevel=zeros(cfg.dims);
lastLevel=interpn(video(:,:,1),Y,X);

[onSpikes offSpikes]=deal(false(length(ypoints)*length(xpoints),length(tpoints)));

fprintf('Computing Retina Response...'); prog=0;
for i=1:length(tpoints)
    
    vix=floor(tpoints(i));
    
    
    if isequal([size(video,1),size(video,2)],size(von))     % For speed
        rat=mod(tpoints(i),1);        
        level=video(:,:,vix)*(1-rat)+video(:,:,vix+1)*rat;   
    else
        T(:)=mod(tpoints(i),1)+1;
        level=interpn(video(:,:,vix:vix+1),Y,X,T);
    end
        
    stim=level-lastLevel;
    
    lastLevel=level;
    
%     onStim=stim*onScale;
    riseOn=riseOn*cOnRise+stim;
    adaptOn=adaptOn*cOnAdapt+stim;
    von=von*cOnTC+adaptOn-riseOn;
    ix=von>scaledOnThresh;
    onSpikes(ix,i)=true;
    von(ix)=0;
    
    riseOff=riseOff*cOffRise-stim;
    adaptOff=adaptOff*cOffAdapt-stim;
    voff=voff*cOffTC+adaptOff-riseOff;
    ix=voff>scaledOffThresh;
    offSpikes(ix,i)=true;
    voff(ix)=0;
    
    
    if i/length(tpoints)>prog        
        fprintf('%g%%..',prog*100);
        prog=prog+.05;        
    end
    
    
%     if mod(i,10)==0
%     
%         imagesc(voff,[-scaledOnThresh scaledOnThresh*2]);
%         colorbar;
%         title(sprintf('time: %g',i*cfg.ndt));
%         drawnow;
%     end
    
end

fprintf('Done.\n');


function setdef(field,val)

    if ~isfield(cfg,field) || isempty(cfg.(field))
        cfg.(field)=val;
    end
end

onSpikes=reshape(onSpikes,[length(ypoints),length(xpoints),length(tpoints)]);

offSpikes=reshape(offSpikes,[length(ypoints),length(xpoints),length(tpoints)]);




S=struct;
onEv=bin2spikes(onSpikes);
offEv=bin2spikes(offSpikes);

S.t=[onEv.t; offEv.t];
[S.t,ix]=sort(S.t);
S.x=[onEv.x; offEv.x];
S.y=[onEv.y; offEv.y];
S.pol=[true(length(onEv.t),1); false(length(offEv.t),1)];

S.x=S.x(ix);
S.y=S.y(ix);
S.pol=S.pol(ix);



end

function sp=bin2spikes(bin)

    ix=find(bin(:));
    
    sz=size(bin);
    
    sp.addr=mod(ix,sz(1)*sz(2));
    sp.y=mod(ix,sz(1));
    sp.x=floor(sp.addr/sz(1));
    sp.t=floor(ix / (sz(1)*sz(2)));
    

end