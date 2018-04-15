from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np

from Arrow3D import Arrow3D


def join(a, b):
    return [[a[0], b[0]], [a[1], b[1]], [a[2], b[2]]]

fig = plt.figure()
ax = fig.gca(projection='3d')

ax.axis('off')

# Set axis limits

ax.set_xlim3d(-4, 4)
ax.set_ylim3d(-4, 4)
ax.set_zlim3d(-4, 4)

f = 1.7

# Camera points

A = [-f, 0, -1, 0]
B = [f, 0, -1, 0]
C = [f, 0, 1, 0]
D = [-f, 0, 1, 0]

# Camera project point

T = [0, -4, 0, -2]

cam_col = 'black'

first = False

if first:
    ax.plot(*join(A, B), color=cam_col, linestyle='dashed')
    ax.plot(*join(D, A), color=cam_col, linestyle='dashed')
    ax.plot(*join(T, A), color=cam_col, linestyle='dashed')
    ax.plot(*join(B, C), cam_col)
    ax.plot(*join(T, B), cam_col)

else:
    ax.plot(*join(A, B), color=cam_col, linestyle='dashed')
    ax.plot(*join(D, A), color=cam_col)
    ax.plot(*join(T, A), color=cam_col)
    ax.plot(*join(B, C), cam_col, linestyle='dashed')
    ax.plot(*join(T, B), cam_col, linestyle='dashed')

ax.plot(*join(C, D), cam_col)
ax.plot(*join(T, C), cam_col)
ax.plot(*join(T, D), cam_col)


if first: # draw axes
    origin = T
    arr_len = 3

    axe_color = 'gray'

    Ax, Ay, Az = list(origin), list(origin), list(origin)
    Ax[0] += arr_len
    Ay[1] += arr_len + 6
    Az[2] += -arr_len

    y = Arrow3D(*join(origin, Ay), mutation_scale=20, lw=1, arrowstyle="-|>", color=axe_color)
    x = Arrow3D(*join(origin, Ax), mutation_scale=20, lw=1, arrowstyle="-|>", color=axe_color)
    z = Arrow3D(*join(origin, Az), mutation_scale=20, lw=1, arrowstyle="-|>", color=axe_color)


    ax.add_artist(x)
    ax.add_artist(y)
    ax.add_artist(z)

    e = 0.1

    ax.text(Ay[0] + e, Ay[1] + e, Ay[2] + e, 'z', color=axe_color)
    ax.text(Ax[0] + e, Ax[1] + e, Ax[2] + e, 'x', color=axe_color)
    ax.text(Az[0] + 2*e, Az[1] + e, Az[2] + e, 'y', color=axe_color)



# Plot the surface.

plt.show()

