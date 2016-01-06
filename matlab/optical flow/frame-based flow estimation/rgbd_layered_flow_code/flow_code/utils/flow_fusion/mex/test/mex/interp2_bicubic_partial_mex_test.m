% function interp2_bicubic_partial_mex_test

n = 400;

Z = rand(n,n)*255;
u  = randn(n,n);
v  = randn(n,n);

[X Y] = meshgrid(1:n, 1:n);

XI = X+u;
YI = Y+v;
%%
tic
[ZI, ZXI, ZYI] = interp2_bicubic_partial_mex(Z, XI, YI);
%ZI = interp2_bicubic_partial_mex(Z, XI, YI);
toc


tic
[ZI2, ZXI2, ZYI2] = interp2_bicubic(Z, XI, YI);
%ZI2= interp2_bicubic(Z, XI, YI);
toc

% err = [ZI(:)-ZI2(:)];
% max(abs(err(:)))

err = [ZI(:)-ZI2(:);ZXI(:)-ZXI2(:); ZYI(:)-ZYI2(:)];
max(abs(err(:)))


%% Print out c code for sparse matrix multiplication

%%

% w=[        1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
%     0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,
%     -3,  0,  0,  3,  0,  0,  0,  0, -2,  0,  0, -1,  0,  0,  0,  0,
%     2,  0,  0, -2,  0,  0,  0,  0,  1,  0,  0,  1,  0,  0,  0,  0,
%     0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
%     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,
%     0,  0,  0,  0, -3,  0,  0,  3,  0,  0,  0,  0, -2,  0,  0, -1,
%     0,  0,  0,  0,  2,  0,  0, -2,  0,  0,  0,  0,  1,  0,  0,  1,
%     -3,  3,  0,  0, -2, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
%     0,  0,  0,  0,  0,  0,  0,  0, -3,  3,  0,  0, -2, -1,  0,  0,
%     9, -9,  9, -9,  6,  3, -3, -6,  6, -6, -3,  3,  4,  2,  1,  2,
%     -6,  6, -6,  6, -4, -2,  2,  4, -3,  3,  3, -3, -2, -1, -1, -2,
%     2, -2,  0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
%     0,  0,  0,  0,  0,  0,  0,  0,  2, -2,  0,  0,  1,  1,  0,  0,
%     -6,  6, -6,  6, -3, -3,  3,  3, -4,  4,  2, -2, -2, -2, -1, -1,
%     4, -4,  4, -4,  2,  2, -2, -2,  2, -2, -2,  2,  1,  1,  1,  1];
% 
% 
% for i = 1:size(w,1)
%     
%     fprintf('coef[%d] = ', i-1);
%     for j=1:size(w,2);
%         if w(i,j)==1
%             fprintf('+ tmpI[%d]', j-1);
%         elseif w(i,j)==-1
%             fprintf('- tmpI[%d]', j-1);
%         elseif w(i,j)>0
%             fprintf(' + %d *tmpI[%d]', w(i,j), j-1);
%         elseif w(i,j)<0
%             fprintf(' - %d *tmpI[%d]', -w(i,j), j-1);
%         end;
%     end;
%     fprintf(';\n');
% end;
