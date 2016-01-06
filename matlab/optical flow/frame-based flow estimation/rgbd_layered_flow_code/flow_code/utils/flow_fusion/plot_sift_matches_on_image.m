function plot_sift_matches_on_image(matches, im1, fa, fb)
%%
figure; imshow(uint8(im1)); hold on;
nMatches = size(matches,2);
for i=1:nMatches;
    xa = fa(1, matches(1,i));
    ya = fa(2, matches(1,i));
    xb = fb(1, matches(2,i));
    yb = fb(2, matches(2,i));
    
    plot(xa, ya, 'o');
    line([xa xb], [ya yb], 'Color', 'r');
    
end