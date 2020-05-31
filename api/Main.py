from saving_and_loading import *
from time import sleep

# screenName = input("Enter a twitter handle to be searched:\t")
screenName = "_KSU"
api, graph = loadAll(screenName)

minutes = 15
enumerations = 80

sve = True if input("Save data? (y/n) ") == "y" else False
graph.listSearch_graph(api, depth=99)
for i in range(enumerations):
    print(f"\nFAfter Lst Search.\n\tTotal number of nodes: {graph.getNodeNum()}\
                                \n\tTotal number of done nodes: {graph.getDoneNum()}\n")

    graph.idSearch_graph(api)
    print(f"\nFAfter Id Search.\n\tTotal number of nodes: {graph.getNodeNum()}\
                                \n\tTotal number of done nodes: {graph.getDoneNum()}\n")

    # if graph.getNodeNum() - graph.getDoneNum() <= 15:
    #     graph.mopSearch(api)

    saveShelve(screenName, graph, dumb=sve, onlyDone=True, numPartitions=50)
    finished = list(node.id for node in graph.nodes.values() if any(node.done))
    with open("logs.txt", 'a') as file:
        file.write(str(finished))

    print(f"\nFinished {i + 1} iteration.\n\tTotal number of nodes: {graph.getNodeNum()}\
                                \n\tTotal number of done nodes: {graph.getDoneNum()}\n")
    for minute in range(15):
        print("\r░ MINUTES UNTIL NEXT BATCH\t{:>02}".format(15 - minute), end=" ")
        sleep(60)
    sleep(15)
    print("\r░ MINUTES UNTIL NEXT BATCH\t{:>02}".format(0), end=" ")

### Data
# X TODO: Check cluster splitting if works
# TODO: Add level of node with respect to origin to node attributes
# X TODO: Add 'weight' function that calculates weight of any edge
# TODO: Add database of twitter shelves
# X TODO: Add node.numFriends in JSON
# X TODO: CLUSTER HIERARCHY
# X  1- Each node should belong to a family of clusters where 'node.cluster = 2122' means the node's ancestors
#   belong to the second cluster, and its grandfather belongs to the first subcluster.. etc


### Graph
# X TODO: Change size of each node depending on node.numFriends (in JSON)
# TODO: Add 'Overview' button that highlights general information about the graph
# X TODO: Add minimap
# X TODO: Cluster hierarchy:
# X  1- Edges between clusters and subclusters are dotted, thick and have a unique color
# X TODO: Clusters as nodes:
# X  1- Add clusters info box that provides a short summary of all clusters
# X  2- Clicking a cluster shows all names of nodes inside of it and maybe other info
# N  3- Implement some sort of accompanying animation (If it takes too much time no need)
# X  4- Cluster nodes should size according to the number of elements inside of it
# N  5- Nodes inside cluster should be hidden until user clicks cluster node


### Later
# TODO: Generate graph automatically given screen name, Oauth info and runs browser
# TODO: Add about button

# graph.display()


saveShelve(screenName, graph, dumb=sve, onlyDone=True, numNodes=0, numPartitions=50)
