from saving_and_loading import *
from time import sleep

api, graph, JSON = loadAll()

# for _ in range(1):
#     # listLimit = api.rate_limit_status()["resources"]["friends"]['/friends/list']["remaining"]
#     # mopLimit = api.rate_limit_status()["resources"]['users']['/users/lookup']['remaining']
#     graph.idSearch_graph(api)
#     # saveShelve(graph, JSON)
#
#     # for _ in range(listLimit):
#     #     graph.listSearch_graph(api, 1)
#     #     saveShelve(graph, JSON)
#
#     # for _ in range(min((mopLimit, 200))): # Suspends executing for some reason after requesting within limit, FIXME
#     #     graph.mopSearch(api)
#     #     saveShelve(graph, JSON)
#
#     #sleep(15*61)

# TODO: Add level of node with respect to origin
# TODO: Add database of twitter shelves
# TODO: Search IDs automatically


# graph.display()

saveShelve(graph, JSON, True)

if input("Save data? (y/n) ") == "y":
    graph.fullEdgeSearch()
    dumpData(JSON)
