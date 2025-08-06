using StaticArrays
using GLMakie
using GeometryBasics
using Random

# -- Parameters --
dims = SVector(30, 30, 30)
voxel_size = SVector(1.0f0, 1.0f0, 1.0f0)
seed = 42
threshold = 0.5  # controls the 'density' of the shape

# -- Noise function --
function pseudo_perlin_noise(x, y, z; scale=0.1)
    return 0.5 * (sin(scale * x) + cos(scale * y) + sin(scale * z)) +
           0.5 * (cos(scale * x * y) + sin(scale * y * z))
end

# -- Generate voxel positions --
function generate_organic_positions(dims::SVector{3, Int}, threshold::Float64)
    coords = Vector{SVector{3, Int}}()
    for z in 0:(dims[3]-1), y in 0:(dims[2]-1), x in 0:(dims[1]-1)
        noise_val = pseudo_perlin_noise(x, y, z)
        if noise_val > threshold
            push!(coords, SVector(x, y, z))
        end
    end
    return coords
end

# -- Base unit cube mesh (reused) --
const CUBE_VERTICES = Point3f.([
    (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
    (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)
])
const CUBE_FACES = [
    (1, 2, 3), (1, 3, 4),
    (5, 6, 7), (5, 7, 8),
    (1, 2, 6), (1, 6, 5),
    (2, 3, 7), (2, 7, 6),
    (3, 4, 8), (3, 8, 7),
    (4, 1, 5), (4, 5, 8),
]

# -- Fast mesh builder --
function build_voxel_mesh(positions::Vector{SVector{3, Int}}, voxel_size::SVector{3, Float32})
    n_voxels = length(positions)
    verts_per_cube = 8
    faces_per_cube = 12

    total_verts = n_voxels * verts_per_cube
    total_faces = n_voxels * faces_per_cube

    vertices = Vector{Point3f}(undef, total_verts)
    faces = Vector{TriangleFace{Int}}(undef, total_faces)

    @inbounds for i in 1:n_voxels
        offset = (i - 1) * verts_per_cube
        base_pos = Point3f(positions[i]...)
        for j in 1:verts_per_cube
            vertices[offset + j] = base_pos .+ voxel_size .* CUBE_VERTICES[j]
        end
        for j in 1:faces_per_cube
            a, b, c = CUBE_FACES[j]
            faces[(i - 1) * faces_per_cube + j] = TriangleFace(offset + a, offset + b, offset + c)
        end
    end

    return GeometryBasics.Mesh(vertices, faces)
end

# -- Main --
cpu_positions = generate_organic_positions(dims, threshold)
println("Generated ", length(cpu_positions), " voxels.")

voxel_mesh = build_voxel_mesh(cpu_positions, voxel_size)

scene = Scene(camera = cam3d!, resolution = (1000, 800))
mesh!(scene, voxel_mesh, color = :seagreen, shading = false)
 display(scene)
