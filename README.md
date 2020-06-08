# Twitgraph
Twitgraph is a library that generates an interactive network of social clusters related to any twitter profile.   

### How it works
It does this following these steps:
  1. Choosing an origin of the network, i.e. the profile we want to examine.
  2. Getting data about the following of that profile.
  3. Repeating step 2 for each profile we get until we reach a satisfactory number of nodes.
  4. Cluster the profiles in a way that groups similar profiles to each other.
  5. Visualize the clusters using a node-edge graph, where clusters have edges to other clusters and profiles have edges to other profiles

The api is called using [Tweepy](https://www.tweepy.org/) and the nodes are clustered using [Spectral Clustering](https://en.wikipedia.org/wiki/Spectral_clustering), visualized using [Sigmajs](http://sigmajs.org/) on the web

The thing to note is that the graph shows connections between **clusters**, so as an example one profile graph of a resturant might be seperated to two clusters, a cluster with containing other companies the resturant follows, and a cluster containing important people like the manager and such. The first cluster might be further clustered into two clusters, say resturants that follow the same resturant chain and another composed of different resturants.

### Usage

    usage: Twitgraph [-h] {collect,getkeys,show,visualize} ...

    Collect:	Collect data from twitter api.
    Get Keys:	List and/or delete keys from database.
    Show:		Print contents of one or more handles.
    Visualize:	Visualize graph.

    positional arguments:
      {collect,getkeys,show,visualize}

    optional arguments:
      -h, --help            show this help message and exit




    usage: Twitgraph collect [-h] -H Handle [-e Enumeration] [-q]

    Collect data from twitter api

    optional arguments:
      -h, --help            show this help message and exit
      -H Handle, --handle Handle
                            Twitter handle (the part in brackets @[foo])
      -e Enumeration, --enumeration Enumeration
                            Number of times the api is called (each takes 15
                            minutes)
      -q, --quiet           Displays less statuses




    usage: Twitgraph getkeys [-h] [-d]

    List and/or delete keys from database

    optional arguments:
      -h, --help    show this help message and exit
      -d, --delete  Delete all information of a\an handle\s




    usage: Twitgraph show [-h] -H Handle [Handle ...] [-p]

    Print contents of one or more handles

    optional arguments:
      -h, --help            show this help message and exit
      -H Handle [Handle ...], --handle Handle [Handle ...]
                            Twitter handle (the part in brackets @[foo])
      -p, --peek            Print the first 10 users in selected handles




    usage: Twitgraph visualize [-h] -H Handle [-n Node Number]
                               [-p Partition Number] [-t Theme] [-l Layout]

    Visualize graph

    optional arguments:
      -h, --help            show this help message and exit
      -H Handle, --handle Handle
                            Twitter handle (the part in brackets @[foo])
      -n Node Number, --nodenum Node Number
                            Number of nodes visualized (default for all nodes)
      -p Partition Number, --partitionnum Partition Number
                            Number of times data is partitioned (default for 0.1
                            of node number)
      -t Theme, --theme Theme
                            Visual style of graph
      -l Layout, --layout Layout
                            Layout of (x, y) positions of nodes in the graph

### Adding your own theme
You can specify colors and constants of the graph visualization by editing the data/configurations.json, duplicate and existing theme and edit the values that you wish to edit, you can leave and out any object you do not wish to edit and it'll replaced by it's default config, as an example you duplicate the 'colors' object and leave out the 'constants' and 'layout' objects.

### Adding your own layout algorithm
You can write an algorithm to compute the (x, y) coordinates of each cluster by writing a javascript function in graph/layoutAlgorithm.js that returns an object which relate each cluster ID -> (x, y) coordinate (Note: you will need to fimilirize yourself with the code structure in script.js first). After that you should choose the add name of the function you created to 'layouts' in the file data/configurations.json. Running Main.py visualize, choose '--layout' as the name of your function.

