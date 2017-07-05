function video=barGen(cmd,cfg)
% Generate event-driven moving bar stimuli.
% 
% cmd is a structure array of commands, initialing and updating the bar's
%  position.  It contains fields:
% Field     Default     Meaning
% t         -           Time At which command happens
% cen       [0 0]       Bar Center Position, normalied to range [-1 1]
% wid       [.5 .5]     Bar Width in x,y directions (0=no width, 1=full screen widht]
% col       [0]         Bar shade [0=black 1=white]
% bgcol     [1]         Background [0=black, 1=white]
% 
% 
% cfg is a structure containing fields
% Field     Default     Meaning
% dims      [128 128]   A 2-element vecotr indicating the size of the visual area
% dt        .03         Frame-rate in s.


assert(all(arrayfun(@(c)~isempty(c.t),cmd)) && issorted([cmd.t]),'Your commands are not sorted in time!  Sort them.');


cfg=setdef(cfg,'dt',.03);


[y x]=meshgrid(linspace(-1,1,cfg.dims(1)),linspace(-1,1,cfg.dims(2)));

cmd=inferMissing(cmd);

times=cmd(1).t:cfg.dt:cmd(end).t;





video=zeros(cfg.dims(1),cfg.dims(2),length(times));
for frm=1:length(times)
   video(:,:,frm)=cmd2im(interpolate(cmd,times(frm)));    
end


    function comd=inferMissing(comd)
        % If a command setting has not been made, assume it is the same as
        % the previous command.
        
        comd(1)=setdef(comd(1),'cen',[0 0]);
        comd(1)=setdef(comd(1),'wid',[.5 .5]);
        comd(1)=setdef(comd(1),'col',0);
        comd(1)=setdef(comd(1),'bgcol',1);
        
        for i=2:length(comd)
%             assert(~isempty(comd.t),'Every command must have some specified time t');
            f=fields(comd);
            for j=1:length(f)
                if isempty(comd(i).(f{j}))
                    comd(i).(f{j})=comd(i-1).(f{j});
                end
            end
            
        end
    end

    function comd=interpolate(cmds,t)
        % Create a command at time t by interpolating the neighbouring commands
        
        ix=find(t>=[cmd.t],1,'last');
        
        assert(~isempty(ix)&&ix<length(cmds),'You''re requesting a point that falls out of the given range of commands!');
        
        cmd1=cmds(ix);
        cmd2=cmds(ix+1);
        
        rat=(t-cmd1.t)/(cmd2.t-cmd1.t);
        
        f=fields(cmds);
        for j=1:length(f)
            comd.(f{j})=(1-rat)*cmd1.(f{j}) + rat*cmd2.(f{j});
        end
               
    end


    function im=cmd2im(comd)
        % Construct an image given the specified command

        im=repmat(comd.bgcol,cfg.dims);

        im(abs(y-comd.cen(1))<comd.wid(1) & abs(x-comd.cen(2))<comd.wid(2))=comd.col;


    end

    function struc=setdef(struc,field,val)
        if ~isfield(struc,field)||isempty(struc.(field))
            struc.field=val;
        end
    end

end