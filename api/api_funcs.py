from graph import Node, Graph


def checkRate(rate):
    """Returns a boolean of False when the rate function gives off values less than 1"""
    if rate() < 1:
        return False
    return True


def saveJSON(JSON, graph: Graph):
    # initialize JSON it with nodeNum, doneNum and origin values
    JSON.update({
        "variables": {
            "nodeNum": graph.getNodeNum(),
            "doneNum": graph.getDoneNum()
        },
        "nodes": {},
        "origin": {"friends ids": tuple(graph.origin.friendsIds), "edges": tuple(graph.origin.edges),
                   "json": graph.origin.user._json, "done": str(graph.origin.done)}
    })

    # Add nodes in graph into JSON
    for node in graph.nodes.values():
        JSON["nodes"].update(
            {node.user.id:
                {"friends ids": tuple(node.friendsIds), "edges": tuple(node.edges),
                 "json": node.user._json, "done": str(node.done)}
             })
