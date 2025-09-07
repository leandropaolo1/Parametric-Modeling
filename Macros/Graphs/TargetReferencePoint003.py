import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Reference face vertices
reference_face = np.array(
    [
        (-113.12865648751726, 4.789457814476987, -270.27419162089467),
        (-115.07642775687538, 38.80953815277934, -240.5570390438199),
        (-118.04060161192928, 4.789457814476990, -195.33261472983640),
        (-118.11044330302204, 20.817561281289972, -194.26704227124210),
        (-118.50699530542012, 4.255156433468684, -188.21684319920945),
        (-118.58629913058888, 20.266577164611410, -187.00690690022168),
    ]
)

# Target face (flat in XY plane at Z=0)
target_face = np.array(
    [
        (62.1281, 45.1335, 0),
        (101.813, 45.1335, 0),
        (101.813, 67.6384, 0),
        (62.1281, 67.6384, 0),
    ]
)

# Clicked point on reference
pointC = np.array([-115.67, 22.3606, -231.499])

# --- Reference normal (fixed)
v1, v2, v3 = reference_face[:3]
normal_ref = np.cross(v2 - v1, v3 - v1)
normal_ref /= np.linalg.norm(normal_ref)

# --- Target normal (Z-up)
normal_tgt = np.array([0, 0, 1])

# --- Rotation (Rodrigues)
axis = np.cross(normal_tgt, normal_ref)
axis_len = np.linalg.norm(axis)
if axis_len > 1e-8:
    axis /= axis_len
    angle = np.arccos(np.clip(np.dot(normal_tgt, normal_ref), -1.0, 1.0))
    K = np.array(
        [[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]]
    )
    R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
else:
    R = np.eye(3)

# --- Rotate + translate target only
rotated_face = target_face @ R.T
translation = pointC - rotated_face.mean(axis=0)  # match centroid
aligned_face = rotated_face + translation

# --- Visualization
fig = plt.figure(figsize=(12, 6))

# Before
ax1 = fig.add_subplot(121, projection="3d")
ax1.add_collection3d(Poly3DCollection([reference_face], alpha=0.3, facecolor="blue"))
ax1.add_collection3d(Poly3DCollection([target_face], alpha=0.3, facecolor="red"))
ax1.scatter(*pointC, c="g", s=50)
ax1.set_title("Before (Target free)")
ax1.set_xlabel("X")
ax1.set_ylabel("Y")
ax1.set_zlabel("Z")

# After — show both old and new target
ax2 = fig.add_subplot(122, projection="3d")
ax2.add_collection3d(Poly3DCollection([reference_face], alpha=0.3, facecolor="blue"))

# Old target (faded gray)
ax2.add_collection3d(
    Poly3DCollection([target_face], alpha=0.1, facecolor="gray", edgecolor="k")
)

# New aligned target (red)
ax2.add_collection3d(Poly3DCollection([aligned_face], alpha=0.3, facecolor="red"))

ax2.scatter(*pointC, c="g", s=50)
ax2.set_title("After (Old gray, New red)")
ax2.set_xlabel("X")
ax2.set_ylabel("Y")
ax2.set_zlabel("Z")

plt.tight_layout()
plt.show()
