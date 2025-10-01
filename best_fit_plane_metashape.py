"""
Metashape Best-Fit Plane Alignment Script

Aligns a 3D mesh to lie flat on the XY plane by:
1. Centering the mesh at the origin
2. Computing the best-fit plane using PCA
3. Rotating the mesh to align this plane with XY

IMPORTANT: This script transforms the ENTIRE CHUNK (cameras, point cloud, 
mesh, markers, etc.) by modifying chunk.transform.matrix. All elements will 
be repositioned together. Requires a mesh to be generated first.

Ideal for preparing scanned planar artworks for orthomosaic generation but should work for any 3D mesh.

Author: Xavier Aure Calvet
License: MIT
"""

import Metashape
import numpy as np

# Ensure NumPy is installed
try:
    import numpy as np
except ImportError:
    Metashape.app.pip_install('numpy')
    import numpy as np

# Get the current document and chunk
doc = Metashape.app.document
chunk = doc.chunk

# Verify mesh exists
if not hasattr(chunk, 'models') or len(chunk.models) == 0:
    print("No mesh found in the chunk. Please generate a mesh first.")
    raise Exception("No mesh found in the chunk.")

# Select the first mesh
model = chunk.models[0]

# Extract mesh vertices
vertices = model.vertices
if len(vertices) < 3:
    print("Not enough vertices to compute a plane.")
    raise Exception("Not enough vertices to compute a plane.")

# Get vertex coordinates in world space
points = []
for vertex in vertices:
    coord = vertex.coord
    coord_world = chunk.transform.matrix.mulp(coord)
    points.append([coord_world.x, coord_world.y, coord_world.z])

points = np.array(points)

# STEP 1: Center the mesh at the origin
# Note: This transforms the entire chunk, not just the mesh
centroid = np.mean(points, axis=0)
print(f"Original centroid: {centroid}")

# Create translation matrix
T = Metashape.Matrix().Translation(Metashape.Vector(-centroid))
chunk.transform.matrix = T * chunk.transform.matrix  # Transforms entire chunk

print("Mesh centered at (0, 0, 0)")

# STEP 2: Align best-fit plane with XY plane
centered_points = points - centroid

# Compute covariance matrix for PCA
cov = np.cov(centered_points, rowvar=False)

# Find principal components
eigenvalues, eigenvectors = np.linalg.eigh(cov)

# Smallest eigenvalue corresponds to the plane normal
normal_vector = eigenvectors[:, 0]

# Ensure normal points upward
if normal_vector[2] < 0:
    normal_vector = -normal_vector

# Target is the Z-axis
target_vector = np.array([0, 0, 1])

# Compute rotation matrix using Rodrigues' rotation formula
v = np.cross(normal_vector, target_vector)
s = np.linalg.norm(v)

if s == 0:
    # Already aligned
    R = np.eye(3)
else:
    c = np.dot(normal_vector, target_vector)
    vx = np.array([[0, -v[2], v[1]],
                   [v[2], 0, -v[0]],
                   [-v[1], v[0], 0]])
    R = np.eye(3) + vx + vx @ vx * ((1 - c) / s**2)

# Convert to Metashape 4x4 matrix
R_matrix = Metashape.Matrix([[R[0, 0], R[0, 1], R[0, 2], 0],
                             [R[1, 0], R[1, 1], R[1, 2], 0],
                             [R[2, 0], R[2, 1], R[2, 2], 0],
                             [0, 0, 0, 1]])

# Apply rotation
chunk.transform.matrix = R_matrix * chunk.transform.matrix  # Transforms entire chunk

print("Best-fit plane aligned with XY plane")

# Optional: Reset region to fit new orientation
if hasattr(chunk, 'resetRegion'):
    chunk.resetRegion()

# Verify final position
final_points = []
for vertex in vertices:
    coord = vertex.coord
    coord_world = chunk.transform.matrix.mulp(coord)
    final_points.append([coord_world.x, coord_world.y, coord_world.z])

final_centroid = np.mean(final_points, axis=0)
print(f"Final centroid: {final_centroid}")
print("✓ Alignment complete. Ready for orthomosaic generation.")
