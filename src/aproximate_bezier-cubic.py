import numpy as np
from numpy.linalg import inv

# Coordinates of points P=[P_{1}, P_{2}, ..., P_{n}]
x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
y = np.array([3.1, 3.5, 3.7, 3.4, 3.2])

# Estimation of t parameters mapping t_{i} to point P_{i}
t = np.array([0.0, 0.25, 0.5, 0.75, 1.0])

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

print Cx
print Cy
