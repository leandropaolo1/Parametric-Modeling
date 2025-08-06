using GLMakie                      # For plotting
using GeometryBasics               # For constructing custom mesh geometry

# -- Create polar grid --
r = range(0, 1, length=100)        # Radius values from 0 to 1
θ = range(0, π, length=100)        # Angle values from 0 to π (upper half-circle)

# Generate meshgrid-like matrices R and Θ
R = [ri for θi in θ, ri in r]      # Replicates radius across theta steps
Θ = [θi for θi in θ, ri in r]      # Replicates theta across radius steps

# -- Convert to Cartesian coordinates --
X = R .* cos.(Θ)                   # Convert polar (R, Θ) to Cartesian x
Y = R .* sin.(Θ)                   # Convert polar (R, Θ) to Cartesian y
Z = @. exp(X^2 + Y^2)              # Compute surface height z = exp(x² + y²)

# -- Flatten into vertices and generate faces --
points = Point3f.(X[:], Y[:], Z[:])  # Flatten matrices into 3D vertex list
colors = Z[:]                         # Flatten Z values to match vertex order

# Create triangle connectivity (faces)
nrows, ncols = size(X)
faces = TriangleFace{Int32}[]
for i in 1:nrows-1, j in 1:ncols-1
    p1 = (j - 1) * nrows + i       # Index of top-left corner
    p2 = p1 + 1                    # Top-right
    p3 = p1 + nrows                # Bottom-left
    p4 = p3 + 1                    # Bottom-right

    # Add two triangles per grid square
    push!(faces, TriangleFace((p1, p2, p3)))
    push!(faces, TriangleFace((p2, p4, p3)))
end

# Create the mesh object from vertices and triangle faces
mesh_data = GeometryBasics.Mesh(points, faces)

# -- Create the plot figure and 3D axis --
fig = Figure(resolution=(1200, 1100))  # Set figure size
ax = Axis3(fig[1, 1],
    title=L"e^{x^2 + y^2} \text{ over Region } R \text{ with Boundary Highlighted}",
    xlabel="x", ylabel="y", zlabel="z",
    elevation=0.3, azimuth=315,
    titlesize=22,     # << Increase title font size
    titlegap=25       # << Add space below title
)

# -- Track and display the camera view dynamically --
on(ax.scene.camera.projectionview) do _
    az = ax.azimuth[]
    el = ax.elevation[]
    #ax.title = "az = $(round(az, digits=1)), el = $(round(el, digits=1))"
end

# -- Plot the surface mesh --
meshplot = mesh!(ax, mesh_data;
    color=colors,
    colormap=:viridis,
    shading=false,
    transparency=true
)

# -- Add the boundary curve y = sqrt(1 - x^2) in red --
x_boundary = range(-1, 1, length=200)
y_boundary = sqrt.(1 .- x_boundary .^ 2)
z_boundary = @. exp(x_boundary^2 + y_boundary^2)
boundary_plot = lines!(ax, x_boundary, y_boundary, z_boundary;
    color=:red,
    linewidth=3
)

# -- Add a colorbar and legend for the boundary curve --
Colorbar(fig[1, 2], meshplot;
    label="Height (z)",
    width=15,               # Make colorbar thinner
    height=Relative(0.4)    # Shrink vertical size of colorbar
)

# Add a legend entry for the red boundary line
axislegend(ax, [boundary_plot], [L"Boundary~y = \sqrt{1 - x^2}"], position=:rt)

# -- Show the figure --
fig
