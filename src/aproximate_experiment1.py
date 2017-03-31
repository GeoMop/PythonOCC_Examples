x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
y = [0.50, 0.45, 0.43, 0.42, 0.40, 0.39, 0.41, 0.47, 0.51, 0.54,
     0.51, 0.48, 0.45, 0.49, 0.51, 0.58, 0.61, 0.65, 0.69, 0.67]

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

tck,u = interpolate.splprep([x,y], k=5)

# Create smooth polyline representation of bspline
# used for ploting
unew = np.arange(0, 1.01, 0.01)
out = interpolate.splev(unew, tck)

# Plot output
plt.figure()
plt.plot(x, y, 'o', out[0], out[1])
plt.show()