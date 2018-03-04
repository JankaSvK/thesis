import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

ax = plt.axes(projection='3d')
plt.ion()

points = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [1, 0, 1]]
for i in range(1, len(points)):
    last, curr = points[i-1], points[i]
    ax.plot([last[0], curr[0]], [last[1], curr[1]], [last[2], curr[2]])
    plt.pause(0.05)
plt.show(block=True)