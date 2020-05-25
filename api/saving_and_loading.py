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
        if input("Is the screen name you entered new? (y, n) ") == "n": # FIXME
            print("screen name not found, quitting")
            sys.exit()

        graph = Graph()
        graph.setOrigin(api, screenName)

    return api, graph


def saveShelve(screenName, graph: Graph, dumb=False, onlyDone=True, checkEdges=False, checkClusters=False, numNodes=0, numPartitions=0):
    """"""

    with shelve.open("shelve/graph_shelve") as sh:
        sh[screenName] = graph

    if dumb:

        if checkEdges:
            graph.fullEdgeSearch(numNodes)
        if numNodes == 0:
            numNodes = sum(1 for Id in graph.nodes.keys() if any(graph.nodes[Id].done))
        if numPartitions == 0:
            numPartitions = numNodes // 10
        clusters = None
        clusterSizes = None
        # If checkClusters then generate clusters dict and sizes dict
        if checkClusters:
            cutNodes = {}  # Sliced version of dict
            for i, node in enumerate(graph.nodes.values()):
                if i == numNodes:
                    break
                i += 1
                cutNodes.update({node.id: node})
            clusters = getClusters(cutNodes, numPartitions)
            clusterSizes = dict(
                map(lambda x: (str(x), sum(1 for el in clusters.values() if el == x)), set(clusters.values())))

        _dumpData(_saveJSON(graph, numNodes, onlyDone, clusters, clusterSizes))


def _dumpData(JSON):
    """Dumps given JSON to data.json file"""
    with open("../data/data.json", "w") as data:
        data.write("let data = ")
        json.dump(JSON, data, indent=8)


def _saveJSON(graph: Graph, numNodes, onlyDone=True, clusters=None, clusterSizes=None):
    """Updates the JSON dict and returns it
    onlyDone adds the nodes which pass any(node.done)
    numNodes only add the number of nodes specified by it, 0 means all"""
    if clusters is None:
        clusters = {}
    JSON = {}

    clustersTuple = sorted(list(set(clusters.values())), key=lambda x: -1/x if str(x)[0] == "1" else x)
    clustersTuple = tuple(map(lambda x: str(x), clustersTuple))
    # initialize JSON with nodeNum, doneNum and origin values
    JSON.update({
        "variables": {
            "nodeNum": numNodes if numNodes else graph.getNodeNum(),
            # "doneNum": graph.getDoneNum(),
            "clusters": clustersTuple,
            "numClusters": len(clustersTuple),
            "clusterSizes": {} if clusterSizes is None else clusterSizes
        },
        "nodes": {},
        "origin": {"friends ids": len(graph.origin.friendsIds),
                   "edges": tuple(str(edge) for edge in graph.origin.edges),
                   "json": graph.origin.user._json,
                   "done": str(graph.origin.done),
                   "cluster": "5" if graph.origin.id not in clusters else str(clusters[graph.origin.id])
                   }
    })

    # Add nodes in graph into JSON

    i = 0
    for node in graph.nodes.values():
        if onlyDone and not any(node.done) or node.id == graph.origin.id:
            continue

        if numNodes:
            if numNodes == i:
                break
            i += 1

        JSON["nodes"].update(
            {str(node.id):
                 {"friends ids": len(node.friendsIds),
                  "edges": tuple(str(edge) for edge in node.edges),
                  "json": node.user._json,
                  "done": str(node.done),
                  "cluster": "5" if node.id not in clusters else str(clusters[node.id])
                  }
             })

    return JSON
