function touchDir(fdir)
%%
if ~exist(fdir, 'file')
    mkdir(fdir);
end