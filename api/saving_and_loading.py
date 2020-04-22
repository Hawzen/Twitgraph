from graph import Graph
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


def saveShelve(graph, JSON, onlyDone=False):
    """"""
    with shelve.open("shelve/graph_shelve") as sh:
        saveJSON(JSON, graph, onlyDone)

        sh['JSON'] = JSON
        sh['graph'] = graph


def dumpData(JSON):
    """Dumps given JSON to data.json file"""
    with open("../data/data.json", "w") as data:
        data.write("data = ")
        json.dump(JSON, data, indent=8)


def saveJSON(JSON, graph: Graph, onlyDone=False):
    # initialize JSON it with nodeNum, doneNum and origin values
    JSON.update({
        "variables": {
            "nodeNum": graph.getNodeNum(),
            "doneNum": graph.getDoneNum(),
            "leafNodes": graph.leafNodes,
            "parentNodes": graph.parentNodes
        },
        "nodes": {},
        "origin": {"friends ids": len(graph.origin.friendsIds), "edges": tuple(graph.origin.edges),
                   "json": graph.origin.user._json, "done": str(graph.origin.done)}
    })

    # Add nodes in graph into JSON
    for node in graph.nodes.values():
        if onlyDone and not any(node.done): continue
        JSON["nodes"].update(
            {node.id:
                 {"friends ids": len(node.friendsIds), "edges": tuple(node.edges),
                  "json": node.user._json, "done": str(node.done)}
             })
