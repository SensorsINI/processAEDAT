function [R indx] = imwarpmtx(u,v)

% create a sparse matrix to perform warping with flow u, v
% indx indicates those out boundary pixels

%   Authors: Deqing Sun, Department of Computer Science, Brown University
%            Stefan Roth, Department of Computer Science, TU Darmstadt
%   Contact: dqsun@cs.brown.edu, sroth@cs.tu-darmstadt.de
%   $Date: 2008-6-13 $
%   $Revision$

% Copyright 2008-, Brown University, TU Darmstadt
%
%                         All Rights Reserved
%
% Permission to use, copy, modify, and distribute this software and its
% documentation for any purpose other than its incorporation into a
% commercial product is hereby granted without fee, provided that the
% above copyright notice appear in all copies and that both that
% copyright notice and this permission notice appear in supporting
% documentation, and that the name of the author and Brown University not be used in
% advertising or publicity pertaining to distribution of the software
% without specific, written prior permission.
%
% THE AUTHOR AND BROWN UNIVERSITY DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
% INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR ANY
% PARTICULAR PURPOSE.  IN NO EVENT SHALL THE AUTHOR OR BROWN UNIVERSITY BE LIABLE FOR
% ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
% WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
% ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
% OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE. 

sz = size(u);

A = speye(prod(sz));

[x,y]=meshgrid(1:sz(2), 1:sz(1));

rows = y + v;   % vertical
cols = x + u;   % horizontal 

% out of boundary processing, return these indices?

brows = floor(rows);
bcols = floor(cols);
trows = ceil(rows); 
tcols = ceil(cols); 

if nargout == 2
    indx = (brows<1)|(brows>sz(1)) | (bcols < 1)|(bcols > sz(2)) | ...
        (trows<1)|(trows>sz(1)) | (tcols < 1)|(tcols > sz(2));
end;

brows(brows < 1) = 1; brows(brows > sz(1)) = sz(1);
bcols(bcols < 1) = 1; bcols(bcols > sz(2)) = sz(2);
trows(trows < 1) = 1; trows(trows > sz(1)) = sz(1);
tcols(tcols < 1) = 1; tcols(tcols > sz(2)) = sz(2);
   
% brows = floor(rows); brows(brows < 1) = 1; brows(brows > sz(1)) = sz(1);
% bcols = floor(cols); bcols(bcols < 1) = 1; bcols(bcols > sz(2)) = sz(2);
% trows = ceil(rows); trows(trows < 1) = 1; trows(trows > sz(1)) = sz(1);
% tcols = ceil(cols); tcols(tcols < 1) = 1; tcols(tcols > sz(2)) = sz(2);

ralpha = rows - brows;
calpha = cols - bcols;

R = sparse(prod(sz), prod(sz));

% bottom, bottom
ind = brows + sz(1)*(bcols-1);
alpha = (1 - ralpha).*(1 - calpha);

D = sparse(1:numel(alpha), 1:numel(alpha), alpha(:));
R = R + D * A(ind(:), :);

% $$$     tmp = alpha;

% top, bottom
ind = trows + sz(1)*(bcols-1);
alpha = ralpha .* (1 - calpha);

D = sparse(1:numel(alpha), 1:numel(alpha), alpha(:));
R = R + D * A(ind(:), :);

% $$$     tmp = tmp + alpha;

% bottom, top
ind = brows + sz(1) * (tcols-1);
alpha = (1 - ralpha).*calpha;

D = sparse(1:numel(alpha), 1:numel(alpha), alpha(:));
R = R + D * A(ind(:), :);

% $$$     tmp = tmp + alpha;

% top, top
ind = trows + sz(1) * (tcols-1);
alpha = ralpha .* calpha;

D = sparse(1:numel(alpha), 1:numel(alpha), alpha(:));
R = R + D * A(ind(:), :);

% $$$     tmp = tmp + alpha;
% $$$     tmp

