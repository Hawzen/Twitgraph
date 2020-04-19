from saving_and_loading import *
from time import sleep

api, graph, JSON = loadAll()

for _ in range(2):
    # listLimit = api.rate_limit_status()["resources"]["friends"]['/friends/list']["remaining"]
    mopLimit = api.rate_limit_status()["resources"]['users']['/users/lookup']['remaining']
    # graph.idSearch_graph(api)
    # saveShelve(graph, JSON)

    # for _ in range(listLimit):
    #     graph.listSearch_graph(api, 1)
    #     saveShelve(graph, JSON)

    for _ in range(min((mopLimit, 200))): # Suspends executing for some reason after requesting within limit, FIXME
        graph.mopSearch(api)
        saveShelve(graph, JSON)

    sleep(15*61)

#graph.display()

saveShelve(graph, JSON)

if input("Save data? (y/n) ") == "y":
    graph.fullEdgeSearch()
    dumpData(JSON)
