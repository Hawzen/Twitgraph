from time import sleep

import tweepy
from tqdm import tqdm

from graph import Graph
from saving_and_loading import saveShelve


def followersStrategy(screenName: str, graph: Graph, api: tweepy.API, nIterations: int, 
                    quiet: bool=False, dump: bool=False) -> None:
    """Searches by looking at followers of a target screenName, then followers of that follower and so on"""
    try:
        for i in tqdm(range(nIterations)):
            graph.idSearch_graph(api)
            if graph.getNodeNum() - graph.getDoneNum() <= 15:
                graph.mopSearch(api)

            saveShelve(screenName, graph, dump=dump, onlyDone=True)
            if not quiet: print(f"\nFinished {i + 1} iteration.\n\tTotal number of nodes: {graph.getNodeNum()}\
                                        \n\tTotal number of done nodes: {graph.getDoneNum()}\n")

            for minute in range(15):
                # if not quiet: print("\r░ MINUTES UNTIL NEXT BATCH\t{:>02}".format(15 - minute), end=" ")
                sleep(60)
            sleep(15)
            # if not quiet: print("\r░ MINUTES UNTIL NEXT BATCH\t{:>02}".format(0), end=" ")
    finally:
        saveShelve(screenName, graph, dump=dump, onlyDone=True)