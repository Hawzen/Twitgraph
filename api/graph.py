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

    def listSearch(self, api, depth=99999, limit=1):
        """
        Returns dictionary of all friends of self {ID : Node} and a saves cursor in self.cursor
        If limit does not run out before searching then assign self.done to (True, True)

        A depth parameter can be assigned to get a specific number of friends, if depth > total friends of self then
        the method will stop after it gets all friends

        Raises IOError When limit == 0

        When given a limit of -1 it computes the limit then searches until it
        finds all of self' friends or the limit runs out
        """
        friendsDict = {}  # A dict of {IDs: Node} objects related which stores friends of user
        if limit == -1:
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
        """Gets the first 5000 ids of self's friends and adds them to the friendsIds set then sets self.done[0] to True"""

        ids = api.friends_ids(self.user.id, self.user.screen_name)
        self.addFriend(ids)  # Warning: Maximum of 5000
        self.friendsIds.update(ids)
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
        self.friendlessIds = set() # Set of ids of nodes that have length zero of the node.friendsIds set

    def setOrigin(self, api, userName):
        self.origin = Node(api.get_user(userName))
        self.nodes.update({self.origin.user.id: self.origin})

    def collectUnexplored(self):
        """Collects the union set of friendsIds in all nodes in self.nodes and stores them in self.unexploredIds"""
        for node in self.nodes.values():
            self.unexploredIds.update(set(Id for Id in node.friendsIds if Id not in self.nodes.keys()))
            # self.unexploredIds = self.unexploredIds.union(temp)

    def collectFriendless(self):
        """NOTE: CONSIDERS 0 FRIENDS AS FRIENDLESS"""
        self.friendlessIds = set(node.id for node in self.nodes.values() if len(node.friendsIds) == 0)

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

    def iterator(self, internal):
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
                if current != path[-1]: path.append(current)  # FIXME: This is not elegant, should be redone

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
            if current == path[-1]: path.pop()  # FIXME: This is not elegant, should be redone
            current = path[-1]

    def listSearch_graph(self, api, limit=-1):
        """
        Executes list search starting from origin until limit runs out or no further nodes need searching

        Note: Limit on each listSearch is set to 1
        """
        if not self.parentNodes:
            self.parentNodes = list(self.iterator(True))
        if limit == -1:
            limit = api.rate_limit_status()["resources"]["friends"]['/friends/list']["remaining"]

        try:
            for _ in range(limit):
                node = self.nodes[self.parentNodes.pop(0)]
                self.nodes.update(node.listSearch(api, limit=1))
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

    def mopSearch(self, api, limit = -1):
        """
        Gets user id from self.leafNodes and executes api.getUser() on that id and adds resulting node to self.nodes
        limit number of times
        """
        if not self.leafNodes:
            self.leafNodes = list(self.iterator(False))

        # if not self.unexploredIds:
        #     self.collectUnexplored()

        if limit == -1:
            limit = api.rate_limit_status()["resources"]['users']['/users/lookup']['remaining']

        for _ in range(min([limit, len(self.leafNodes) // 100])):
            users = api.lookup_users(self.leafNodes[0:100])
            for user in users:
                self.nodes.update({user.id: Node(user)})
            self.leafNodes = self.leafNodes[100:]


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
        return full + partial + f"{crntIndent}And {len(node.friendsIds) - count} others\n"

    def display(self, start=None, num=100, indent=2, depth=9, done=None):
        if not start:
            start = self.origin
        output = self.printFriends(start, indent, depth)
        printableNum = sum(1 for node in self.nodes.values() if any(node.done))  # Num of nodes with node.done: (False, True)
        completeNum = sum(1 for node in self.nodes.values() if all(node.done))  # Num of nodes with node.done: (True, True)

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
