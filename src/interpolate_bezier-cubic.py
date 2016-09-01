import numpy as np
from numpy.linalg import inv
import matplotlib.pyplot as plt
import sys
import math

eps = sys.float_info.epsilon

def compute_points_params(x, y, z=None):
    """
    This function return vector t with parametrisation of points
    """
    # Compute distances of Points from begining of curve
    di = 0.0
    d = [di,]
    for i in range(1, n):
        if z is None:
            dest = math.sqrt( (x[i] - x[i - 1])**2 + (y[i] - y[i - 1])**2 )
        else:
            dest = math.sqrt( (x[i] - x[i - 1])**2 + (y[i] - y[i - 1])**2 + (z[i] - z[i - 1])**2 )
        di += dest
        d.append(di)

    # Computer values of parameter t mapping t_{i} to point P_{i}
    t = []
    for item in d:
        t.append(item/d[-1])
    t = np.array(t)

    return t

def construct_param_matrix(t):
    """
    Construct matrix of parametrisation for least square solution
    """
    t3 = np.array([item**3 for item in t])
    t2 = np.array([item**2 for item in t])
    t1 = np.array([item for item in t])
    t0 = np.array([1 for item in t])
    return np.mat([t3, t2, t1, t0]).transpose()

# Coordinates of points P=[P_{1}, P_{2}, ..., P_{n}]
x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
y = np.array([3.1, 3.5, 3.7, 3.4, 3.2])

n = len(x)

# Base matrix of Bezier cubic curve
M = np.matrix([
    [-1, 3, -3, 1],
    [3, -6, 3, 0],
    [-3, 3, 0, 0],
    [1, 0, 0, 0]])
iM = inv(M)

# Compute array of t params
t = compute_points_params(x, y)

# Construct matrix T
T = construct_param_matrix(t)
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

dt = 0.02

# Draw Bezier curve aproximating points
Px = []
Py = []
t = 0.0
while t < 1.0 + dt:
    P = np.array([t**3, t**2, t, 1]) * M * np.bmat([Cx, Cy])
    Px.append(P[0, 0])
    Py.append(P[0, 1])
    t += dt
plt.plot(Px, Py, c='red')

# Draw Bezier curve aproximating points and intersecting first and
# last point
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
