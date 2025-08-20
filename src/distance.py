import math

def compute_euclidean_distance_matrix(locations):
    matrix = {}
    for from_idx, from_node in enumerate(locations):
        matrix[from_idx] = {}
        for to_idx, to_node in enumerate(locations):
            dx = from_node[0] - to_node[0]
            dy = from_node[1] - to_node[1]
            matrix[from_idx][to_idx] = int(math.hypot(dx, dy))
    return matrix
