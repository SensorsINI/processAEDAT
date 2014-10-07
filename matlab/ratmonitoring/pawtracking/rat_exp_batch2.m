
function a = rat_exp_batch2(pathfolder,smooth_factor,itermax)
pause on;




%cd(pathfolder);
files = dir ([ pathfolder '/*.txt']);
i = 0;
%itermax = 20;
size = length(files(:));
%size = 11;
figure;
hold on;


speeds(1) = 0;
speeds(2) = 0;
speeds(3) = 0;
speeds(4) = 0;
speeds(5) = 0;
nsp = 0;
%old_rat = rat_number(files(1).name);
i1 = 1;
for n=1:size
    i = i + 1;
    
    
   % rat = rat_number(files(n).name);
  
    %if length(rat)==length(old_rat)
    %  if rat~=old_rat
   %      i = itermax;        
   %   end
   % else
   %    i = itermax; 
   % end
    
   sp = rat_exp_xyz([pathfolder '/' files(n).name],smooth_factor,files(n).name);
   speeds(1) = speeds(1)+sp(1);
   speeds(2) = speeds(2)+sp(2);
   speeds(3) = speeds(3)+sp(3);
   speeds(4) = speeds(4)+sp(4);
   speeds(5) = speeds(5)+sp(5);
   
  
   
   
   
   nsp = nsp + 1;

  %  rat_exp_xyz_cloud([pathfolder '/' files(n).name],smooth_factor);
   
    if i==itermax | n==size
        hold off;
        
       i = 0;
       j = n+itermax;
       
       if n~=size
         message = ['press key to process next files ' num2str(n+1) ' to ' num2str(j) ' out of ' num2str(size) ];
         message
       end
       
       
       
       if itermax==1
         % title([ pathfolder ' , file ' num2str(i1) ' : ' files(n).name ]); 
          
          figtitle = [ pathfolder ' , file ' num2str(i1) ' : ' files(n).name ];
          title(figtitle);
          set(gcf(),'Name',figtitle)
       else           
        %  title([ pathfolder ' , files ' num2str(i1) ' to ' num2str(n) ]);
          figtitle = [ pathfolder ' , files ' num2str(i1) ' to ' num2str(n) ];
          title(figtitle);
          set(gcf(),'Name',figtitle)
       end
       i1 = n+1;
      % old_rat = rat;
       drawnow;
       
       
       if n~=size
           
       
         pause;   
       
         figure;
       %  axis(700,1300,1700,2400,-800,-300);
         hold on;
       end
    end
    
    
    
end
hold off;

if(nsp~=0)
   speeds(1) = speeds(1)/nsp;
   speeds(2) = speeds(2)/nsp;
   speeds(3) = speeds(3)/nsp;
   speeds(4) = speeds(4)/nsp;
   speeds(5) = speeds(5)/nsp;
   
   
   rat_plot_speed(pathfolder,speeds);
   

end




