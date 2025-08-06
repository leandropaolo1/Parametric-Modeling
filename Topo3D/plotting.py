import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Create a polar grid for the semicircle
r = np.linspace(0, 1, 100)
theta = np.linspace(0, np.pi, 100)
R, Theta = np.meshgrid(r, theta)

# Convert polar to Cartesian coordinates
X = R * np.cos(Theta)
Y = R * np.sin(Theta)
Z = np.exp(X**2 + Y**2)

# Create the 3D surface plot
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection="3d")
surf = ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="none", alpha=0.9)

# Highlight the boundary (y = sqrt(1 - x^2)) in red
x_boundary = np.linspace(-1, 1, 200)
y_boundary = np.sqrt(1 - x_boundary**2)
z_boundary = np.exp(x_boundary**2 + y_boundary**2)
ax.plot(
    x_boundary,
    y_boundary,
    z_boundary,
    color="red",
    linewidth=2.5,
    label=r"Boundary $y = \sqrt{1 - x^2}$",
)

# Labels, title, view angle, and colorbar
ax.set_title(r"$e^{x^2 + y^2}$ over Region $R$ with Boundary Highlighted")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.view_init(elev=30, azim=45)
plt.colorbar(surf, ax=ax, shrink=0.6, label="Height (z)")
ax.legend()

# Show the plot
plt.show()
