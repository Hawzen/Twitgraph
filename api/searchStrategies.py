from time import sleep
from itertools import zip_longest
from typing import Generator, Dict, List

import tweepy
from tqdm import tqdm

from graph import Graph
from saving_and_loading import saveShelve


def followersStrategy(key: str, graph: Graph, api: tweepy.API, nIterations: int,
                    maxNumCallsMop=10, startingScreenNames: List[str]=[]) -> Generator:
    """Searches by looking at followers of a target key, then followers of that follower and so on"""
    graph.screenNamesSearch(api, startingScreenNames, addToScreenNames=True)
    for i in range(nIterations):
        try:
            graph.idSearch_graph(api)
            for j in range(maxNumCallsMop):
                    graph.mopSearch(api)
        except tweepy.TweepError as e:
            print(f"{e}\nError in FollowersStrategy iteration {i} mopCall {j}")

        saveShelve(key, graph, onlyDone=True)
        yield None

def queryStrategy(key: str, graph: Graph, api: tweepy.API, queries=[], numTweetsPerQurey=[]) -> Generator:
    """Searches by investigating a search qurey"""
    for qurey, numTweets in zip(queries, numTweetsPerQurey):
        try:
            graph.qureySearch(api, qurey, numTweets)
        except tweepy.TweepError as e:
            print(f"{e}\nError in QureyStrategy qurey {qurey} numTweets {numTweets}")
        except IndexError: # Happens when rate limited
            yield None
            graph.qureySearch(api, qurey, numTweets)

        saveShelve(key, graph, onlyDone=True)

def wait15mins(nIterations):
    for _ in range(nIterations):
        sleep(60 * 15 + 10) # Sleep for fifteen minutes and a bit
        yield

def mixStrategies(nIterations: int, strategiesIterators=[]):
    for i, _ in enumerate(tqdm(zip_longest(*strategiesIterators), total=nIterations)):
        pass