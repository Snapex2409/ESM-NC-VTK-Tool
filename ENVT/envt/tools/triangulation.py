import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt

def compute_normal(points, e1, e2):
    """Compute the normal vector using the first three points."""
    # Compute the normal vector as the cross product of these two vectors
    normal = np.cross(e1, e2)
    normal = normal / np.linalg.norm(normal)  # Normalize the normal vector
    return normal

def sort_counterclockwise(points, indices, normal):
    """Sort points in counterclockwise order using the normal vector."""
    center = np.mean(points, axis=0)  # Compute centroid
    ref_vector = points[0] - center   # Reference vector

    def angle_from_ref(p):
        vec = p - center
        angle = np.arctan2(np.dot(normal, np.cross(ref_vector, vec)), np.dot(ref_vector, vec))
        return angle

    sorting = np.argsort([angle_from_ref(p) for p in points])
    return points[sorting], indices[sorting]


def compute_plane_basis(points):
    """Compute an orthonormal basis for the plane using the first three points."""
    v1 = points[1] - points[0]  # First basis vector
    v1 /= np.linalg.norm(v1)  # Normalize

    v2 = points[2] - points[0]  # A second vector in the plane
    v2 -= np.dot(v2, v1) * v1  # Remove component along v1
    v2 /= np.linalg.norm(v2)  # Normalize

    return v1, v2

def project_onto_plane(points, origin, e1, e2):
    """Project 3D points onto a 2D local coordinate system (e1, e2)."""
    return np.array([[np.dot(p - origin, e1), np.dot(p - origin, e2)] for p in points])

def triangulate_polygon(points, indices):
    """Triangulate the polygon by projecting it onto a local 2D coordinate system."""
    if len(points) == 3:
        return np.array([points]), np.array([indices])

    e1, e2 = compute_plane_basis(points)
    normal = compute_normal(points, e1, e2)
    sorted_points, sorted_indices = sort_counterclockwise(points, indices, normal)
    projected_2d = project_onto_plane(sorted_points, sorted_points[0], e1, e2)
    tri = Delaunay(projected_2d)

    # Reconstruct triangles in 3D using original points
    #plt.triplot(projected_2d[:,0], projected_2d[:,1], tri.simplices)
    #plt.plot(projected_2d[:,0], projected_2d[:,1], '.')
    #plt.show()

    return sorted_points[tri.simplices], sorted_indices[tri.simplices]
