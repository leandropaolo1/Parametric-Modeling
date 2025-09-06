import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from RodriguezTransformation import Points

points = Points()
R = points.rotation()
newTarget = points.target @ R.T
newTargetTranslation = points.point - newTarget.mean(axis=0)
alignedNewTarget = newTarget + newTargetTranslation

fig = plt.figure(figsize=(12, 6))

# Before alignment
ax1 = fig.add_subplot(121, projection="3d")
ax1.add_collection3d(Poly3DCollection([points.reference], alpha=0.3, facecolor="blue"))
ax1.add_collection3d(Poly3DCollection([points.target], alpha=0.3, facecolor="red"))
ax1.scatter(*points.point, c="g", s=50)
ax1.set_title("Before (Target free)")
ax1.set_xlabel("X")
ax1.set_ylabel("Y")
ax1.set_zlabel("Z")

# After alignment
ax2 = fig.add_subplot(122, projection="3d")
ax2.add_collection3d(Poly3DCollection([points.reference], alpha=0.3, facecolor="blue"))

# Old target (gray, faded)
ax2.add_collection3d(
    Poly3DCollection([points.target], alpha=0.1, facecolor="gray", edgecolor="k")
)

# New aligned target (red)
ax2.add_collection3d(Poly3DCollection([alignedNewTarget], alpha=0.3, facecolor="red"))

ax2.scatter(*points.point, c="g", s=50)
ax2.set_title("After (Old gray, New red)")
ax2.set_xlabel("X")
ax2.set_ylabel("Y")
ax2.set_zlabel("Z")

plt.tight_layout()
plt.show()
