
function a = save_to_ascii( name, indexes );


fid = fopen([ name '.txt'],'wt');

for n = 1:length(indexes)
    fprintf(fid,'%g\n',indexes(n));
   
end;

fclose(fid);