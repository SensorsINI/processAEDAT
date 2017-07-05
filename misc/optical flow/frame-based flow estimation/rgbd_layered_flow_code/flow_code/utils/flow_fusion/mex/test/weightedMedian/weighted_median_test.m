% function weighted_median_test

sz = [15^2 1];
x = randn(sz);
w = rand(sz);

tic
y1 = weighted_median(w, x);
toc

tic
y2 = weightedMedian(x, w);
toc

err = y1-y2;

max(abs(err(:)));