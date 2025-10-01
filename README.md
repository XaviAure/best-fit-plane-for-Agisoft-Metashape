# Agisoft Metashape Best-Fit Plane Alignment

A Python script for Agisoft Metashape that automatically aligns scanned planar artworks (or any planar mesh) to lie flat on the XY plane, optimizing them for high-resolution orthomosaic generation.

## Purpose

When scanning flat artworks or documents, the resulting 3D mesh often sits at an arbitrary angle in 3D space. This script:
1. Centers the mesh at the origin (0, 0, 0)
2. Calculates the best-fit plane through the mesh using PCA
3. Rotates the mesh so this plane aligns with the XY plane
4. Prepares the model for optimal orthomosaic export

## Requirements

- Agisoft Metashape (Professional edition recommended)
- NumPy (auto-installed if missing)
- **A mesh must be generated in your chunk** (the script analyses mesh vertices)

## Important Note

This script transforms the **entire chunk** (cameras, point cloud, mesh, markers, etc.), not just the mesh. It modifies `chunk.transform.matrix`, so all elements in the chunk will be repositioned together.

## Usage

1. Open your Metashape project with a generated mesh
2. Run the script via: **Tools → Run Script**
3. Select `best_fit_plane_metashape.py`
4. The mesh will be automatically aligned
5. Generate your orthomosaic: **Workflow → Build Orthomosaic**

## How It Works

The script uses Principal Component Analysis (PCA) to find the plane that best fits all vertices in the mesh. The eigenvector with the smallest eigenvalue represents the normal to this plane. The script then applies rotation and translation transformations to align this plane with the XY plane.

## Output

The script prints:
- Original mesh centroid coordinates
- Confirmation of centring and alignment
- Final centroid coordinates (should be near origin)

## License

MIT
