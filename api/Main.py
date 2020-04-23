from saving_and_loading import *
from time import sleep

api, graph, JSON = loadAll()

minutes = 15
enumerations = 25

for i in range(enumerations):
    # listLimit = api.rate_limit_status()["resources"]["friends"]['/friends/list']["remaining"]
    # mopLimit = api.rate_limit_status()["resources"]['users']['/users/lookup']['remaining']
    graph.idSearch_graph(api)
    # saveShelve(graph, JSON)

    # for _ in range(listLimit):
    #     graph.listSearch_graph(api, 1)
    #     saveShelve(graph, JSON)

    # for _ in range(min((mopLimit, 200))): # Suspends executing for some reason after requesting within limit, FIXME
    #     graph.mopSearch(api)
    #     saveShelve(graph, JSON)
    saveShelve(graph, JSON, True)
    print(f"Finish going through {i+1} loop, sleeping for 15 minutes and 15 seconds\n")

    for minute in range(15):
        s = "\r░ MINUTES UNTIL NEXT BATCH\t{:>02}".format(15 - minute)
        print(s, end=" ")
        sleep(60)
    sleep(15)

# TODO: Add level of node with respect to origin
# TODO: Add database of twitter shelves
# TODO: Search IDs automatically


# graph.display()

# saveShelve(graph, JSON, True)

# if input("Save data? (y/n) ") == "y":
#     graph.fullEdgeSearch()
#     dumpData(JSON)
