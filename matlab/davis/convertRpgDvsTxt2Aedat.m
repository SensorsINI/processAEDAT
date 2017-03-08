function [allAddr,allTs]=convertRpgDvsTxt2Aedat(file)
%function [allAddr,allTs]=convertRpgDvsTxt2Aedat(file);
% loads events from a text file events.txt of format used in the RPG event based
% dataset and writes out to Davis240C AER-DAT-2.0 file
%
% file is the input filename including path. Noarg invocation opens a file
% chooser. The output file is saved as events.txt.aedat.

pathname=pwd;
% check the input arguments
if ~exist('file', 'var')
    [filename,pathname,~]=uigetfile('events.txt','Select recorded retina text data file');
    if filename==0, return; end
elseif ischar(file)
    filename = file;
end
ifilename=fullfile(pathname,filename);
fprintf('importing data in file %s ...',ifilename);
d=importdata(ifilename);
fprintf(' done\n');
xshift=12;
yshift=22;
polshift=11;

ts=int32(d(:,1)*1e6);
x=int32(d(:,2));
y=int32(d(:,3));
p=int32(d(:,4));

addr=bitshift(x,xshift)+bitshift(y,yshift)+bitshift(p,polshift);
ofilename=fullfile(pathname, [filename,'.aedat']);
fprintf('saving aedat file %s....',ofilename);
saveaerdat([ts,addr],ofilename);
