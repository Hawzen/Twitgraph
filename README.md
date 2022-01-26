# Twitgraph
Twitgraph is a library that generates an interactive network of social clusters related to any twitter profile or a twitter qurey.   

![mg](https://i.imgur.com/VGXPtQd_d.webp?maxwidth=760&fidelity=grand)


### Usage

    usage: Twitgraph [-h] {collect,keys,stats,visualize} ...

    collect:        Collect data from twitter api.
    keys:   List and/or delete keys from database.
    stats:          Print statistics of handles.
    visualize:      Visualize graph.

    positional arguments:
      {collect,keys,stats,visualize}

    optional arguments:
      -h, --help            show this help message and exit



    usage: Twitgraph collect [-h] -k DBKey [-H Handles to search from [Handles to search from ...]]
                             [-q QUERIES [QUERIES ...]] [-m [maxTweets ...]] [-n nIterations]

    Collect data from twitter api

    optional arguments:
      -h, --help            show this help message and exit
      -k DBKey, --key DBKey
                            Name of database (using a name for the first time will create one, otherwise
                            will use the existing DB)
      -H Handles to search from [Handles to search from ...], --handles Handles to search from [Handles to search from ...]
                            Twitter handle(s) to begin searching from (the part in brackets @[foo])
      -q QUERIES [QUERIES ...], --queries QUERIES [QUERIES ...]
                            queries to collect users from
      -m [maxTweets ...], --maxTweetsPerQurey [maxTweets ...]
                            Maximum number of tweets to collect per qurey (e.g. '-m 1000 300 500').
                            Defaults to 1000
      -n nIterations, --nIterations nIterations
                            Number of times the api is called (each takes 15 minutes)



    usage: Twitgraph keys [-h] [-k DBKey] [-d]

    List and/or delete keys from database

    optional arguments:
      -h, --help            show this help message and exit
      -k DBKey, --key DBKey
                            Name of database (using a name for the first time will create one, otherwise
                            will use the existing DB)
      -d, --delete          Delete all information of a handle or more



    usage: Twitgraph stats [-h] [-k DBKey [DBKey ...]] [-p]

    Print contents of one or more handles

    optional arguments:
      -h, --help            show this help message and exit
      -k DBKey [DBKey ...], --key DBKey [DBKey ...]
                            Name of database (using a name for the first time will create one, otherwise
                            will use the existing DB)
      -p, --peek            Print the first 10 users in selected handles



    usage: Twitgraph visualize [-h] -k DBKey [-n Node Number] [-p Partition Number] [-t Theme]
                               [-l Layout] [-a algorithm]

    Visualize graph

    optional arguments:
      -h, --help            show this help message and exit
      -k DBKey, --key DBKey
                            Name of database (using a name for the first time will create one, otherwise
                            will use the existing DB)
      -n Node Number, --nodenum Node Number
                            Number of nodes visualized (default for all nodes)
      -p Partition Number, --n_clusters Partition Number
                            Number of times data is partitioned (default for 0.1 of node number)
      -t Theme, --theme Theme
                            Visual style of graph
      -l Layout, --layout Layout
                            Layout of (x, y) positions of nodes in the graph
      -a algorithm, --algorithm algorithm
                            Choice of algorithm (spectral_clustering, HDBSCAN)
                            
                            
### Adding your own theme
You can specify colors and constants of the graph visualization by editing the data/configurations.json, duplicate and existing theme and edit the values that you wish to edit, you can leave and out any object you do not wish to edit and it'll replaced by it's default config, as an example you duplicate the 'colors' object and leave out the 'constants' and 'layout' objects.

### Adding your own layout algorithm
You can write an algorithm to compute the (x, y) coordinates of each cluster by writing a javascript function in graph/layoutAlgorithm.js that returns an object which relate each cluster ID -> (x, y) coordinate (Note: you will need to fimilirize yourself with the code structure in script.js first). After that you should choose the add name of the function you created to 'layouts' in the file data/configurations.json. Running Main.py visualize, choose '--layout' as the name of your function.

