function body = generateBody()
rawlist = imread('body', 'gif');
index = 1;
x_size = size(rawlist,1);
y_size = size(rawlist,2);
body_size = size(find(rawlist),1);
body = zeros(2,body_size);
for x = 1: x_size
    for y = 1: y_size
        if rawlist(x,y) == 1
            body(2,index) = round(x_size/2)-x;
            body(1,index) = y-round(y_size/2);
            index = index+1;
        end
    end
end
end