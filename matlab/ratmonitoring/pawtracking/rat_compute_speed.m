% compute speed

function a = rat_compute_speed(data,i)
  
% compute speed
timelengthOfGrasp = data(i,1)-data(1,1);
distx = data(i,2)-data(1,2);
disty = data(i,3)-data(1,3);
distz = data(i,4)-data(1,4);
dist = sqrt(distx*distx + disty*disty + distz*distz );

dz = sqrt(distz*distz );

if(timelengthOfGrasp==0)
    a(1) = 0;
    a(2) = 0;
    a(3) = 0;
    a(4) = 0;
    a(5) = 0;
else
    a(1) = timelengthOfGrasp;
    a(2) = dist;
    a(3) = dist/timelengthOfGrasp;
    a(4) = dz;
    a(5) = dz/timelengthOfGrasp;
end


end