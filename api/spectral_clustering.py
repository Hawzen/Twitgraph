# Spectral clustering
# Reference: https://arxiv.org/abs/0711.0189
#            https://people.eecs.berkeley.edu/~demmel/cs267/lecture20/lecture20.html
import numpy as np
from itertools import compress, groupby
from sklearn.cluster import spectral_clustering
from warnings import filterwarnings
filterwarnings("ignore", "Graph is not fully connected, spectral embedding")


def getClusters(nodes: dict, n_clusters:int=8) -> dict:
    """ Takes in a dictionary of nodes {ID: nodeObject} and a number of n_clusterss.
        Returns a dictionary mapping of every node and its cluster {ID: cluster} using the spectral clustering
            algorithm.
    """
    nodesToClusters = {}
    for node in nodes.values():
        if node.user.protected:
            nodesToClusters[node.id] = -1

    for Id in nodesToClusters.keys():
        nodes.pop(Id)

    # clusters = []  # Clusters is a python list to allow variable length integers

    # for i in range(numPartitions - 1):
    #     if i == 0:
    #         clusters = list((spectral(createAdjacency(nodes))))
    #         continue

    #     # Sort then group clusters by num. of members
    #     frequency = {key: len(tuple(group)) for key, group in groupby(sorted(clusters)) if "5" not in str(key)}
    #     maximum = max(frequency.values())
    #     for key, freq in frequency.items():
    #         if freq == maximum:
    #             cluster = key  # Use 'cluster' to select biggest cluster

    #     # Split nodes that belong to 'cluster' into two clusters
    #     vec = (spectral(createAdjacency(nodes, tuple(cluster == x for x in clusters))))

    #     # Update all new clustered elements from vec to clusters
    #     cnt = 0
    #     for index, el in enumerate(clusters):
    #         if el == cluster:
    #             clusters[index] = int(str(clusters[index]) + str(vec[cnt]))
    #             cnt += 1

    node_clusters =  spectral_clustering(createAdjacency(nodes), n_clusters=n_clusters)

    for Id, cluster in zip(nodes, node_clusters):
        nodesToClusters.update({Id: int(cluster)})
    return nodesToClusters


def createAdjacency(nodes: dict, selectors: tuple = None) -> np.ndarray:
    """Creates a symmetric adjacency matrix
    For each node in nodes, create vector v such that v[i] = 1 if the ith Id in nodes is in node.edges
    or node.id is in ith node.edges else 0

    The index of nodes from the dictionary can be specified, if indices were (1, 0, 0, 1) and the given
      dictionary is {id1: nd, id2: nd, id3: nd, id4: nd} then {id1: nd, id2: nd} will be used to construct the matrix

    Ex. nodes = {id1: NodeObject, id2: NodeObject, id3: NodeObject}
        nodes[id1].edges = [id2, id3] -> id1 vector = [0, 1, 1]
        nodes[id2].edges = [] -> id2 vector [1, 0, 0] (matrix is symmetric)
        nodes[id3].edges = [id1] -> id3 vector [1, 0, 0]
    """
    if selectors is None:
        selectors = (True,) * len(nodes)

    compressed = tuple(compress(nodes.items(), selectors))  # Throw out any nodes not specified in selectors
    A = []
    for _, node in compressed:
        A.append(list(1 if Id in node.edges or node.id in nodes[Id].edges else 0 for Id, _ in compressed))
    return np.array(A)


def spectral(A):
    labels = spectral_clustering(A, 2)
    for i, el in enumerate(labels):
        if el == 0:
            labels[i] = 1
        elif el == 1:
            labels[i] = 2
    return labels

### Unused functions

def createLaplacian(A: np.ndarray) -> np.ndarray:
    """Given adjacency matrix return Laplacian Matrix"""
    D = np.diag(sum(A))
    L = D - A
    return L


def getEigenvec(L: np.ndarray) -> np.ndarray:
    """Given Laplacian Matrix, returns a clustering of the nodes in the Laplacian Matrix

        Note: The returned vector has the following properties
            1 at index i means that the ith node in L belongs to first cluster
            2 at index i means that the ith node in L belongs to second cluster
            5 at index i means that the ith node in L belongs to no cluster and should be considered irrelevant"""
    vals, vecs = np.linalg.eigh(L)

    # Get eigenvector associated with the second eigenvalue
    index = np.where(vals > 10e-6)[0][0]
    vec = vecs[:, index]

    # If      vec[i] > 0 -> vec[i] belongs to cluster 1
    # Else if vec[i] < 0 -> vec[i] belongs to cluster 2
    # This heuristic could be improved by applying K-Means to vec which should provide better clusters, but we will
    # refrain from applying it
    temp = np.zeros(len(vec), dtype=np.int64)
    for i, el in enumerate(vec):
        if el < 0:
            temp[i] = 1
        elif el > 0:
            temp[i] = 2
        elif el == 0:
            temp[i] = 5  # The number is an arbitrary choice, read 'Note' in function docstring

    return temp
