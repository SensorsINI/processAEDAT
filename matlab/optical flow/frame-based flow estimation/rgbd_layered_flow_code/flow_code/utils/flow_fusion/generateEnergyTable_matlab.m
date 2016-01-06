function [pairwise_terms] = generateEnergyTable_matlab(cliques,potential_func,fp_0,fp_1)
%%
% does not apply if potential func is C mex funciton that modify its input
% via pointer
mytruthtable=[0 0;0 1;1 0;1 1];
%inputV = generatePotentialVectors(fp_0,fp_1,mytruthtable',cliques);
inputV  = zeros(size(cliques,1)*4, 2);
generatePotentialVectorsV2(fp_0,fp_1,mytruthtable',cliques, inputV);

c = cliques';

sz = size(inputV,1);
p_tmp = ones(size(inputV,2)*2,size(inputV,1));
p_tmp(1:2,1:4:end) = c;
p_tmp(1:2,2:4:end) = c;
p_tmp(1:2,3:4:end) = c;
p_tmp(1:2,4:4:end) = c;

p_tmp(3:4,:) = inputV';

% tmp = ones(size(inputV));
% tmp(1:4:end, :) = cliques;
% tmp(2:4:end, :) = cliques;
% tmp(3:4:end, :) = cliques;
% tmp(4:4:end, :) = cliques;
% 
% % tmp      = potential_func([tmp';inputV']);
% % pairwise = reshape(tmp,4,[]);
% % 
% % pairwise_terms = [cliques' ; pairwise];
% 
% %ti = tmp';
% %iv = inputV';
% %p_in = [tmp'; inputV'];
% p_in2 = [tmp inputV]';
p = potential_func(p_tmp);
pt_r = reshape(p, 4, []);
pairwise_terms = [cliques'; pt_r];

%pairwise_terms = [cliques' ; reshape( potential_func([tmp';inputV']), 4,[])];

clear tmp inputV;


