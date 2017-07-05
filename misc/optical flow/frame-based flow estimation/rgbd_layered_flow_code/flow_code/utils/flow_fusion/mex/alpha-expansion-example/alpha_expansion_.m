%% Alpha expansion for image denoising
% [fp,current_energy] = alpha_expansion_(img,labelset,prior_func,lambda)
% IN:
%   img - noisy (grayscale) image
%   labelset    -   1xn matrix, e.g. 0:255 for 8Bit grayscale images
%   prior_func  -   @function_handle, potential function for the prior, have a
%                   look at my_squared_difference.m, how to define new functions
%   lambda      -   prior gain
% OUT:
%   fp          - alpha-expansion result
%   current_energy - energy for labeling fp

function [fp,current_energy] = alpha_expansion_(img,labelset,prior_func,lambda)
[m,n] = size(img);
%% define cliques
vert = im2col((reshape(1:m*n,m,n)),[2 1])';%vertical
hor = im2col((reshape(1:m*n,m,n)),[1 2])';%horizontal
cliques = [vert ; hor];

%% initialize energy
current_energy = 1e32;

%% initialize labeling
fp = zeros(m,n);

%% start alpha_expansion
while true
    for loop=1 : size(labelset,2)
        alpha = labelset(loop);
        current_proposal = repmat(alpha,m,n);
        %in case of pairwise mrfs, we do not split the potentials to unary
        %and pairwise terms, we simply use the energytable
        %[E00,E01,E10,E11], which can be represented by single pairwise
        %term
        pairwise_terms = generateEnergyTable(cliques,prior_func,fp,current_proposal);
        pairwise_terms(3:end,:) = lambda *pairwise_terms(3:end,:);

        
        %Seteup dataterm, these are only unary terms
        Dp_fp =(fp - img ).^2; %energy, if pixel is set to current labeling fp
        Dp_alpha =(alpha - img ).^2;%energy, if pixel is set to alpha
        data_unary = [(1:m*n)' Dp_alpha(:) Dp_fp(:)]';%arrange dataterm to a 3xn matrix
        
        %call qpbo
        [new_fp,new_energy] = QPBO_all_in_one(m*n,data_unary,pairwise_terms);
        
        if (new_energy - current_energy) > .5
            %if we use potentials of type double, it is
            %possible that the new energy grows, because of numerical
            %issues, see QPBO documentation
            disp(strcat('WARNING: energy grows, (new_energy - current_energy) >'...
                ,num2str(new_energy - current_energy)));
        elseif (new_energy - current_energy) < -1
            success = 1;
            current_energy=new_energy;
        end
        disp(strcat('alpha=',num2str(alpha),', energy=',num2str(current_energy)));
        
        new_fp = reshape(new_fp(1:m*n),m,n);%reshape new_fp to given image size
        fp = (1-new_fp).* current_proposal+ new_fp .* fp;%generate new labeling
        
        
        
    end
    if success == 0
        disp('finished, energy did not shrink');
        break;
    end
    success = 0;
end


end

