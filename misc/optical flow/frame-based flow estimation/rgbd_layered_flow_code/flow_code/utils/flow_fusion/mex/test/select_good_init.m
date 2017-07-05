function layer_uv = select_good_init(iSeq)

K  = 4;
% iSeq = 17;
fn = sprintf('/u/dqsun/research/program/nips10_flow/data/init/classic+nl/train_%03d.flo', iSeq);
uv = readFlowFile(fn);
fn = sprintf('/u/dqsun/research/program/nips10_flow/data/init/classic+nl-backward/train_%03d.flo', iSeq);
uv2 = readFlowFile(fn);

n_candidate = 10;

for i = 1:n_candidate
    [A{i} score(i) segs{i}] =robust_fit_affine_motion(uv, K);
end;

[tmp ind] = min(score);


seg = segs{ind(1)};
A1 = A{ind(1)};
figure; imagesc(seg); title(num2str(score(ind(1))));

for i = 1:n_candidate
    [A{i} score2(i) segs2{i}] =robust_fit_affine_motion(uv2, K);
end;

[tmp ind] = min(score2);

A2 = A{ind(1)};
seg2 = segs2{ind(1)};

%Make two segmentation consistent to each other
nL = K;
c = ones(nL,1);
for i =1:nL
%     dis = sum((centers + repmat(centers2(i,:), [nL 1])).^2, 2);
    dis = sum( sum( (A1+ repmat(A2(:, i, :), [1 nL 1])).^2, 3), 1);
    [tmp ind] = min(dis);
    c(i) = ind;
end;
seg3 = seg2;
A3 = A2;
for i =1:nL
    seg2(seg3==i) = c(i);
    A2(:,c(i), :) = A3(:,i, :);
end;
% score
% score2

figure; imagesc(seg2); title(num2str(min(score2)));

% Test temporal consistency
tmp = warp_backward(uv, seg2, 'nearest');
tmp(isnan(tmp)) = seg(isnan(tmp));
figure;imagesc(tmp~=seg)
sum(tmp(:)~=seg(:))/length(seg(:))


if nargout > 0
    layer_uv = affine2layer(A{ind}, [size(uv,1) size(uv,2)]);
end;

function layer_uv = affine2layer(A, sz)
% convert the affine motion parameters of each layer into dense flow field

[X Y] = meshgrid(1:sz(2), 1:sz(1));
for j = 1:size(A,2)
    u2 = X*A(1,j,1)+Y*A(2,j,1)+A(3,j,1);
    v2 = X*A(1,j,2)+Y*A(2,j,2)+A(3,j,2);
    layer_uv{j} = cat(3, u2, v2);
end;