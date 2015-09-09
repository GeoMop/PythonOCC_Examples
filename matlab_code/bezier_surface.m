clear all
close all
clc

% initialize

M = [-1 3 -3 1;3 -6 3 0;-3 3 0 0;1 0 0 0];

syms u
syms v

uv = [u^3; u^2; u; 1];
vv = [v^3; v^2; v;1];

Bu = M*uv
Bv = M*vv

% 1th patch

P(:,:,3) = [1 1 1 1;
            1 2 2 1;
            1 2 2 1;
            1 1 1 1];

P(:,:,2) = [0 0.75 0 0.75;
            1 1 1 1;
            2 2 2 2;
            3 2.5 2.5 3];

P(:,:,1) = [0 1 2 3;
            0.2 1 2 2.5;
            0.5 1 2 3.5;
            0 1 2 3];



bz(:,:,1) = transpose(Bu)*P(:,:,1)*Bv
bz(:,:,2) = transpose(Bu)*P(:,:,2)*Bv
bz(:,:,3) = transpose(Bu)*P(:,:,3)*Bv

steps = 10;
z1 = zeros(steps);

for k=1:3
    for i = 1:steps+1
        for j = 1:steps+1
            z1(i,j,k) = subs(bz(k),{'u','v'},{(i-1)/steps,(j-1)/steps});
        end
    end
end
        
% patch 2

P(:,:,3) = [1 1 1 1;
    1 -1 -1 1;
    1 -1 -1 1;
    1 1 1 1];

P(:,:,2) = [0 0.75 0 0.75;
    -1 -1 -1 -1;
    -2 -2 -2 -2;
    -3 -2.5 -2.5 -3];

P(:,:,1) = [0 1 2 3;
    0.2 1 2 2.5;
    0.5 1 2 3.5;
    0 1 2 3];


bz(:,:,1) = transpose(Bu)*P(:,:,1)*Bv
bz(:,:,2) = transpose(Bu)*P(:,:,2)*Bv
bz(:,:,3) = transpose(Bu)*P(:,:,3)*Bv

z2 = zeros(steps);

for k=1:3
    for i = 1:steps+1
        for j = 1:steps+1
            z2(i,j,k) = subs(bz(k),{'u','v'},{(i-1)/steps,(j-1)/steps});
        end
    end
end




surf(z1(:,:,1),z1(:,:,2),z1(:,:,3))        
hold on
surf(z2(:,:,1),z2(:,:,2),z2(:,:,3)) 
plot3(P(:,:,1),P(:,:,2),P(:,:,3),'.') 
hold off





