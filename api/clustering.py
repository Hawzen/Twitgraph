from warnings import filterwarnings

import numpy as np
from itertools import compress, groupby
from sklearn.cluster import SpectralClustering
import pandas as pd
from hdbscan import HDBSCAN
filterwarnings("ignore", "Graph is not fully connected, spectral embedding")


def mySpectralClustering(nodes: dict, numPartitions: int = 2) -> dict:
    """" Takes in a dictionary of nodes {ID: nodeObject} and a number of partitions.
         Returns a dictionary mapping of every node and its cluster {ID: cluster} using the spectral clustering
          algorithm.
          Example: The function applies spectral clustering at the biggest cluster of nodes numPartitions time,
          e.g. numPartition=3, [n1, n2, n3, n4, n5] -> [n1, n2 | n3, n4, n4] -> [n1, n2 | n3, | n4, n5]
         Notes:
            Each time the algorithm preforms a clustering, it makes the Adjacency Matrix and the Laplacian Matrix
                again, as well as getting the eigenvectors and values, so the performance is slow on higher numPartition
            The algorithm is implemented for symmetric matrices, so the direction-ess of the graph is ignored
            Each cluster has a unique id identifying it, and gives an easy way to look at its ancestors,
                e.g. 12 -> belongs to the first cluster and to the second cluster
                     1 -> belongs to the first cluster
                     211 -> belongs to the second cluster, the first sub cluster and the first sub-sub cluster
    """

    nodesToClusters = {}
    for node in nodes.values():
        if node.user.protected:
            nodesToClusters[node.id] = -1

    for id_ in nodesToClusters.keys():
        nodes.pop(id_)

    # clusters = []  # Clusters is a python list to allow variable length integers
    clusterer = SpectralClustering(n_clusters=8, affinity="precomputed", assign_labels="discretize")

    for i in range(numPartitions - 1):
        if i == 0:
            clusters = list((clusterer.fit_predict(createAdjacency(nodes))))
            continue

        # Sort then group clusters by num. of members
        frequency = {key: len(tuple(group)) for key, group in groupby(sorted(clusters))}
        cluster = max(frequency, key=frequency.get)
        
        # Split nodes that belong to 'cluster' into two clusters
        vec = clusterer.fit_predict(createAdjacency(nodes, tuple(cluster == x for x in clusters)))

        # Update all new clustered elements from vec to clusters
        cnt = 0
        for index, el in enumerate(clusters):
            if el == cluster:
                clusters[index] = int(str(clusters[index]) + str(vec[cnt]))
                cnt += 1

    for Id, cluster in zip(nodes, clusters):
        nodesToClusters.update({Id: int(cluster)})

    edges = None
    # # Get edges based on mean closeness
    # clusters_unique = np.unique(clusters).tolist()
    # adj = createAdjacency(nodes)
    # means = {cluster: np.zeros(adj.shape[1]) for cluster in clusters_unique}
    # counts = {cluster: 0 for cluster in clusters_unique}
    # for row, cluster in zip(adj, clusters):
    #     means[cluster] += row
    #     counts[cluster] += 1
    # means = {cluster: means[cluster] / counts[cluster] for cluster in means}
    # distances = [
    #     [abs(cl1 - cl2).mean() for cl2 in means.values()] for cl1 in means.values()
    # ]
    # edges = pd.DataFrame(distances).applymap(lambda x: x > 0.17).values.tolist()

    return nodesToClusters, edges


def myHDBSCAN(nodes, numPartitions):
    nodesToClusters = {}
    for node in nodes.values():
        if node.user.protected:
            nodesToClusters[node.id] = -1

    for Id in nodesToClusters.keys():
        nodes.pop(Id)

    hdb = HDBSCAN(
        min_cluster_size=5,
        cluster_selection_epsilon=2, 
        cluster_selection_method="leaf",
        metric="manhattan",
    )

    for i in range(numPartitions - 1):
        if i == 0:
            clusters = hdb.fit_predict(createAdjacency(nodes))
            continue
        
        # Sort then group clusters by num. of members
        frequency = {key: len(tuple(group)) for key, group in groupby(sorted(clusters)) if "-1" not in str(key)}
        maximum = max(frequency.values())
        for key, freq in frequency.items():
            if freq == maximum:
                cluster = key  # Use 'cluster' to select biggest cluster

        # Split nodes that belong to 'cluster' into two clusters
        vec = hdb.fit_predict(createAdjacency(nodes, tuple(cluster == x for x in clusters)))

        # Update all new clustered elements from vec to clusters
        cnt = 0
        for index, el in enumerate(clusters):
            if el == cluster:
                clusters[index] = (clusters[index]) + (vec[cnt])
                cnt += 1

    # clusters = np.unique(n_clusters).tolist()
    # clusters.remove(-1)
    # distances = [
    #     [abs(hdb.weighted_cluster_centroid(i) - hdb.weighted_cluster_centroid(j)).mean() for j in clusters]
    #             for i in clusters]
    # edges = pd.DataFrame(distances).applymap(lambda x: x > 0.05).values.tolist()

    for Id, cluster in zip(nodes, clusters):
        nodesToClusters.update({Id: (cluster)})

    return nodesToClusters, None


# def getClusters(nodes: dict, n_clusters:int=8, algorithm="spectral_clustering"):
#     """ Takes in a dictionary of nodes {ID: nodeObject} and a number of n_clusterss.
#         Returns a dictionary mapping of every node and its cluster {ID: cluster} using the spectral clustering
#             algorithm.
#     """
#     if algorithm == "spectral_algorithm":
#         return mySpectralClustering(nodes, n_clusters)
#     if algorithm == "hdbscan":
#         return myHDBSCAN(nodes, n_clusters)

#     raise NotImplementedError()


# Helper


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
    labels = spectral_clustering(A, n_clusters=8)
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
