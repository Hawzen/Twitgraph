from graph import Graph
from spectral_clustering import getClusters
import tweepy
import shelve
import json



def loadAll():
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
    username = lines[4]

    auth = tweepy.OAuthHandler(apiKey, apiSecretKey)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth)

    # Keep track of object target
    try:
        with shelve.open("shelve/graph_shelve") as sh:
            graph = sh['graph']
            JSON = sh["JSON"]
    except KeyError:
        graph = Graph()
        graph.setOrigin(api, username)
        graph.nodes.update(graph.origin.listSearch(api))
        JSON = {}

    return api, graph, JSON


def saveShelve(graph: Graph, JSON, onlyDone=False, checkEdges=False, checkClusters=False, numNodes=0, numClusters=2):
    """"""
    if checkEdges:
        graph.fullEdgeSearch(numNodes)

    if checkClusters:
        cutNodes = {} # Sliced version of dict
        for i, node in enumerate(graph.nodes.values()):
            if i == numNodes:
                break
            i += 1

            cutNodes.update({node.id: node})
    clusters = None if not checkClusters else getClusters(cutNodes, numClusters)


    with shelve.open("shelve/graph_shelve") as sh:
        JSON = saveJSON(JSON, graph, onlyDone, numNodes, clusters)

        sh['JSON'] = JSON
        sh['graph'] = graph


def dumpData(JSON):
    """Dumps given JSON to data.json file"""
    with open("../data/data.json", "w") as data:
        data.write("let data = ")
        json.dump(JSON, data, indent=8)


def saveJSON(JSON, graph: Graph, onlyDone=False, numNodes=0, clusters=None):
    """Updates the JSON dict and returns it
    onlyDone adds the nodes which pass any(node.done)
    numNodes only add the number of nodes specified by it, 0 means all"""
    if clusters is None:
        clusters = {}
    if numNodes:
        JSON = {}

    # initialize JSON with nodeNum, doneNum and origin values
    JSON.update({
        "variables": {
            "nodeNum": numNodes if numNodes else graph.getNodeNum(),
            # "doneNum": graph.getDoneNum(),
            "clusters": tuple(set(clusters.values()))
        },
        "nodes": {},
        "origin": {"friends ids": len(graph.origin.friendsIds),
                   "edges": tuple(str(edge) for edge in graph.origin.edges),
                   "json": graph.origin.user._json,
                   "done": str(graph.origin.done),
                   "cluster": 0 if graph.origin.id not in clusters else clusters[graph.origin.id]
                   }
    })

    # Add nodes in graph into JSON

    if numNodes: i = 0
    for node in graph.nodes.values():
        if onlyDone and not any(node.done): continue
        if node.id == graph.origin.id: continue

        if numNodes:
            if numNodes == i:
                break
            else:
                i += 1

        JSON["nodes"].update(
            {str(node.id):
                 {"friends ids": len(node.friendsIds),
                  "edges": tuple(str(edge) for edge in node.edges),
                  "json": node.user._json,
                  "done": str(node.done),
                  "cluster": 0 if node.id not in clusters else clusters[node.id]
                  }
             })

    return JSON
