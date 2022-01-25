from random import shuffle

from collections import namedtuple
from typing import Dict, Any, Tuple, MutableSet, Generator, List

import tweepy

NodeID = int
TweetID = str
NodeProgress = namedtuple("NodeProgress", ["DoneAddingFriendsIds", "DoneAddingFriendsUSERObject"])

class Node:

    def __init__(self, user: tweepy.User) -> None:
        self.user = user
        self.id: NodeID = user.id
        self.cursor = (0, -1)
        self.friendsIds = set()
        self.edges = set()  # Edges from self to other nodes in graph
        self.done: Tuple[bool, bool] = (False, False) # (FinishAddingFriendsIds, FinishAddingFriendsUserObjects)
        self.tweets: Dict[TweetID, tweepy.Status] = {}

        self.maxIdsToSearch = 500 # This ensures the graph doesnt become too surface level but limits its view 

    def __repr__(self) -> str:
        return f"{self.id}\t{self.user.screen_name}\t{self.done}"

    def addFriend(self, friends):
        self.friendsIds.update(friends)

    def listSearch(self, api: tweepy.API, depth: int=99999) -> Dict[NodeID, Any]:
        """
        Returns dictionary of all friends of self {ID : Node} and a saves cursor in self.cursor
        If limit does not run out before searching then assign self.done to (True, True)

        A depth parameter can be assigned to control how many batches of friends the function should get.
        This is important if the user is friends to more than 20 people. decreasing the depth casts a wider, but shallower net

        Note: each call to api.friends results in a maximum of 20 users returned
        """
        friendsDict: Dict[NodeID, Node] = {}
        limit = api.rate_limit_status()["resources"]["friends"]['/friends/list']["remaining"]
        if limit == 0:
            raise IOError("listSearch LIMIT REACHED")

        # Go through friends of self and add their ids to friendsIds and return the {ID : User} pair to graph
        cursor = self.cursor
        for _ in range(min(limit, depth)):
            friends, cursor = api.friends(screen_name=self.user.screen_name, count=200, cursor=self.cursor[1])
            friendsDict.update({friend.id: Node(friend) for friend in friends})

            # when finished through all friends for specified depth then mark user as done and break
            if cursor[1] == 0:
                self.done = (True, True)
                break

        self.cursor = cursor
        self.friendsIds.update(friendsDict.keys())
        return friendsDict

    def idSearch(self, api: tweepy.API) -> int:
        """Gets the first 5000 ids of self's friends and adds them to the friendsIds set then sets self.done[0] to
        True """
        try:
            ids = api.friends_ids(self.user.id, self.user.screen_name)  # Warning: Maximum of 5000
            ids = ids[:self.maxIdsToSearch]
            self.friendsIds.update(ids)
        except tweepy.error.TweepError as e:
            print(f"Encountered a TweepError while processing node {self.id}\n{e}\nAbandoning idSearch")
            return -1
        self.done = (True, self.done[1])
        return 0


