import sys
from warnings import warn
from os.path import abspath
from argparse import ArgumentParser, RawTextHelpFormatter

from saving_and_loading import *
from searchStrategies import followersStrategy, queryStrategy, wait15mins,mixStrategies

dbKeyHelp = "Name of database (using a name for the first time will create one, otherwise will use the existing DB)"

parser = ArgumentParser(prog="Twitgraph",
                        description="collect:\tCollect data from twitter api.\n"
                                    "keys:\tList and/or delete keys from database.\n"
                                    "stats:\t\tPrint statistics of handles.\n"
                                    "visualize:\tVisualize graph.",
                        formatter_class=RawTextHelpFormatter)
subParsers = parser.add_subparsers(dest="selector")

# Search Data
dataParse = subParsers.add_parser("collect", description="Collect data from twitter api")
dataParse.add_argument("-k", "--key", dest="key", metavar="DBKey", help=dbKeyHelp, required=True)
dataParse.add_argument("-H", "--handles", dest="screenNames", action="append", nargs="+", metavar="Handles to search from", 
                    help="Twitter handle(s) to begin searching from (the part in brackets @[foo])")
dataParse.add_argument("-q", "--queries", dest="queries", action="append", nargs="+", 
                help="queries to collect users from")
dataParse.add_argument("-m", "--maxTweetsPerQurey", dest="maxTweetsPerQurey", metavar="maxTweets", default=[], type=int, nargs="*",
                       help="Maximum number of tweets to collect per qurey (e.g. '-m 1000 300 500'). Defaults to 1000")
dataParse.add_argument("-n", "--nIterations", dest="nIterations", metavar="nIterations", default=1, type=int,
                       help="Number of times the api is called (each takes 15 minutes)")

# Get/Delete keys
keyParser = subParsers.add_parser("keys", description="List and/or delete keys from database")
keyParser.add_argument("-k", "--key", dest="key", metavar="DBKey", help=dbKeyHelp)
keyParser.add_argument("-d", "--delete", dest="deleteSome", action="store_true",
                       help="Delete all information of a handle or more")

# Show data
showParse = subParsers.add_parser("stats", description="Print contents of one or more handles")
showParse.add_argument("-k", "--key", dest="key", action="append", nargs="+", metavar="DBKey", help=dbKeyHelp)
showParse.add_argument("-p", "--peek", dest="peek", action="store_true",
                       help="Print the first 10 users in selected handles")

# Create visual
visualParse = subParsers.add_parser("visualize", description="Visualize graph")
visualParse.add_argument("-k", "--key", dest="key", metavar="DBKey", help=dbKeyHelp, required=True)
visualParse.add_argument("-n", "--nodenum", dest="nodeNum", metavar="Node Number", type=int, default=0,
                         help="Number of nodes visualized (default for all nodes)")
visualParse.add_argument("-p", "--n_clusters", dest="n_clusters", metavar="Partition Number", type=int, default=0,
                         help="Number of times data is partitioned (default for 0.1 of node number)")
visualParse.add_argument("-t", "--theme", dest="theme", metavar="Theme", default="default",
                         help="Visual style of graph")
visualParse.add_argument("-l", "--layout", dest="layout", metavar="Layout", default="default",
                         help="Layout of (x, y) positions of nodes in the graph")
visualParse.add_argument("-a", "--algorithm", dest="algorithm", metavar="algorithm", default="spectral_clustering",
                         help="Choice of algorithm (spectral_clustering, HDBSCAN)")


args = parser.parse_args()

if args.selector is None:
    parser.print_help()

elif args.selector == "collect":

    # Check name
    newName = False
    if args.key not in getShelveKeys():
        if input(f"Key {args.key} not in database. Do you want to create it? (y/n) ") != "y":
            print("Quitting")
            sys.exit()
        else:
            newName = True

    # Check API
    api, graph = loadAll(args.key, newName)

    strategies = []
    if args.screenNames:
        args.screenNames = args.screenNames[0]
        strategies.append(followersStrategy(key=args.key, graph=graph, api=api, nIterations=args.nIterations, 
            startingScreenNames=args.screenNames))

    if args.queries:
        args.queries = args.queries[0]
        if not args.maxTweetsPerQurey:
            args.maxTweetsPerQurey = [1000] * len(args.queries)
        elif len(args.maxTweetsPerQurey) != len(args.queries):
            raise IndexError(f"queries and maxTweetsPerQurey length mismatch")
        strategies.append(queryStrategy(key=args.key, graph=graph, api=api, queries=args.queries, 
            numTweetsPerQurey=args.maxTweetsPerQurey))

    if not strategies:
        raise ValueError("You must choose queries, screenName, or both to start the search")

    if args.nIterations > 1:
        strategies.append(wait15mins(args.nIterations))

    mixStrategies(nIterations=args.nIterations, strategiesIterators=strategies)

elif args.selector == "keys":
    if args.deleteSome:
            if input(f"Do you want to delete {args.key}? (y/n) ") == "y":
                deleteShelveKey(args.key)
    print("\nCurrent screen names are:")
    for key in getShelveKeys():
        print(f"\t{key}")

elif args.selector == "stats":
    if args.key is None:
        args.key = getShelveKeys()

    args.key = args.key[0]

    for screenName in args.key:
        print(args.key)
        graph = loadGraph(screenName)
        graph.display(num=10 if args.peek else 0, depth=5)

elif args.selector == "visualize":
    saveShelve(args.key, loadGraph(args.key), dump=True, onlyDone=False, numNodes=args.nodeNum,
               n_clusters=args.n_clusters, theme=args.theme, layout=args.layout, algorithm=args.algorithm)
    print(f"Copy and paste thins link to a browser to see the visualization {str(abspath('../index.html'))}")

else:
    print(args.selector)

