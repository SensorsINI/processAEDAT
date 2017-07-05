function [this data] = pre_process_data(this)
%%
% texture decomposition
% build up pyramid of imgaes, segemntation, flow etc. 

% Preprocess input (gray) sequences
if this.texture
    images  = structure_texture_decomposition_rof( this.images,...
        1/8, 100, this.alp);
elseif this.fc
    % Laplacian in flowfusion
    f = fspecial('gaussian', [5 5], 1.5); % std = 1 is better
    images  = this.images- this.alp*imfilter(this.images, f, 'symmetric');
    images  = scale_image(images, 0, 255);
else
    images  = scale_image(this.images, 0, 255);
end;

sz = size(images);
sz = sz(1:2);

if this.auto_level % Automatic determine pyramid levels
    % largest size around 16
    N1 = 1 + floor( log(max(size(images, 1), size(images,2))/16)/...
        log(this.pyramid_spacing) );
    % smaller size shouldn't be less than 6
    N2 = 1 + floor( log(min(size(images, 1), size(images,2))/6)/...
        log(this.pyramid_spacing) );
    this.pyramid_levels  =  min(N1, N2);
    
    if this.old_auto_level
        this.pyramid_levels  =  1 + floor( log(min(size(images, 1),...
            size(images,2))/16) / log(this.pyramid_spacing) );
    end;
    
    if this.unEqualSampling
        minWH = 16; 
        this.pyramid_levels  =  1 + floor( log(max(sz)/minWH)...
            / log(this.pyramid_spacing) );
        
        tmp = exp(log(min(sz)/max(sz)*this.pyramid_spacing^(this.pyramid_levels-1))...
            /(this.pyramid_levels-1) );
        if sz(1) > sz(2)
            spacing = [this.pyramid_spacing tmp];
        else
            spacing = [tmp this.pyramid_spacing];
        end
        
    end            
    
    if this.display
        fprintf('%d-level pyramid used\n', this.pyramid_levels);
    end;
end;

factor            = sqrt(2);

if this.unEqualSampling
    %fprintf('unequal sampling\n');
    data.pyramid_images    = compute_image_pyramid_unequal(images, ...
        this.pyramid_levels, spacing, factor);
    
    % For segmentation purpose
    data.org_pyramid_images = compute_image_pyramid_unequal(this.images,...
        this.pyramid_levels, spacing, factor);
    data.org_color_pyramid_images = compute_image_pyramid_unequal(...
        this.color_images, this.pyramid_levels, spacing, factor);
