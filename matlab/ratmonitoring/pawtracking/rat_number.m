
function a = rat_number(filename)

% return rat #
filename
k = strfind(filename,'rat')
k2 = strfind(filename,'s')
k3 = strfind(filename,'.')

if isempty(k)
    a = '1';
else
    
if isempty(k2) 
    k4 = k3;
else
    k4 = k2;
    
end
k4
if k4>k+4
    a = [filename(k+3) filename(k+4)]
else 
    a = filename(k+3)
end

end