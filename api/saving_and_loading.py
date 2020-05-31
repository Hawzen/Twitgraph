from graph import Graph
from spectral_clustering import getClusters
import tweepy
import shelve
import json
import sys


def loadAll(screenName):
    """Gets apiKey, apiSecretKey, accessToken, accessTokenSecret and username from file twitterkeys.txt in
    the same directory, preforms api authentication
    then loads graph and JSON objects from shelve If either does not exist then creates them and set graph origin as
    username

    return api, graph, JSON
    """
    with open('twitterkeys.txt', 'r') as file:
        lines = file.read().split('\n')
    apiKey = lines[0]
    apiSecretKey = lines[1]
    accessToken = lines[2]
    accessTokenSecret = lines[3]

    auth = tweepy.OAuthHandler(apiKey, apiSecretKey)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth)

    # Keep track of object target
    try:
        with shelve.open("shelve/graph_shelve") as sh:
            graph = sh[screenName]
    except KeyError:
        if input("Is the screen name you entered new? (y, n) ") == "n":  # FIXME
            print("screen name not found, quitting")
            sys.exit()

        graph = Graph()
        graph.setOrigin(api, screenName)

    return api, graph


def saveShelve(screenName, graph: Graph, dumb=False, onlyDone=True, numNodes=0,
               numPartitions=0):
    """Saves graph object to shelve as well as dumb the data to data.json if dumb=True"""

    with shelve.open("shelve/graph_shelve") as sh:
        sh[screenName] = graph

    if dumb:

        graph.fullEdgeSearch(numNodes)
        if numNodes == 0:
            numNodes = sum(1 for Id in graph.nodes.keys() if any(graph.nodes[Id].done))
        if numPartitions == 0:
            numPartitions = numNodes // 10

        if onlyDone:
            if numNodes > graph.getDoneNum():
                raise ArithmeticError("Not enough done nodes")
        elif numNodes > graph.getNodeNum():
            raise ArithmeticError("Not enough nodes")

        # If checkClusters then generate clusters dict and sizes dict
        cutNodes = {}  # Sliced version of dict
        for i, node in enumerate(graph.nodes.values()):

            if onlyDone and not any(node.done):
                continue

            if i == numNodes:
                break

            i += 1
            cutNodes.update({node.id: node})
        clusters = getClusters(cutNodes, numPartitions)  # {Id: cluster node belongs to}
        clusterSizes = \
            dict(  # {cluster: num nodes in cluster}
                map(
                    lambda x: (str(x), sum(1 for el in clusters.values() if el == x)), set(clusters.values())
                )
            )

        _dumpData(_saveJSON(graph, clusters, clusterSizes))


def _dumpData(JSON):
    """Dumps given JSON to data.json file"""
    with open("../data/data.json", "w") as data:
        data.write("let data = ")
        json.dump(JSON, data, indent=8)
        data.flush()


def _saveJSON(graph: Graph, clusters=None, clusterSizes=None):
    """Creates a JSON containing data from clusters and clusterSizes"""
    JSON = {}

    # Sorted clusters
    clustersTuple = sorted(list(set(clusters.values())), key=lambda x: -1 / x if str(x)[0] == "1" else x)
    clustersTuple = tuple(map(lambda x: str(x), clustersTuple))

    # initialize JSON with nodeNum, doneNum and origin values
    JSON.update({
        "variables": {
            "nodeNum": len(clusters.keys()),
            # "doneNum": graph.getDoneNum(),
            "clusters": clustersTuple,
            "numClusters": len(clustersTuple),
            "clusterSizes": {} if clusterSizes is None else clusterSizes
        },
        "nodes": {},
        "origin": {"edges": tuple(str(edge) for edge in graph.nodes[graph.origin.id].edges),
                   "json": graph.nodes[graph.origin.id].user._json,
                   "done": str(graph.nodes[graph.origin.id].done),
                   "cluster": str(clusters[graph.origin.id])
                   }
    })

    # Add nodes in graph into JSON

    for Id in clusters.keys():
        node = graph.nodes[Id]
        if node.id == graph.origin.id:
            continue

        JSON["nodes"].update(
            {str(node.id):
                 {"edges": tuple(str(edge) for edge in node.edges),
                  "json": node.user._json,
                  "done": str(node.done),
                  "cluster": str(clusters[Id])
                  }
             })

    return JSON
