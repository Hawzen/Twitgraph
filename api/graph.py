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
        self.origin = None
        self.nodes = {}  # {id : Node}

    def setOrigin(self, api, userName):
        self.origin = Node(api.get_user(userName))
        self.nodes.update({self.origin.user.id: self.origin})

    ###Getter Methods###

    def checkFollowers(self, Id):
        return tuple(node.id for node in self.nodes.values() if Id in node.edges)

    def collectUnexplored(self):
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

    def collectFriendless(self):
        """Returns set of ids who have an empty node.friendsIds"""
        return set(node.id for node in self.nodes.values() if len(node.friendsIds) == 0)

    def getNodeNum(self):
        return len(self.nodes)

    def getDoneNum(self):
        return sum(1 for node in self.nodes.values() if any(node.done))

    ###Searching Methods###

    def searchCost(self, Id: int):
        """Returns number of friends of node of id ID
           Returns -1 if Id not in self.nodes"""
        if Id in self.nodes.keys():
            return len(self.nodes[Id].friendsIds)
        return -1

    def getFriends(self, node: Node):
        """Return all friends of node that are in self.nodes in a set"""
        return set(friend[1] for friend in self.nodes.items() if friend[0] in node.friendsIds)

    def getLeafIds(self):
        """Breadth first search generator for nodes that aren't in self.nodes"""
        visited = {Id: False for Id in self.nodes}
        stack = [self.origin.id]

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

    def getInternalIds(self):
        """Breadth first search generator for nodes that are in self.nodes and aren't done (not any(node.done))"""
        visited = {Id: False for Id in self.nodes}
        stack = [self.origin.id]

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

    def idSearch_graph(self, api):
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
                        print("Reached Limit idSearch, breaking...")
                        break

                    node.idSearch(api)
                    limit -= 1
                else:
                    node.done = (True, False)

    def mopSearch(self, api):
        """ Gets friends of users and adds them to self.nodes"""
        # nodeList = list(self.collectUnexplored())  # Look up these nodes
        nodeList = list(self.getLeafIds())
        limit = api.rate_limit_status()["resources"]['users']['/users/lookup']['remaining']

        if len(nodeList) == 0:
            return

        for _ in range(len(nodeList) // 100):
            users = api.lookup_users(nodeList[0:100])
            for user in users:
                if user.id not in self.nodes:
                    self.nodes.update({user.id: Node(user)})
            nodeList = nodeList[100:]

            limit += -1
            if limit == 1:
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
        """
        nodeList = list(self.getInternalIds())

        try:
            while True:
                node = self.nodes[nodeList.pop(0)]
                self.nodes.update(node.listSearch(api, depth=depth))
        except (IOError, StopIteration, IndexError):
            pass

    ###Edge Search Methods###

    def edgeSearch(self, node: Node, nodesSet: set):
        """Gets the intersection of given 'node' with self.nodes and stores them in node's edges set"""
        node.edges = nodesSet.intersection(node.friendsIds)

    def fullEdgeSearch(self, numNodes):
        """Executes edgeSearch numNodes number of nodes for nodes in self.nodes"""
        nodesSet = set(self.nodes)
        for i, node in enumerate(self.nodes.values()):
            self.edgeSearch(node, nodesSet)

            if i + 1 == numNodes:
                break

    ###Extra Methods###

    def printFriends(self, node: Node, indent=0, depth=9):
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
