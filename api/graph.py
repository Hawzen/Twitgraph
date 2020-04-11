class Node:

    def __init__(self, user):
        self.user = user
        self.cursor = (0, -1)
        self.friendsIds = set()
        self.edges = set() # Edges from self to other nodes in graph
        self.done = (False, False)  # 1.Done adding everyone's ids   2.done adding everyone's USER object to graph dict

    def addFriend(self, friends):
        self.friendsIds.update(friends)

    def listSearch(self, api, depth=5000):
        """ """
        friendsDict = {}  # A dict of IDs to USER objects related which stores friends of user
        rateLimit = api.rate_limit_status()["resources"]["friends"]['/friends/list']["remaining"]

        # Go through friends of self and add their ids to friendsIds and return the {ID : User} pair to graph
        cursor = self.cursor
        for _ in range(rateLimit):
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
        self.done = True


class Graph:
    def __init__(self):
        self.nodeNum = 0
        self.doneNum = 0
        self.origin = None
        self.nodes = {}  # {id : Node}
        self.unexploredNodes = set() # Set of ids connected to nodes in self.nodes but yet to be added to self.nodes

    def setOrigin(self, api, userName):
        self.origin = Node(api.get_user(userName))
        self.nodes.update({self.origin.user.id: self.origin})

    def collectUnexplored(self):
        """Collects the union set of friendsIds in all nodes in self.nodes and stores them in self.unexploredNodes"""
        for node in self.nodes.values():
            temp = set(Id for Id in node.friendsIds if Id not in self.nodes.values())
            self.unexploredNodes = self.unexploredNodes.union(temp)

    def getNodeNum(self):
        self.nodeNum = len(self.nodes)
        return self.nodeNum

    def getDoneNum(self):
        self.doneNum = sum(1 for node in self.nodes.values() if all(node.done))
        return self.doneNum

    ###Searching Methods###

    #TODO: Implement the method below
    '''
    def listSearch_graph(self, api):
        """
        Breadth first listSearch starting from origin's friends, executing one listSearch per call
        """
        try:
            current
        except NameError:
            current = self.origin
            
        set().
    '''

    def idSearch_graph(self, api):
        """
        Goes through self.nodes and gets ids of all nodes in it when node.done is False and stores them in the node's
        node.friendsIds set. Then sets all(node.done) to True.

        Note: This method gets 5000 ids per user
        """
        limit = api.rate_limit_status()["resources"]['friends']["/friends/ids"]["remaining"]
        print("idSearch limit is {}".format(limit))

        for node in self.nodes.values():
            if not node.done:
                if limit < 1:
                    break
                limit -= 1

                node.idSearch(api)
                self.doneNum += 1
        print("{} Nodes left".format(self.getNodeNum() - self.getDoneNum()))

    def mopSearch(self, api):
        """Goes through self.unexploredNodes set and searches ids adds them to self.nodes"""
        if not self.unexploredNodes:  # If its empty, collect unexplored
            self.collectUnexplored()

        limit = api.rate_limit_status()["resources"]['users']["/users/show/:id"]["remaining"]
        print("idSearch limit is {}".format(limit))
        for _ in range(limit):
            node = Node(api.getUser(self.unexploredNodes.pop()))
            self.nodes.update({node.user.id: node})
        print("{} Nodes left".format(len(self.unexploredNodes)))

    ###Edge Search Methods###

    def edgeSearch(self, node: Node):
        """Stores the intersection of node with self.nodes in node's edges"""
        node.edges = node.friendsIds.intersection(set(self.nodes.keys()))

    def fullEdgeSearch(self):
        for node in self.nodes.values():
            self.edgeSearch(node)


