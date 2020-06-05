from saving_and_loading import *
from time import sleep


def automate(screenName, graph, api, enumerations, quiet=False, dumb=True):
    for i in range(enumerations):
        graph.idSearch_graph(api)
        if graph.getNodeNum() - graph.getDoneNum() <= 15:
            graph.mopSearch(api)

        saveShelve(screenName, graph, dumb=dumb, onlyDone=True, numPartitions=50)
        if not quiet: print(f"\nFinished {i + 1} iteration.\n\tTotal number of nodes: {graph.getNodeNum()}\
                                    \n\tTotal number of done nodes: {graph.getDoneNum()}\n")

        for minute in range(15):
            if not quiet: print("\r░ MINUTES UNTIL NEXT BATCH\t{:>02}".format(15 - minute), end=" ")
            sleep(60)
        sleep(15)
        if not quiet: print("\r░ MINUTES UNTIL NEXT BATCH\t{:>02}".format(0), end=" ")
