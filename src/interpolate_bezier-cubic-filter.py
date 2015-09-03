import numpy as np
from numpy.linalg import inv
import matplotlib.pyplot as plt
import sys

eps = sys.float_info.epsilon

# Coordinates of points P=[P_{1}, P_{2}, ..., P_{n}]
x = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0])
y = np.array([3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.1, 3.2, 3.4, 3.7, 3.9,  4.0,  4.1,  4.1,  4.1,  4.1])

# Estimation of t parameters mapping t_{i} to point P_{i}
t = np.linspace(0.0, 1.0, len(x))

new_t = []
new_x = []
new_y = []
yi_1 = None
i = 0
li = 0
di = 2
for yi in y:
    if yi_1 is None:
        new_t.append(t[i])
        new_x.append(x[i])
        new_y.append(y[i])
    elif abs(yi - yi_1) > eps or i - li > di:
        new_t.append(t[i])
        new_x.append(x[i])
        new_y.append(y[i])
        li = i
    yi_1 = yi
    i += 1
if new_t[-1] != t[-1]:
    new_t.append(t[i - 1])
    new_x.append(x[i - 1])
    new_y.append(y[i - 1])

x = np.array(new_x)
y = np.array(new_y)
t = np.array(new_t)

n = len(x)

print x
print y
print t

# Base matrix of Bezier cubic curve
M = np.matrix([
    [-1, 3, -3, 1],
    [3, -6, 3, 0],
    [-3, 3, 0, 0],
    [1, 0, 0, 0]])
iM = inv(M)

t3 = np.array([item**3 for item in t])
t2 = np.array([item**2 for item in t])
t1 = np.array([item for item in t])
t0 = np.array([1 for item in t])

T = np.mat([t3, t2, t1, t0]).transpose()
tT = T.transpose()

X = np.mat(x).transpose()
Y = np.mat(y).transpose()

Cx = iM * inv(tT * T) * tT * X
Cy = iM * inv(tT * T) * tT * Y

diff_x0 = x[0] - Cx[0]
diff_xn = x[n - 1] - Cx[3]

diff_y0 = y[0] - Cy[0]
diff_yn = y[n - 1] - Cy[3]

dy = ( diff_y0 + diff_yn ) / 2.0

Kx = np.array([x[0], Cx[1], Cx[2], x[n - 1]])
Ky = np.array([y[0], Cy[1] - dy, Cy[2] - dy, y[n - 1]])

# Draw coordinates of P points
plt.scatter(x,y)

Px = []
Py = []

t = 0.0
dt = 0.02
while t < 1.0 + dt:
    P = np.array([t**3, t**2, t, 1]) * M * np.bmat([Cx, Cy])
    Px.append(P[0, 0])
    Py.append(P[0, 1])
    t += dt

plt.plot(Px, Py, c='red')

Px = []
Py = []

t = 0.0
while t < 1.0 + dt:
    P = np.array([t**3, t**2, t, 1]) * M * np.mat([Kx, Ky]).transpose()
    Px.append(P[0, 0])
    Py.append(P[0, 1])
    t += dt

plt.plot(Px, Py, c='blue')

plt.show()
