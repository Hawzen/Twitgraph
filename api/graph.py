class Node:

    def __init__(self, user):
        self.user = user
        self.id = user.id
        self.cursor = (0, -1)
        self.friendsIds = set()
        self.edges = set()  # Edges from self to other nodes in graph
        self.done = (False, False)  # 1.Done adding friends' ids   2.Done adding friends' USER object to graph dict

    def addFriend(self, friends):
        self.friendsIds.update(friends)

    def listSearch(self, api, depth=99999):
        """
        Returns dictionary of all friends of self {ID : Node} and a saves cursor in self.cursor
        If limit does not run out before searching then assign self.done to (True, True)

        A depth parameter can be assigned to limit friend searching
        Raises IOError When limit == 0
        """
        friendsDict = {}  # A dict of IDs to USER objects related which stores friends of user
        limit = api.rate_limit_status()["resources"]["friends"]['/friends/list']["remaining"]
        if limit == 0:
            raise IOError("SEARCH LIST LIMIT REACHED")

        # Go through friends of self and add their ids to friendsIds and return the {ID : User} pair to graph
        cursor = self.cursor
        for _ in range(min(limit, depth)):
            friends, cursor = api.friends(screen_name=self.user.screen_name, count=200, cursor=self.cursor[1])
            friendsDict.update({friend.id: Node(friend) for friend in friends})

            # If you finished going through all the friends for the specified depth then mark user as done and break
            if cursor[1] == 0:
                self.done = (True, True)
                break

        # keep track of cursor
        self.cursor = cursor

        # Update friendsIds set with all new ids from friendsDict
        self.friendsIds.update(friendsDict.keys())

        # Return {ID : Node} pair to graph
        return friendsDict

    def idSearch(self, api):
        """Gets the first 5000 ids of self's friends and adds them to the friendsIds set then sets self.done[0] to True"""

        ids = api.friends_ids(self.user.id, self.user.screen_name)
        self.addFriend(ids)  # Warning: Maximum of 5000
        self.friendsIds.update(ids)
        self.done = (True, False)


class Graph:
    def __init__(self):
        self.nodeNum = 0
        self.doneNum = 0

        self._steps = 0
        self._currentCost = -1

        self.origin = None
        self.nodes = {}  # {id : Node}
        self.leafIterator = None  # Leaf node iterator
        self.intIterator = None  # Internal node iterator
        self.unexploredIds = set()  # Set of ids connected to nodes in self.nodes but yet to be added to self.nodes

    def setOrigin(self, api, userName):
        self.origin = Node(api.get_user(userName))
        self.nodes.update({self.origin.user.id: self.origin})

    def collectUnexplored(self):
        """Collects the union set of friendsIds in all nodes in self.nodes and stores them in self.unexploredIds"""
        for node in self.nodes.values():
            self.unexploredIds = set(Id for Id in node.friendsIds if Id not in self.nodes.keys())
            # self.unexploredIds = self.unexploredIds.union(temp)

    def getNodeNum(self):
        self.nodeNum = len(self.nodes)
        return self.nodeNum

    def getDoneNum(self):
        self.doneNum = sum(1 for node in self.nodes.values() if all(node.done))
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

    def iterator(self, internal):
        """
        When internal == False
        Return iterator over all leaf nodes

        Otherwise return an iterator over all unique parents of leaf nodes
        Note: The second case does not work when the level of the graph is less than 3
        """
        path = []
        done = set()
        current = self.origin.id  # Current is the current working node id
        while True:
            while current in self.nodes and \
                    any(node in self.nodes for node in self.nodes[current].friendsIds.difference(done)):
                # While current is internal and there are internal nodes
                if current not in path: path.append(current)
                friends = set(node for node in self.nodes[current].friendsIds if node not in done)  # Get all friendsIds except when done
                current = min(friends, key=self.searchCost) # Gives off 0 if node.friendsIds is not updated

            path.append(current)
            done.add(current)
            if current not in self.nodes:  # If current is leaf node, i.e. not searched
                if internal:
                    path.pop()
                    yield path.pop()  # Get internal node id
                else:
                    yield path.pop()  # Get leaf node id
            else:
                path.pop()

            if all(node in done for node in self.origin.friendsIds):
                raise StopIteration

            current = path[-1]

    def listSearch_graph(self, api, depth=15):
        """
        Executes list search starting from origin until limit runs out or no further nodes need searching
        """
        if not self.intIterator:
            self.intIterator = self.iterator(True)

        try:
            while True:
                node = self.nodes[next(self.intIterator)]
                self.nodes.update(node.listSearch(api, depth))
        except IOError or StopIteration:
            pass

    def idSearch_graph(self, api):
        """
        Goes through self.nodes and gets ids of all nodes in it when node.done is False and stores them in the node's
        node.friendsIds set.

        Note: This method gets 5000 ids per user
        """
        limit = api.rate_limit_status()["resources"]['friends']["/friends/ids"]["remaining"]
        print("idSearch limit is {}".format(limit))

        for node in self.nodes.values():
            if not any(node.done):
                if limit < 1:
                    break
                limit -= 1

                node.idSearch(api)
        print("{} Nodes left".format(self.getNodeNum() - self.getDoneNum()))

    def mopSearch(self, api):
        """
        Gets user id from self.leafIterator and executes api.getUser() on that id and adds resulting node to self.nodes
        limit number of times
        """
        if not self.leafIterator:
            self.leafIterator = self.iterator(False)

        limit = api.rate_limit_status()["resources"]['users']["/users/show/:id"]["remaining"]
        for _ in range(limit):
            node = Node(api.getUser(next(self.leafIterator)))
            self.nodes.update({node.id: node})

    ###Edge Search Methods###

    def edgeSearch(self, node: Node):
        """Gets the intersection of given 'node' with self.nodes and stores them in node's edges set"""
        node.edges = node.friendsIds.intersection(set(self.nodes.keys()))

    def fullEdgeSearch(self):
        for node in self.nodes.values():
            self.edgeSearch(node)

    ###Extra Methods###

    def printFriends(self, node: Node, indent=0, depth=9):
        if not node.edges:
            self.edgeSearch(node)
        crntIndent = " "*indent
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
        print(full + partial + f"{crntIndent}And {len(node.friendsIds) - count} others\n")

    def tree(self, start=None, indent=2, depth=9, done=None):
        if not done:
            done = set()
        if not start:
            start = self.origin

        self.printFriends(start, indent, depth)
        done.add(start)

        for friend in start.friendsIds.difference(self.nodes.keys()):
            if friend not in done:
                self.tree(self.nodes[friend], 2+indent, depth, done)