else
    
    % Construct image pyramid, using filter setting in Bruhn et al in
    % "Lucas/Kanade.." (IJCV2005') page 218
    % For gnc stage 1

    smooth_sigma      = sqrt(this.pyramid_spacing)/factor;
    f                 = fspecial('gaussian',...
        2*round(1.5*smooth_sigma) +1, smooth_sigma);
    data.pyramid_images    = compute_image_pyramid(images, f,...
        this.pyramid_levels, 1/this.pyramid_spacing);
    
    % For segmentation purpose
    data.org_pyramid_images = compute_image_pyramid(this.images, f,...
        this.pyramid_levels, 1/this.pyramid_spacing);
    data.org_color_pyramid_images = compute_image_pyramid(this.color_images,...
        f, this.pyramid_levels, 1/this.pyramid_spacing);

end
% For gnc stage 2 to gnc_iters
smooth_sigma      = sqrt(this.gnc_pyramid_spacing)/factor;
f                 = fspecial('gaussian',...
    2*round(1.5*smooth_sigma) +1, smooth_sigma);
data.gnc_pyramid_images= compute_image_pyramid(images,...
    f, this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing);

% For segmentation/weighted median filtering
data.org_gnc_pyramid_images = compute_image_pyramid(this.images,...
    f, this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing);
data.org_color_gnc_pyramid_images = compute_image_pyramid(this.color_images,...
    f, this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing);



%%
%   % Preprocess input (gray) sequences
%   if this.texture      
%       %images  = scale_image(this.images, 0, 255);
% %       f = fspecial('gaussian', [3 3], 0.5);  % li & huttenlocher
% %       images  = imfilter(this.images, f, 'symmetric');
% %       images  = structure_texture_decomposition_rof(images, 1/8, 100, this.alp);
% %       fprintf('Gaussian(0.5), followed by texture decomposition\n');
%       
% %       % Perform ROF structure texture decomposition 
% %        images  = structure_texture_decomposition_rof( this.images,...
% %            1/8, 100, this.alp, this.isScale);
% %        
% %        % fixed scale
% %        if ~this.isScale
% %            images = images*250/0.8;
% %        end;
% 
% 
%        images  = structure_texture_decomposition_rof( this.images,...
%            1/8, 100, this.alp);
%        
% %       fprintf('texture \n');
% 
% %         f = fspecial('gaussian', [5 5], 1);  % Li & Huttenlocher
% %         %f = fspecial('gaussian', [3 3], 0.5);  % Li & Huttenlocher
% %         images  = imfilter(this.images, f, 'symmetric');
% %       
% %       images  = scale_image(images, 0, 255);
% %       fprintf('Gaussian(0.5) \n');
%              
%   elseif this.fc     
%       
%       % Laplacian in flowfusion
%       f = fspecial('gaussian', [5 5], 1.5);
%       %f = fspecial('gaussian', [3 3], 1);
%       images  = this.images- this.alp*imfilter(this.images, f, 'symmetric');
%       
%       % Gaussian pre-filering
%       %         f = fspecial('gaussian', [3 3], 0.5);  % Li & Huttenlocher
%       %         images  = imfilter(this.images, f, 'symmetric');
%       
%       % Sobel edge magnitude
%       %         Dy = fspecial('sobel')/8;
%       %         Dx = Dy';
%       %         Ix = imfilter(this.images, Dx, 'symmetric');
%       %         Iy = imfilter(this.images, Dy, 'symmetric');
%       %         images = sqrt(Ix.^2 + Iy.^2);
%       
%       images  = scale_image(images, 0, 255);
%   else
%       images  = scale_image(this.images, 0, 255);
%   end;
%     
%   if this.auto_level
%       % Automatic determine pyramid level
%       
%       % largest size around 16
%       N1 = 1 + floor( log(max(size(images, 1), size(images,2))/16)/...
%           log(this.pyramid_spacing) );
%       % smaller size shouldn't be less than 6
%       N2 = 1 + floor( log(min(size(images, 1), size(images,2))/6)/...
%           log(this.pyramid_spacing) );
%       
% %       if this.display
% %           fprintf('%d, %d \n', N1, N2);
% %       end;
%       % satisfies at least one(N2)
%       this.pyramid_levels  =  min(N1, N2);
% 
%       if this.old_auto_level
%           this.pyramid_levels  =  1 + floor( log(min(size(images, 1), size(images,2))/16) / log(this.pyramid_spacing) );
%       end;
%       if this.display
%           fprintf('%d-level pyramid used\n', this.pyramid_levels);
%       end;
%       
%   end;
%   
%   % Construct image pyramid, using filter setting in Bruhn et al in
%   % "Lucas/Kanade.." (IJCV2005') page 218   
%   % For gnc stage 1    
%   factor            = sqrt(2);  % sqrt(3) worse
%   % or sqrt(3) recommended by Manuel Werlberger 
%   smooth_sigma      = sqrt(this.pyramid_spacing)/factor;   
%   f                 = fspecial('gaussian',...
%       2*round(1.5*smooth_sigma) +1, smooth_sigma);        
%   pyramid_images    = compute_image_pyramid(images, f,...
%       this.pyramid_levels, 1/this.pyramid_spacing);
% 
% % % %   disp('ROF every level');
% % % %   % perform ROF on each image pyramid
% % % %   gray_pyramid_images    = compute_image_pyramid(this.images, f, this.pyramid_levels, 1/this.pyramid_spacing);
% % % %   for l = 1:length(gray_pyramid_images)
% % % %       pyramid_images{l}  = structure_texture_decomposition_rof(gray_pyramid_images{l}, 1/8, 100, this.alp);
% % % %   end;
%     
%   
% 
%   % For segmentation purpose
%   org_pyramid_images = compute_image_pyramid(this.images, f,...
%       this.pyramid_levels, 1/this.pyramid_spacing);
%   org_color_pyramid_images = compute_image_pyramid(this.color_images,...
%       f, this.pyramid_levels, 1/this.pyramid_spacing);
% 
%   % For gnc stage 2 to gnc_iters  
%   smooth_sigma      = sqrt(this.gnc_pyramid_spacing)/factor;
%   f                 = fspecial('gaussian',...
%       2*round(1.5*smooth_sigma) +1, smooth_sigma);        
%   gnc_pyramid_images= compute_image_pyramid(images,...
%       f, this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing); 
% 
%     
%   % For segmentation/weighted median filtering
%   org_gnc_pyramid_images = compute_image_pyramid(this.images,...
%       f, this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing);   
%   org_color_gnc_pyramid_images = compute_image_pyramid(this.color_images,...
%       f, this.gnc_pyramid_levels, 1/this.gnc_pyramid_spacing);   