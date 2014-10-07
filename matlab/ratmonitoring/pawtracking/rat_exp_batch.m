
function a = rat_exp_batch(pathfolder,smooth_factor,itermax)
pause on;




cd(pathfolder);
files = dir ('*.txt');
i = 0;
%itermax = 20;
size = length(files(:));
%size = 11;
figure;
hold on;

old_rat = rat_number(files(1).name);
i1 = 1;
for n=1:size
    i = i + 1;
    
    
    rat = rat_number(files(n).name);
  
    if length(rat)==length(old_rat)
      if rat~=old_rat
         i = itermax;        
      end
    else
       i = itermax; 
    end
    
    if i==itermax
        hold off;
        
       i = 0;
       j = n+itermax;
       message = ['press key to process rat#' rat ', files ' num2str(n) ' to ' num2str(j) ' out of ' num2str(size) ];
       message
       title([ 'rat #' old_rat ' , files ' num2str(i1) ' to ' num2str(n-1) ]);
       i1 = n;
       old_rat = rat;
       drawnow;
       pause;   
       
       figure;
       hold on;
    end
    
    rat_exp_xyz(files(n).name,smooth_factor);
    
end
hold off;