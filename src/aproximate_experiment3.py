import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splev, splrep

#x = np.linspace(0, 10, 10)
#y = np.sin(x)

x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
y = [0.50, 0.45, 0.43, 0.42, 0.40, 0.39, 0.41, 0.47, 0.51, 0.54,
     0.51, 0.48, 0.45, 0.49, 0.51, 0.58, 0.61, 0.65, 0.69, 0.67]

tck = splrep(x, y)
print(tck)
#x2 = np.linspace(0, 10, 200)
x2 = np.linspace(0, 19, 200)
y2 = splev(x2, tck)
plt.plot(x, y, 'o', x2, y2)
plt.show()