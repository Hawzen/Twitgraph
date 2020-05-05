# Spectral clustering algorithm
# https://people.eecs.berkeley.edu/~demmel/cs267/lecture20/lecture20.html
import numpy as np
from itertools import compress, groupby


def getClusters(nodes: dict, numClusters: int = 2):

    for i in range(numClusters - 1):
        if i == 0:
            clusters = getEigenvec(createLaplacian(createAdjacency(nodes)))
            continue

        keys = tuple(key for key, group in groupby(np.sort(clusters)))
        freq = tuple(len(tuple(group)) for key, group in groupby(np.sort(clusters)))
        cluster = keys[freq.index(max(freq))] # split this cluster into two

        vec = getEigenvec(createLaplacian(createAdjacency(nodes, tuple(clusters == cluster)))) + 2 * i

        cnt = 0
        for index, el in enumerate(clusters):
            if el == cluster:
                clusters[index] = vec[cnt]
                cnt += 1

    out = {}
    for Id, cluster in zip(nodes, clusters):
        out.update({Id: cluster})
    return out


def createAdjacency(nodes: dict, indices: tuple = None) -> np.ndarray:
    """Creates a symmetric adjacency matrix
    For each node in nodes, create vector v such that v[i] = 1 if the ith Id in nodes is in node.edges
    or node.id is in ith node.edges else 0

    If indices were (1, 0, 0, 1) and the given nodes is {id1: nd, id2: nd, id3: nd, id4: nd} then {id1: nd, id2: nd}
    will be in the matrix

    Ex. nodes = {id1: NodeObject, id2: NodeObject, id3: NodeObject}
        nodes[id1].edges = [id2, id3] -> id1 vector = [0, 1, 1]
        nodes[id2].edges = [] -> id2 vector [1, 0, 0] (matrix is symmetric)
        nodes[id3].edges = [id1] -> id3 vector [1, 0, 0]
    """
    if indices is None:
        indices = (True,) * len(nodes)

    compressed = tuple(compress(nodes.items(), indices))
    A = []
    for _, node in compressed:
        A.append(list(1 if Id in node.edges or node.id in nodes[Id].edges else 0 for Id, _ in compressed))

    return np.array(A)


def createLaplacian(A: np.ndarray) -> np.ndarray:
    """Given adjacency matrix return Laplacian Matrix"""
    D = np.diag(sum(A))
    L = D - A
    return L


def getEigenvec(L: np.ndarray) -> np.ndarray:
    """Given laplacian matrix return normal eigenvector associated with second eigenvalue"""
    vals, vecs = np.linalg.eig(L)
    index = np.where(vals == np.partition(vals, 1)[1])[0][0]

    vec = vecs[:, index]  # Eigenvector associated with the second eigenvalues
    for i, el in enumerate(vec):
        if el < 0:
            vec[i] = 1
        elif el > 0:
            vec[i] = 2

    return vec
