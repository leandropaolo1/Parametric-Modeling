import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Actual reference face vertices from FreeCAD
reference_face = [
    (-113.12865648751726,  4.789457814476987, -270.27419162089467),
    (-115.07642775687538, 38.80953815277934, -240.5570390438199),
    (-118.04060161192928,  4.789457814476990, -195.33261472983640),
    (-118.11044330302204, 20.817561281289972, -194.26704227124210),
    (-118.50699530542012,  4.255156433468684, -188.21684319920945),
    (-118.58629913058888, 20.266577164611410, -187.00690690022168)
]

# Target face (example: flat rectangle in XY plane at Z=0)
target_face = [
    (62.1281, 45.1335, 0),
    (101.813, 45.1335, 0),
    (101.813, 67.6384, 0),
    (62.1281, 67.6384, 0)
]

# Clicked point
pointC = (-115.67, 22.3606, -231.499)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot reference face
ax.add_collection3d(Poly3DCollection([reference_face], alpha=0.3, facecolor="blue", label="Reference Face"))

# Plot target face
ax.add_collection3d(Poly3DCollection([target_face], alpha=0.3, facecolor="red", label="Target Face"))

# Plot clicked point
ax.scatter(*pointC, c="g", s=100, marker="o", label="Clicked Point")

# Labels
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.legend()
ax.set_title("Reference Face, Target Face, and Clicked Point")

plt.show()
