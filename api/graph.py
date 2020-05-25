class Node:

    def __init__(self, user):
        self.user = user
        self.id = user.id
        self.cursor = (0, -1)
        self.friendsIds = set()
        self.edges = set()  # Edges from self to other nodes in graph
        self.done = (False, False)  # 1.Done adding friends' ids   2.Done adding friends' USER object to graph dict

    def __repr__(self):
        return f"{self.id}\t{self.user.screen_name}\t{self.done}"

    def addFriend(self, friends):
        self.friendsIds.update(friends)

    def listSearch(self, api, depth=99999):
        """
        Returns dictionary of all friends of self {ID : Node} and a saves cursor in self.cursor
        If limit does not run out before searching then assign self.done to (True, True)

        A depth parameter can be assigned to control how many batches of friends the function should get.
        This is important if the user is friends to more than 20 people. decreasing the depth casts a wider, but shallower net

        Note: each call to api.friends results in a maximum of 20 users returned
        """
        friendsDict = {}  # A dict of {IDs: Node} objects related which stores friends of user
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

    def idSearch(self, api):
        """Gets the first 5000 ids of self's friends and adds them to the friendsIds set then sets self.done[0] to
        True """
        try:
            ids = api.friends_ids(self.user.id, self.user.screen_name)  # Warning: Maximum of 5000

            self.friendsIds.update(ids)
        except tweepy.error.TweepError:
            pass
        self.done = (True, self.done[1])


