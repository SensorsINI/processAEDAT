function local_smoothed_histogram_filter_test
%%

sz = 100*[1 1];
im = 100*ones(sz);
im(end/2:end, end/2:end) = 50;
im(1:end/2, 1:end/2) = 50;
im = im+randn(sz)*1;
imo = local_smoothed_histogram_filter(im);

% figure; imagesc(imo);
% %%
figure; imshow(im, []);
figure; imshow(imo, []);
%%
imo2 = medfilt2(im, [13 13], 'symmetric');
figure; imshow(imo2, []); 

%%
figure; imshow([imo imo2], []);
figure; imshow(imo2~=imo);