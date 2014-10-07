
function a = rat_exp_speed_batch(pathfolder,z0,zmin)
pause on;


%cd(pathfolder);
files = dir ([ pathfolder '/*.txt']);
i = 0;

size = length(files(:));


 meantime = 0;
 meandist = 0;
 meanspeed = 0;
 meanzdist = 0;
 meanzspeed = 0;

 
 maxspeed = 0;
 maxzspeed = 0;
 
i = 0;
for n=1:size
   
    
    
   % rat = rat_number(files(n).name);
  
    %if length(rat)==length(old_rat)
    %  if rat~=old_rat
   %      i = itermax;        
   %   end
   % else
   %    i = itermax; 
   % end
    
 %  res = rat_exp_speed([pathfolder '/' files(n).name],z0,zmin);
 
 
   res = rat_exp_speed_max([pathfolder '/' files(n).name],z0,zmin);
   
   if res(1)~=0
       i = i + 1;   
       meantime = res(1) + meantime;
       meandist = res(2) + meandist;
       meanspeed = res(3) + meanspeed;
       meanzdist = res(4) + meanzdist;
       meanzspeed = res(5) + meanzspeed;
       if res(3)>maxspeed
           maxspeed = res(3);
       end
       if res(5)>maxzspeed
           maxzspeed = res(5);
       end
   end
     
end
i
meantime =  meantime/i
meandist =  meandist/i
meanspeed =  meanspeed/i
meanzdist =  meanzdist/i
meanzspeed =  meanzspeed/i
maxspeed
maxzspeed