class Graph:
    def __init__(self):
        self.nodeNum = 0
        self.doneNum = 0

        self.origin = None
        self.nodes = {}  # {id : Node}
        self.leafNodes = []  # Ids of every leaf node in self.nodes
        self.parentNodes = []  # Ids of parents of every leaf node in self.nodes

        self.unexploredIds = set()  # Set of ids connected to nodes in self.nodes but yet to be added to self.nodes
        self.friendlessIds = set()  # Set of ids of nodes that have length zero of the node.friendsIds set

    def setOrigin(self, api, userName):
        self.origin = Node(api.get_user(userName))
        self.nodes.update({self.origin.user.id: self.origin})

    ###Getter Methods###

    def checkFollowers(self, Id):
        return tuple(node.id for node in self.nodes.values() if Id in node.edges)

    def collectUnexplored(self):
        """Collects the union set of friendsIds in all nodes in self.nodes and stores them in self.unexploredIds"""
        for node in self.nodes.values():
            if any(node.done):
                s = set(Id for Id in node.friendsIds if Id not in self.nodes.keys())
                if len(s) == 0:
                    node.done = (True, True)
                else:
                    self.unexploredIds.update(s)
                # self.unexploredIds = self.unexploredIds.union(temp)
        return self.unexploredIds

    def collectFriendless(self):
        """NOTE: CONSIDERS 0 FRIENDS AS FRIENDLESS"""
        return set(node.id for node in self.nodes.values() if len(node.friendsIds) == 0)

    def getNodeNum(self):
        self.nodeNum = len(self.nodes)
        return self.nodeNum

    def getDoneNum(self):
        self.doneNum = sum(1 for node in self.nodes.values() if any(node.done))
        return self.doneNum

    ###Searching Methods###

    def searchCost(self, ID: int):
        """Return number of friends of node of id ID
           Return -1 for nodes not in self.nodes
           Note: Be careful of inputting nodes that don't have their friendsIds set filled, they will always return 0"""
        if ID in self.nodes.keys():
            return len(self.nodes[ID].friendsIds)

        return -1

    def getFriends(self, node: Node):
        """Return all friends of node that are in self.nodes in a set"""
        return set(friend[1] for friend in self.nodes.items() if friend[0] in node.friendsIds)

    def iterator(self, internal):  # FIXME Redo using breadth first search
        """
        When internal == False
        Return iterator over all leaf nodes

        Otherwise return an iterator over all unique parents of leaf nodes
        Note: The second case does not work when the level of the graph is less than 3
        """
        current = self.origin.id  # Current is the current working node id
        path = [current]  # Stack to keep track of current path
        done = set()  # Set to keep track of which nodes already yielded
        while True:

            # While current is internal and there are internal nodes connected to it that arent in done
            while current in self.nodes and \
                    any(ID in self.nodes for ID in self.nodes[current].friendsIds if ID not in done and ID not in path):

                # Add current to path if isn't the last element
                if current != path[-1]: path.append(current)  # FIXME

                # Get all friendsIds except when done or when already passed
                friends = set(ID for ID in self.nodes[current].friendsIds if ID not in done and ID not in path)

                # Gives off 0 if node.friendsIds is not updated
                current = min(friends, key=self.searchCost)

            done.add(current)
            if current not in self.nodes:  # If current is leaf node, i.e. not searched
                if internal:
                    current = path[-1]
                    done.add(current)
                    yield current  # Get internal node id
                else:
                    yield current  # Get leaf node id

            if all(node in done for node in self.origin.friendsIds):
                raise StopIteration
            if current == path[-1]: path.pop()  # FIXME
            current = path[-1]

    def iterator2(self):
        visited = {Id: False for Id in self.nodes}
        stack = [self.origin.id]

        yielded = set()

        while stack:
            current = stack.pop()
            visited[current] = True

            for Id in self.nodes[current].friendsIds:
                if Id in self.nodes:
                    if not visited[Id] and Id not in stack:
                        stack.append(Id)
                else:
                    if Id not in yielded:
                        yielded.add(Id)
                        yield Id

    def idSearch_graph(self, api):
        """
        Gets friends ids of nodes if they aren't stored already, and stores them in the node's
        node.friendsIds set.

        Usage: Use this to quickly get many ids of related nodes. This is better used before mopSearch and listSearch
        Note: This method gets 5000 ids per user
        """
        limit = api.rate_limit_status()["resources"]['friends']["/friends/ids"]["remaining"]

        for node in self.nodes.values():
            if not any(node.done):  # If already done skip
                if not node.user.protected:  # If protected label done and skip
                    if limit < 1:
                        print("Reached Limit idSearch, breaking...")
                        break

                    node.idSearch(api)
                    limit -= 1
                else:
                    node.done = (True, False)

    def mopSearch(self, api):
        """ Gets friends of users and adds them to self.nodes"""
        # nodeList = list(self.collectUnexplored())  # Look up these nodes
        if not self.leafNodes:
            self.leafNodes = list(self.iterator(False))
        nodeList = self.leafNodes
        limit = api.rate_limit_status()["resources"]['users']['/users/lookup']['remaining']

        for _ in range(len(nodeList) // 100):
            users = api.lookup_users(nodeList[0:100])
            for user in users:
                if user.id not in self.nodes:
                    self.nodes.update({user.id: Node(user)})
            nodeList = nodeList[100:]

            limit += -1
            if limit == 0:
                break
        else: # This else is visited after the for finishes and when it doesnt encounter a 'break'
            users = api.lookup_users(nodeList)
            for user in users:
                self.nodes.update({user.id: Node(user)})

    def listSearch_graph(self, api, depth=5):
        """
        Executes listSearch on all nodes in graph.nodes that have unrecorded friends.
        Searching is ordered by insertion and stops when limit is zero or no further nodes need searching.

        Usage: This combines what idSearch and mopSearch do in a single function, but is much worse, since its limited
            to 20 users per call, where idSearch gets 5000 ids per call and mopSearch gets 100 users per call
        Note: A maximum depth value of 5 is set by default

        WARNING: This could create problems when used with other searching functions. Use
        """
        if not self.parentNodes:
            self.parentNodes = list(self.iterator(True))

        try:
            while True:
                node = self.nodes[self.parentNodes.pop(0)]
                self.nodes.update(node.listSearch(api, depth=depth))
        except IOError:
            pass
        except StopIteration:
            pass
        except IndexError:  # If parentNodes is empty, create it again
            self.parentNodes = list(self.iterator(True))

    ###Edge Search Methods###

    def edgeSearch(self, node: Node, nodesSet=None):
        """Gets the intersection of given 'node' with self.nodes and stores them in node's edges set"""
        if nodesSet is None:
            nodesSet = set(self.nodes)

        node.edges = nodesSet.intersection(node.friendsIds)

    def fullEdgeSearch(self, numNodes):
        """Repeats for all nodes when numNodes == 0"""
        nodesSet = set(self.nodes)
        for i, node in enumerate(self.nodes.values()):
            self.edgeSearch(node, nodesSet)

            if i + 1 == numNodes:
                break

    ###Extra Methods###

    def printFriends(self, node: Node, indent=0, depth=9):
        if not node.edges:
            self.edgeSearch(node)
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

    def display(self, start=None, num=100, indent=2, depth=9):
        if not start:
            start = self.origin
        output = self.printFriends(start, indent, depth)
        printableNum = sum(
            1 for node in self.nodes.values() if any(node.done))  # Num of nodes with node.done: (False, True)
        completeNum = sum(
            1 for node in self.nodes.values() if all(node.done))  # Num of nodes with node.done: (True, True)

        for count, friend in enumerate(self.nodes.keys()):
            if any(self.nodes[friend].done):
                output += self.printFriends(self.nodes[friend], indent, depth)
            else:
                count += -1
            if count == num:
                output += f"Total Nodes is {printableNum}, of which {completeNum} had all of their friends be in " \
                          f"graph.nodes and {printableNum - completeNum} only had the ids of their friends stored\n" \
                          f"Number of nodes printed is {count + 1}\n"
                break
        print(output)


import tweepy
