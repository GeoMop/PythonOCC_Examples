import scipy
import math
import numpy
from scipy import interpolate
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


x = [1, 2, 3, 4, 5, 6]
y = [10, 20, 30]

Y = numpy.array([[i]*len(x) for i in y])
X = numpy.array([x for i in y])
Z = numpy.array([[2.3, 3.4, 5.6, 7.8, 9.6, 11.2],
                 [24.3, -5.4, 7.6, 9.8, 11.6, 13.2],
                 [6.3, 7.4, 8.6, 10.8, 13.6, 15.2]])

# Bspline without optimization
tck,fp,ior,msg = interpolate.bisplrep(X, Y, Z, xb=min(x), xe=max(x), yb=min(y), ye=max(y), kx=5, ky=2, full_output=1)

# It seems that weight does not influence surface
#W = numpy.array([1000, 1000, 1000, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1000, 1000, 1000])
#tck,fp,ior,msg = interpolate.bisplrep(x=X, y=Y, z=Z, w=W, xb=min(x), xe=max(x), yb=min(y), ye=max(y), kx=3, ky=2, full_output=1)

# Knots
#TX = numpy.array([1, 1, 1, 1, 3, 6, 6, 6, 6])
#TY = numpy.array([10, 10, 10, 30, 30, 30])
#tck,fp,ior,msg = interpolate.bisplrep(X, Y, Z, xb=min(x), xe=max(x), yb=min(y), ye=max(y), kx=3, ky=2, task=-1, tx=TX, ty=TY, full_output=1)

print 'tck: ', tck
print 'fp: ', fp
print 'ior: ', ior
print 'msg: ', msg

xnew = numpy.arange(1.0, 6, 0.1)
ynew = numpy.arange(10.0, 30,0.5)

xx,yy = numpy.meshgrid(xnew, ynew)

znew = interpolate.bisplev(xnew, ynew, tck)

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter(X, Y, Z, color='red')

# print 'xx: ', len(xx), 'xnew: ', len(xnew)
# print 'yy: ', len(yy), 'ynew: ', len(ynew)
# print 'znew: ', len(znew[0][:]), len(znew[:][0])

# print 'x> ', xx
# print 'y> ', yy
# print 'z> ', znew

ax.plot_surface(xx.transpose(), yy.transpose(), znew, color='gray', shade=True, antialiased=True, rstride=1, cstride=1)
plt.show()
