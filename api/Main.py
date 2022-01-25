import sys
from warnings import warn
from os.path import abspath
from argparse import ArgumentParser, RawTextHelpFormatter

from saving_and_loading import *
from searchStrategies import followersStrategy

handlestring = "Twitter handle (the part in brackets @[foo])"

parser = ArgumentParser(prog="Twitgraph",
                        description="Collect:\tCollect data from twitter api.\n"
                                    "Get Keys:\tList and/or delete keys from database.\n"
                                    "Show:\t\tPrint contents of one or more handles.\n"
                                    "Visualize:\tVisualize graph.",
                        formatter_class=RawTextHelpFormatter)
subParsers = parser.add_subparsers(dest="selector")

# Search Data
dataParse = subParsers.add_parser("collect", description="Collect data from twitter api")
dataParse.add_argument("-H", "--handle", dest="screen_name", metavar="Handle", required=True, help=handlestring)
dataParse.add_argument("-n", "--nIterations", dest="enum", metavar="Enumeration", default=1, type=int,
                       help="Number of times the api is called (each takes 15 minutes)")
dataParse.add_argument("-q", "--quiet", dest="quiet", action="store_true", help="Displays less statuses")

# Get/Delete keys
keyParser = subParsers.add_parser("getkeys", description="List and/or delete keys from database")
# keyParser.add_argument("-H", "--handle", dest="screen_names", action="append", nargs="+", metavar="Handle",
#                        help=handlestring)
keyParser.add_argument("-d", "--delete", dest="deleteSome", action="store_true",
                       help="Delete all information of a handle or more")

# Show data
showParse = subParsers.add_parser("show", description="Print contents of one or more handles")
showParse.add_argument("-H", "--handle", dest="screen_names", nargs="+", metavar="Handle",
                       help=handlestring, required=True)
showParse.add_argument("-p", "--peek", dest="peek", action="store_true",
                       help="Print the first 10 users in selected handles")

# Create visual
visualParse = subParsers.add_parser("visualize", description="Visualize graph")
visualParse.add_argument("-H", "--handle", dest="screen_name", metavar="Handle", required=True, help=handlestring)
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
    if args.screen_name not in getShelveKeys():
        if input(f"Handle name {args.screen_name} not in database. Do you want to create it? (y/n) ") != "y":
            print("Quitting")
            sys.exit()
        else:
            newName = True

    # Check API
    print("\nMake sure to have your:\n\tapiKey,\n\tapiSecretKey,\n\taccessToken,\n\taccessTokenSecret\nin a "
         "file named twitterkeys.txt on the same level as this file")

    api, graph = loadAll(args.screen_name, newName)
    followersStrategy(screenName=args.screen_name, graph=graph, api=api, nIterations=args.enum, quiet=args.quiet)

elif args.selector == "getkeys":
    for screenName in getShelveKeys():
        if args.deleteSome:
            if input(f"Do you want to delete {screenName}? (y/n) ") == "y":
                deleteShelveKey(screenName)
        else:
            print(f"\t{screenName}")

elif args.selector == "show":
    if len(args.screen_names) > 1:
        if input(
                "You chose more than one handle to show, this will load all handles from the database for a few seconds, "
                "is that ok? (y/n) ") != "y":
            print("quitting")
            sys.exit()

    for screenName in args.screen_names:
        graph = loadGraph(screenName)
        graph.display(num=10 if args.peek else 0, depth=5)

elif args.selector == "visualize":
    saveShelve(args.screen_name, loadGraph(args.screen_name), dump=True, onlyDone=True, numNodes=args.nodeNum,
               n_clusters=args.n_clusters, theme=args.theme, layout=args.layout, algorithm=args.algorithm)
    print(f"Copy and paste thins link to a browser to see the visualization {str(abspath('../index.html'))}")

else:
    print(args.selector)

