import numpy as np
import matplotlib.pyplot as plt

# -----------------------
# Input points
# -----------------------
reference_points = np.array([
    (-113.12865648751745, 4.789457814477095, -270.27419162089456),
    (-115.07642775687553, 38.80953815277945, -240.55703904381986),
    (-118.11044330302218, 20.817561281290054, -194.267042271242),
    (-118.58629913058903, 20.266577164611498, -187.00690690022165),
    (-118.50699530542028, 4.255156433468771, -188.21684319920942),
    (-118.04060161192942, 4.78945781447708, -195.3326147298364)
])

target_points = np.array([
    (99.82568851450468, 51.99238939618349, 0.0),
    (98.1873844259267, 50.8452365234814, 0.0),
    (98.36169591142202, 48.852847127297906, 0.0),
    (100.17431148549531, 48.00761060381651, 0.0),
    (101.8126155740733, 49.1547634765186, 0.0),
    (101.63830408857798, 51.147152872702094, 0.0)
])

# -----------------------
# Helper functions
# -----------------------
def plane_normal(p1, p2, p3):
    """Compute unit normal from 3 points."""
    v1 = p2 - p1
    v2 = p3 - p1
    n = np.cross(v1, v2)
    return n / np.linalg.norm(n)

def fit_plane(points):
    """Fit plane z = ax + by + c using least squares."""
    X, Y, Z = points[:,0], points[:,1], points[:,2]
    A = np.c_[X, Y, np.ones(points.shape[0])]
    coeff, _, _, _ = np.linalg.lstsq(A, Z, rcond=None)
    a, b, c = coeff
    return a, b, c

def rodrigues_rotation(axis, theta):
    """Rodrigues rotation matrix."""
    axis = axis / np.linalg.norm(axis)
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    return np.eye(3) + np.sin(theta)*K + (1-np.cos(theta))*(K@K)

def plot_plane(ax, coeffs, points, color, alpha=0.3, label="plane"):
    """Plot plane surface + points."""
    a, b, c = coeffs
    xlim = (points[:,0].min()-5, points[:,0].max()+5)
    ylim = (points[:,1].min()-5, points[:,1].max()+5)
    xx, yy = np.meshgrid(np.linspace(*xlim, 10),
                         np.linspace(*ylim, 10))
    zz = a*xx + b*yy + c
    ax.plot_surface(xx, yy, zz, color=color, alpha=alpha)
    ax.scatter(*points.T, c=color, s=40, label=label)

# -----------------------
# 1. Normals
# -----------------------
n_r = plane_normal(reference_points[0], reference_points[1], reference_points[2])
n_t = np.array([0,0,1])  # target plane normal

# -----------------------
# 2. Rotation (align normals)
# -----------------------
axis = np.cross(n_t, n_r)
if np.linalg.norm(axis) < 1e-8:
    R = np.eye(3)
else:
    axis = axis/np.linalg.norm(axis)
    theta = np.arccos(np.clip(np.dot(n_t, n_r), -1, 1))
    R = rodrigues_rotation(axis, theta)

# -----------------------
# 3. Translation (align centroids)
# -----------------------
C_r = reference_points.mean(axis=0)
C_t_rot = (R @ target_points.T).T.mean(axis=0)
T = C_r - C_t_rot

# Apply transform
target_aligned = (R @ target_points.T).T + T

# -----------------------
# 4. Plane fitting
# -----------------------
a_r, b_r, c_r = fit_plane(reference_points)
a_t, b_t, c_t = fit_plane(target_points)
a_ta, b_ta, c_ta = fit_plane(target_aligned)

# -----------------------
# 5. Plotting
# -----------------------
fig = plt.figure(figsize=(14,6))

# BEFORE
ax1 = fig.add_subplot(121, projection="3d")
plot_plane(ax1, (a_r,b_r,c_r), reference_points, "red", 0.5, "Reference plane")
plot_plane(ax1, (a_t,b_t,c_t), target_points, "blue", 0.5, "Target plane")
ax1.set_title("Before Alignment")
ax1.set_xlabel("X"); ax1.set_ylabel("Y"); ax1.set_zlabel("Z")
ax1.legend()

# AFTER
ax2 = fig.add_subplot(122, projection="3d")
plot_plane(ax2, (a_r,b_r,c_r), reference_points, "red", 0.5, "Reference plane")
plot_plane(ax2, (a_ta,b_ta,c_ta), target_aligned, "green", 0.5, "Target aligned plane")
ax2.set_title("After Alignment (centroid match)")
ax2.set_xlabel("X"); ax2.set_ylabel("Y"); ax2.set_zlabel("Z")
ax2.legend()

plt.show()

# -----------------------
# Print transform
# -----------------------
print("Rotation matrix R:\n", R)
print("Translation vector T:\n", T)
