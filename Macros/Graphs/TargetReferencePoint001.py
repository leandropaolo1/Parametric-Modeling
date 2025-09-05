import matplotlib.pyplot as plt
from itertools import product, combinations

target_bbox = {
    "min": (62.1281, 45.1335, 0),
    "max": (101.813, 67.6384, 0)
}

reference_bbox = {
    "min": (-118.586, 4.25516, -270.274),
    "max": (-113.129, 38.8095, -187.007)
}

# Third selected point
third_point = (-115.67, 22.3606, -231.499)

def plot_bbox (ax, bbox, color, label):
    x0, y0, z0 = bbox["min"]
    x1, y1, z1 = bbox["max"]
    
    corners = list(product([x0, x1], [y0, y1], [z0, z1]))
    ax.scatter(*zip(*corners), c=color, label=label)
    
    for s, e in combinations(corners, 2):
        if sum(a != b for a, b in zip(s, e)) == 1:
            ax.plot(*zip(s, e), color=color)
            

figure = plt.figure()
ax = figure.add_subplot(111, projection='3d')
plot_bbox(ax, target_bbox, "r", "Target BBox")
plot_bbox(ax, reference_bbox, "b", "Reference BBox")

ax.scatter(*third_point, c="g", s=10, marker="o", label="Third Point")
    
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.legend()
ax.set_title("Bounding Boxes with Third Point")

plt.show()