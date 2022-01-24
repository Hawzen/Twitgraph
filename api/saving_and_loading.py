import json
from typing import Tuple, List

import tweepy

from graph import Graph
from database import *
from clustering import myHDBSCAN, mySpectralClustering

db = RedisShelve("twitgraph", db=1)

def loadGraph(screenName):
    if screenName in db:
        return db[screenName]
    raise KeyError()

def loadAPI() -> tweepy.API:
    """Returns tweepy API given that a file called twitterkeys.txt with the keys exists"""
    with open('twitterkeys.txt', 'r') as file:
        lines = file.read().split('\n')
    apiKey = lines[0]
    apiSecretKey = lines[1]
    accessToken = lines[2]
    accessTokenSecret = lines[3]
    auth = tweepy.OAuthHandler(apiKey, apiSecretKey)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth)

    return api


def createGraph(screenName: str, api: tweepy.API) -> Graph:
    graph = Graph()
    graph.setOrigin(api, screenName)
    graph.listSearch_graph(api, depth=99)
    return graph


def loadAll(screenName: str, newName: bool=False) -> Tuple[tweepy.API, Graph]:
    """Gets apiKey, apiSecretKey, accessToken, accessTokenSecret and username from file twitterkeys.txt in
    the same directory, preforms api authentication
    then loads graph and JSON objects from shelve If either does not exist then creates them and set graph origin as
    username

    return api, graph, JSON
    """
    api = loadAPI()

    # Keep track of object target
    if not newName:
        graph = loadGraph(screenName)
    else:
        graph = createGraph(screenName, api)

    return api, graph


def getShelveKeys() -> List[str]:
    """returns a list of keys (profiles) stored inside shelve"""
    return db.keys()


def deleteShelveKey(screenName: str) -> None:
    if screenName not in getShelveKeys():
        raise KeyError

    del db[screenName]


def saveShelve(screenName: str, graph: Graph, dump: bool=False, onlyDone: bool=True, 
            numNodes: int=0, n_clusters: int=0, theme: str="default", layout: str="forceDirectedLayout", 
            algorithm: str="spectral_algorithm") -> None:
    """Saves graph object to shelve as well as dump the data to data.json if dump=True"""
    db[screenName] = graph
    db.bgsave()

    if dump:

        graph.fullEdgeSearch(numNodes)

        # Default node, partition values
        if numNodes == 0:
            numNodes = sum(1 for Id in graph.nodes.keys() if any(graph.nodes[Id].done))
        if n_clusters == 0:
            n_clusters = min(numNodes // 10, 20)

        # Check numNodes
        if onlyDone:
            if numNodes > graph.getDoneNum():
                raise ArithmeticError("Not enough done nodes")
        elif numNodes > graph.getNodeNum():
            raise ArithmeticError("Not enough nodes")

        cutNodes = {}  # Sliced version of graph.nodes
        for i, node in enumerate(graph.nodes.values()):

            if onlyDone and not any(node.done):
                continue
            if i == numNodes:
                break

            i += 1
            cutNodes.update({node.id: node})

        if algorithm == "spectral_clustering":
            clusters, cluster_edges = mySpectralClustering(cutNodes, n_clusters)
            clusterSizes = \
                dict(
                    map(
                        lambda x: (str(x), sum(1 for el in clusters.values() if el == x)), set(clusters.values())
                    )
                )
            modifyConfig(theme, layout)
            dumpData(_saveJSON(graph, clusters=clusters, clusterSizes=clusterSizes, cluster_edges=cluster_edges, algorithm="spectral_clustering"))
            return

        elif algorithm == "HDBSCAN":
            clusters, cluster_edges = myHDBSCAN(cutNodes, n_clusters)
            clusterSizes = \
                dict(
                    map(
                        lambda x: (str(x), sum(1 for el in clusters.values() if el == x)), set(clusters.values())
                    )
                )

            modifyConfig(theme, layout)
            dumpData(_saveJSON(graph, clusters=clusters, cluster_edges=cluster_edges, clusterSizes=clusterSizes, algorithm="HDBSCAN"))
            return
    
    raise NotImplementedError(f"Algorithm {algorithm} is not implemeneted yet")


def dumpData(JSON: dict) -> None:
    """Dumps given JSON to data.json file"""
    with open("../data/data.json", "w") as data:
        data.write("let data = ")
        json.dump(JSON, data, indent=8)
        data.flush()


def modifyConfig(theme: str, layout: str) -> None:
    """Modifies the config.js file in graph folder using given arguments and configuration.json file in data folder"""
    with open("../data/configurations.json", 'r') as file:
        config = json.loads(file.read())

    defTheme = config["themes"]["default"]
    conTheme = config["themes"].get(theme, defTheme)

    constants = conTheme.get("constants", defTheme["constants"])
    coloring = conTheme.get("coloring", defTheme["coloring"])
    edges = conTheme.get("edges", defTheme["edges"])

    try:
        config["layouts"].index(layout)
    except ValueError:
        layout = "forceDirectedLayout"

    newConfig = {string: var for string, var in zip(["constants", "coloring", "layout", "edges"],
                                                    [constants, coloring, layout, edges])}

    with open("../graph/config.js", "w") as file:
        file.write("let config =\n")
        json.dump(newConfig, file, indent=8)
        file.flush()


def _saveJSON(graph: Graph, clusters=None, cluster_edges=None, clusterSizes=None, algorithm="spectral_clustering") -> dict:
    """Creates a JSON containing data from clusters and clusterSizes"""
    JSON = {}

    # Sorted clusters
    clustersTuple = sorted(set(clusters.values()))
    clustersTuple = tuple(map(lambda x: str(x), clustersTuple))

    # initialize JSON with nodeNum, doneNum and origin values
    JSON.update({
        "variables": {
            "nodeNum": len(clusters.keys()),
            "clusters": clustersTuple,
            "numClusters": len(clustersTuple),
            "clusterEdges": {} if cluster_edges is None else cluster_edges,
            "clusterSizes": {} if clusterSizes is None else clusterSizes,
            "algorithm": algorithm
        },
        "nodes": {},
        "origin": {
                   "edges": tuple(str(edge) for edge in graph.nodes[graph.origin.id].edges),
                   "json": graph.nodes[graph.origin.id].user._json,
                   "done": str(graph.nodes[graph.origin.id].done),
                   "cluster": str(clusters[graph.origin.id])
                   }
    })

    # Add nodes in graph into JSON

    for id_ in clusters.keys():
        node = graph.nodes[id_]
        # if node.id == graph.origin.id:
        #     continue

        JSON["nodes"].update(
            {str(node.id):
                 {"edges": tuple(str(edge) for edge in node.edges),
                  "json": node.user._json,
                  "done": str(node.done),
                  "cluster": str(clusters[id_])
                  }
             })

    return JSON