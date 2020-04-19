from saving_and_loading import *
from time import sleep

api, graph, JSON = loadAll()

#graph.idSearch_graph(api)
graph.mopSearch(api)
#graph.listSearch_graph(api)

#graph.display()

saveShelve(graph, JSON)

if input("Save data? (y/n) ") == "y":
    graph.fullEdgeSearch()
    dumpData(JSON)
