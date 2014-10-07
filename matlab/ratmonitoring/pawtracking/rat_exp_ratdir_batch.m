
function a = rat_exp_ratdir_batch(pathfolder,smooth_factor,itermax)
pause on;




cd(pathfolder)


% rats or conditions are in different subfolders
% use subfolder name instead of rat names here

dirs = dir;
size = length(dirs(:));


for n=1:size
   if dirs(n).isdir
       if dirs(n).name(1)~='.' 
           
           rat_exp_batch2(dirs(n).name,smooth_factor,itermax);
           
          % rat_exp_batch_many_movie(dirs(n).name,smooth_factor,itermax);
           
       end
       
   end
    
    
end