class Graph:
    def __init__(self) -> None:
        self.nodes: Dict[NodeID, Node] = {} 
        self.screenNames: Dict[str, Dict[str, tweepy.Status]] = {} # Previously searched screenNames
        self.queries: Dict[str, Dict[str, tweepy.Status]] = {} # Previously searched queries

    ###Getter Methods###

    def checkFollowers(self, Id: NodeID) -> Tuple[NodeID]:
        return tuple(node.id for node in self.nodes.values() if Id in node.edges)

    def collectUnexplored(self) -> MutableSet[NodeID]:
        """Returns the union set of friendsIds that are not in self.nodes"""
        unexploredIds = set()
        for node in self.nodes.values():
            if any(node.done):
                s = set(Id for Id in node.friendsIds if Id not in self.nodes.keys())
                if len(s) == 0:
                    node.done = (True, True)
                else:
                    unexploredIds.update(s)
                # self.unexploredIds = self.unexploredIds.union(temp)
        return unexploredIds

    def collectFriendless(self) -> MutableSet[NodeID]:
        """Returns set of ids who have an empty node.friendsIds"""
        return set(node.id for node in self.nodes.values() if len(node.friendsIds) == 0)

    def getNodeNum(self) -> int:
        return len(self.nodes)

    def getDoneNum(self) -> int:
        return sum(1 for node in self.nodes.values() if any(node.done))

    ###Searching Methods###

    def getFriends(self, node: Node) -> MutableSet[tweepy.User]:
        """Return all friends of node that are in self.nodes in a set"""
        return set(friend[1] for friend in self.nodes.items() if friend[0] in node.friendsIds)

    def getLeafIds(self, start: List[NodeID]=[]) -> Generator:
        """Breadth first search generator for nodes that aren't in self.nodes"""
        if not start:
            start = list(self.screenNames.keys())

        visited = {Id: False for Id in self.nodes}
        stack = [*start]

        yielded = set() # Houses yielded leaf nodes

        while stack:
            current = stack.pop()
            visited[current] = True

            for Id in self.nodes[current].friendsIds:
                if Id in self.nodes:
                    if not visited[Id] and Id not in stack and any(self.nodes[Id].done):
                        stack.append(Id)
                else:
                    if Id not in yielded:
                        yielded.add(Id)
                        yield Id

    def getInternalIds(self) -> Generator:
        """Breadth first search generator for nodes that are in self.nodes and aren't done (not any(node.done))"""
        visited = {Id: False for Id in self.nodes}
        stack = list(self.screenNames.keys())

        done = set() # Houses yielded internal nodes, as well as leaf nodes connected to them

        while stack:
            current = stack.pop()
            visited[current] = True

            if not any(self.nodes[current].done):
                yield current

            for Id in self.nodes[current].friendsIds:
                if Id in self.nodes:
                    if not visited[Id] and Id not in stack:
                        stack.append(Id)
                else:
                    if Id not in done:
                        if current not in done:
                            done.add(current)
                            yield current
                        done.add(Id)

    def idSearch_graph(self, api: tweepy.API) -> None:
        """
        Gets friends ids of nodes if they aren't stored already, and stores them in the node's
        node.friendsIds set. And also changes the node's 'done' tuple

        Usage: Use this to quickly get many ids of related nodes.
        Note: This method gets 5000 ids per user
        """
        limit = api.rate_limit_status()["resources"]['friends']["/friends/ids"]["remaining"]

        for node in self.nodes.values():
            if not any(node.done):  # If already done skip
                if not node.user.protected:  # If protected label done and skip
                    if limit < 1:
                        break

                    if node.idSearch(api) == -1:
                        break
                    limit -= 1
                else:
                    node.done = (True, False)

    def mopSearch(self, api: tweepy.API, shuffleLeafIds: bool=True) -> None:
        """
        Gets friends of users and adds them to self.nodes
        
        I think I can call mopSearch many times, the documentation says maximum is 9, 
        but calling it with more than that was fine
        """
        nodeList = list(self.getLeafIds())
        if not nodeList:
            return

        if shuffleLeafIds:
            # SHUFFLING COULD LEAF TO SURFACE LEVEL GRAPH
            shuffle(nodeList)

        users = api.lookup_users(nodeList[:100])
        for user in users:
            if user.id not in self.nodes:
                self.nodes.update({user.id: Node(user)})

    def screenNamesSearch(self, api: tweepy.API, screenNames: List[str], addToScreenNames: bool=False) -> None:
        users = api.lookup_users(screen_names=screenNames[:100])
        for user in users:
            if user.id not in self.nodes:
                nd = Node(user)
                self.nodes.update({user.id: nd})
                if addToScreenNames:
                    self.screenNames[user.id] =  nd

    def listSearch_graph(self, api: tweepy.API, depth: int=5) -> None:
        """
        Executes listSearch on all nodes in graph.nodes that have unrecorded friends.
        Searching is ordered by insertion and stops when limit is zero or no further nodes need searching.

        Usage: This combines what idSearch and mopSearch do in a single function, but is much worse, since its limited
            to 20 users per call, where idSearch gets 5000 ids per call and mopSearch gets 100 users per call
        Note: A maximum depth value of 5 is set by default
        """
        nodeList = list(self.getInternalIds())

        try:
            while True:
                node: Node = self.nodes[nodeList.pop(0)]
                self.nodes.update(node.listSearch(api, depth=depth))
        except (IOError, StopIteration, IndexError):
            pass

    ###QureySearch Search Methods###

    def qureySearch(self, api: tweepy.API, qurey: str, numTweets: int=1000, enforceHashtag: bool=False):
        """
        Searches tweets in a qurey and stores each tweet in its author's Node.tweets
        if the author exists in graph.nodes, otherwise it creates one and adds the tweet
        
        It also adds the id_str to graph.queries[qurey]
        example input: qurey="#Cars", numTweets=180

        Note: numTweets=0 means max tweets 
        """
        if enforceHashtag:
            assert "#" == qurey[0], f"The symbol # is not the first character of the input qurey '{qurey}'"
            assert " " not in qurey, f"qurey '{qurey}' shouldn't include spaces"
            
        maxTweetsLimit = api.rate_limit_status()["resources"]["search"]["/search/tweets"]["remaining"] * 100
        if numTweets > maxTweetsLimit:
            raise IndexError

        if self.queries.get(qurey, None) is None:
            self.queries[qurey] = {}
        for tweet in tweepy.Cursor(api.search, q=qurey, rpp=100, tweet_mode="extended").items(numTweets):
            self.queries[qurey][tweet.id_str] = tweet
            if node := self.nodes.get(tweet.user.id, None):
                node.tweets[tweet.id_str] = tweet
            else:
                self.nodes[tweet.user.id] = Node(tweet.user)
                self.nodes[tweet.user.id].tweets[tweet.id_str] = tweet

    ###Edge Search Methods###

    def edgeSearch(self, node: Node, nodesSet: set) -> None:
        """Gets the intersection of given 'node' with self.nodes and stores them in node's edges set"""
        node.edges = nodesSet.intersection(node.friendsIds)

    def fullEdgeSearch(self, numNodes: int) -> None:
        """Executes edgeSearch numNodes number of nodes for nodes in self.nodes"""
        nodesSet = set(self.nodes)
        for i, node in enumerate(self.nodes.values()):
            self.edgeSearch(node, nodesSet)

            if i + 1 == numNodes:
                break

    ###Extra Methods###

    def printFriends(self, node: Node, indent: int=0, depth: int=9) -> str:
        if not node.edges:
            self.edgeSearch(node, set(self.nodes))
        crntIndent = " " * indent
        full = f"{node.user.screen_name}:\t[{len(node.friendsIds)} Friends]\t[{len(node.edges)} Mutual Friends]\n"
        partial = ""
        count = 0
        for count, friend in enumerate(node.friendsIds):
            if friend in self.nodes:
                full += f"{crntIndent}{count}. {self.nodes[friend].user.screen_name}\n"
            else:
                partial += f"{crntIndent}{count}. {friend}\n"
            if count == depth:
                break
        return full + partial + f"{crntIndent}And {len(node.friendsIds) - count} others\n\n"

    def display(self, start: bool=None, num: int=100, indent: int=2, depth: int=9) -> None:
        if not start:
            start = list(self.screenNames.values())[0]
        output = self.printFriends(start, indent, depth)
        nodeNum = sum(
            1 for _ in self.nodes.values())  # Total num of nodes
        printableNum = sum(
            1 for node in self.nodes.values() if any(node.done))  # Num of nodes with node.done: (True, False)

        for count, Id in enumerate(self.nodes.keys()):

            if count == num:
                output += f"Total Nodes is {nodeNum}, of which {printableNum} can be visualized " \
                          f"while {nodeNum - printableNum} cannot be\n"
                break

            if Id == start.id:
                continue

            if any(self.nodes[Id].done):
                output += self.printFriends(self.nodes[Id], indent, depth)
            else:
                count += -1

        print(output)


import tweepy
