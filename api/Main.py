import tweepy
import shelve
import json
from api_funcs import *

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

graph.tree()

# graph.collectUnexplored()
# graph.idSearch_graph(api)

# generator = graph.iterator(False)
# next(generator)
# next(generator)
# next(generator)

with shelve.open("shelve/graph_shelve") as sh:
    saveJSON(JSON, graph)
    sh['JSON'] = JSON
    sh['graph'] = graph

if input("Save data? (y/n) ") == "y":
    with open("../data/data.json", "w") as data:
        data.write("data = ")
        json.dump(JSON, data, indent=8)
