import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from RodriguezTransformation import Points

# Reference face (3D quad, from your dump)
referencePoints = np.array([
    [7.50399077832747, -38.44055281049395, -33.892940941081044],
    [7.063985796880393, -45.095787817952775, -26.44215288800932],
    [-51.151429778911165, -15.888305555724427, -17.21258078219642],
    [-51.59143476035824, -22.543540563183257, -9.761792729124696],
])

# Target face (flat 2D rectangle in XY plane)
targetPoints = np.array([
    [-3.0, -2.598, 0.0],
    [83.49, -2.598, 0.0],
    [83.49, 80.05, 0.0],
    [-3.0, 80.05, 0.0],
])

# Compute alignment
points = Points(referencePoints, targetPoints)
R = points.compute()

rotated_target = targetPoints @ R.T
translation = referencePoints.mean(axis=0) - rotated_target.mean(axis=0)
aligned_target = rotated_target + translation

# Plot
fig = plt.figure(figsize=(12, 6))

# Before
ax1 = fig.add_subplot(121, projection="3d")
ax1.add_collection3d(Poly3DCollection([referencePoints], alpha=0.3, facecolor="blue"))
ax1.add_collection3d(Poly3DCollection([targetPoints], alpha=0.3, facecolor="red"))
ax1.set_title("Before Alignment")

# After
ax2 = fig.add_subplot(122, projection="3d")
ax2.add_collection3d(Poly3DCollection([referencePoints], alpha=0.3, facecolor="blue"))
ax2.add_collection3d(Poly3DCollection([aligned_target], alpha=0.3, facecolor="green"))
ax2.set_title("After Alignment")

plt.show()
