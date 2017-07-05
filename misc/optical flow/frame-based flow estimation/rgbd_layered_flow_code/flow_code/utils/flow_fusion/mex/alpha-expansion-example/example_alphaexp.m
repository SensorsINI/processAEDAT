load peppers
figure
title('original')
imshow(pep/255)
figure
imshow(pep_noisy/255)
title('noisy')
drawnow
[labeling,energy]=alpha_expansion_(pep_noisy,0:255,@my_squared_difference,50);
figure
title(strcat('denoised, energy = ',num2str(energy)))
imshow(labeling/255);