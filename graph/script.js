// Import Packages
let sigma = require("sigma")
// ### Initialize data JSON
data.nodes = Object.fromEntries(Object.entries(data['nodes']));

let counter, counter2, current, id, node, index, temp, name,
 element, elements, angle,
 clusters, cluster, clusterSizes, fullSize, sizeLeft,
 box, infoBox, keepDetails, nodegraph, lights, scalingMode;

// ### Initialize variables


// # Initialize constants
const nodeKeys = Object.keys(data.nodes);
const info = document.getElementById("info");
const tau = 2 * Math.PI;
const maxCluster = Math.max.apply(Math, Object.values(data.variables.clusterSizes))

// # Load config settings
const layout = config.layout;
const constants = config.constants;
let coloring = config.coloring;


let c = coloring.clusterActive;
if (c.includes("a")) // rgba(a, b, c, d) or rgb(a, b, c)
	coloring.clusterActive = c.slice(5, -1).split(",").map(x => parseFloat(x));
else
	coloring.clusterActive = c.slice(4, -1).split(",").map(x => parseFloat(x));

// # Initialize styles
infoBox = info.firstElementChild
infoBox.style["background-color"]= coloring.box;
infoBox.style["color"]= coloring.boxText;

document.getElementById("container").style["background-color"]= coloring.background;
document.getElementById("miniMap").style["background-color"]= coloring.miniMapBackground;
let buttons = document.getElementsByClassName("buttons");
for(let button in buttons){
	if (button == "length")
		break
	buttons[button].style.background = coloring["button-background"];
	buttons[button].style.color = coloring["button-color"];
}


// ### Graph components


// # Graph arrays
let g = {
    nodes: [],
    edges: []
};


try{
    // clusterPoints = eval(`${config.layout}()`)
    // clusterPoints = laidout_data
    errorme
}
catch(ReferenceError){
    clusterPoints = forceDirectedLayout()
}


const addNode = function(cluster){
    // Given a cluster id, adds it to g.nodes
    // Note: cluster should be in clusterPoints 
    if(g.nodes.some(x => x.id == "c" + cluster )) // check if exists already
        return;

    let name = "";
    let hidden = false;
    let size = 0.0001;
    let color = coloring.background;

    if(data.variables.clusters.some(x => cluster == x)){
        loop1: // Get name from cluster's children, assign as label
        for(node in data.nodes)
            if(data.nodes[node].cluster == cluster){
                name = data.nodes[node].json.name;
                break loop1;
            }
        hidden = false;
        color = idColor(cluster, coloring.clusterActive)
        size = data.variables.clusterSizes[cluster]/maxCluster * constants.clusterSize;
    }

    if(cluster == "-99"){
        name = "Protected";
        size = 1
        color = coloring.protectedCluster
    }

    g.nodes.push({
        id: "c" + cluster,
        label: name,
        x: clusterPoints[cluster].x,
        y: clusterPoints[cluster].y,
        size: size,
        color: color, 
        hidden: hidden
    });    
}


// Add all clusters to g.nodes
addNode("");
for(key in data.variables.clusters){
    cluster = data.variables.clusters[key];

    loopWhile:
    while(true){
        addNode(cluster);
        cluster = cluster.slice(0, cluster.length-1);
        if(cluster == "")
            break loopWhile
    }
}

// Add cluster edges

// If clusterEdges defined take edges from there, otherwise predict edges from cluster names
if(data.variables.clusterEdges.length > 0)
    for(i in data.variables.clusterEdges)
        for(j in data.variables.clusterEdges[i]){
            // console.log(i, data.variables.clusterEdges[i][j])
            if(data.variables.clusterEdges[i][j])
                g.edges.push({
                    id: "e_c" + data.variables.clusters[i] + "_c" + data.variables.clusters[j],
                    source: "c" + data.variables.clusters[i],
                    target: "c" + data.variables.clusters[j],
                    size: constants.edgeSize * 4,
                    color: coloring.clusterEdge,
                    type: config.edges.clusterEdges
                })
            }
else {
    const getClusterEdge = function(cluster) {
        while(true){
            cluster = cluster.slice(0, cluster.length-1);;
            if (cluster == "")   return null
            if (g.nodes.some(x => x.id == "c" + cluster))
                return cluster
        }
    }

    // Add edge from each length 1 cluster (e.g. c1, c2, c3) to origin cluster c
    data.variables.clusters.forEach((c) => {
        if(c.length == 1)
            g.edges.push({
                id: "e_c_c" + c,
                source: "c",
                target: "c" + c,
                size: constants.edgeSize * 4,
                color: coloring.clusterEdge,
                type: config.edges.clusterEdges
            })
    })    
    // console.log(g.edges)
    check = []

    for(key in data.variables.clusters){
        cluster = data.variables.clusters[key];
        
        whileLoop:
        while(true){
            const prev = getClusterEdge(cluster);

            if (prev != null){
                if(!g.edges.some(x => x.id === "e_c" + cluster + "_c" + prev))
                    g.edges.push({
                        id: "e_c" + cluster + "_c" + prev,
                        source: "c" + cluster,
                        target: "c" + prev,
                        size: constants.edgeSize * 4,
                        color: idColor("c" + cluster, coloring.clusterActive, a=1/("c" + cluster).length),
                        type: config.edges.clusterEdges
                    })
            }
            else {
                if(!g.edges.some(x => x.id === "e_c" + cluster + "_c"))
                    g.edges.push({
                        id: "e_c" + cluster + "_c",
                        source: "c" + cluster,
                        target: "c",
                        size: constants.edgeSize * 4,
                        color: idColor("c" + cluster, coloring.clusterActive, a=1/("c" + cluster).length),
                        type: config.edges.clusterEdges
                    })
            }

            cluster = cluster.slice(0, cluster.length-1);
            while(check.some(x => x == cluster))
                cluster = cluster.slice(0, cluster.length-1);
            if(cluster === "")
                break whileLoop;
            check.push(cluster)
        }
    }
}

// # Add nodes
// We determine the x, y position of nodes by uniformly spacing them around the cluster point associated 
//  with the cluster they're in
// see https://en.wikipedia.org/wiki/Polar_coordinate_system

// Copy cluster sizes and use as a reference to place evenly spaces nodes in a circle around every cluster where
// data.variables.clusterSizes is unchanged and stores sizes, and clusterSizes is changed and stores nodes left in cluster
clusterSizes = Object.assign({}, data.variables.clusterSizes)
for (node in data.nodes){
    current = data.nodes[node];

    fullSize = data.variables.clusterSizes[current.cluster];
    sizeLeft = clusterSizes[current.cluster];
    angle = tau/fullSize * (fullSize - sizeLeft);

    g.nodes.push({
        id: current.json.id_str,
        label: current.json.name,
        x: clusterPoints[current.cluster].x + Math.cos(angle) *
        	(data.variables.clusterSizes[current.cluster] / maxCluster * constants.nodeStretch),

        y: clusterPoints[current.cluster].y + Math.sin(angle) *
        	(data.variables.clusterSizes[current.cluster] / maxCluster * constants.nodeStretch),

        size: data.variables.clusterSizes[current.cluster]/maxCluster * 
                                constants.clusterSize * constants.nodeSize / 5,
        color: coloring.active,
        hidden: true
    });
    clusterSizes[current.cluster] += -1;
}

// # Add edges

counter = 0;
for (node in data.nodes) {
    current = data.nodes[node];

    for (index in current.edges) {
        id = String(current.edges[index]) //Id of target

        if (nodeKeys.includes(id)) { 
            g.edges.push({
                id: "e_" + current.json.id_str + "_" + counter,
                source: current.json.id_str,
                target: id,
                size: constants.edgeSize,
                color: coloring.edge,
                type: config.edges.nodeEdges
            });
        counter++;
        }
    }
}

// ### Functions


// # Function variables

let image, header, description;
let stack = []; // How many profile details are displayed
let result;

// # Functions
function displayDetails(id, append=false){
    /* Displays the details of the node given */

    if (id.includes("c")) // If clicked node is a cluster
        if(!data.variables.clusters.includes(id.slice(1))) // if cluster doesn't have nodes then ignore it
            return;
        else
            result = clusterDetails(id); 
    else
        result = profileDetails(data.nodes[id]);

    if (result == -1)
        return;

	if(stack.length == constants.maxProfiles && append)
		return; // if at max and trying to append

    addbox(append, result);
}

function addbox(append, result){
    if (append){
        element = document.createElement("div.infoBox");
        element.innerHTML = result;
        infoBox.appendChild(element)
    }
    else
        infoBox.innerHTML = result;
}

function profileDetails(node){
    if (stack.includes(node.json.id_str))
        return -1; // if node already in box
    else
        stack.push(node.json.id_str)

    profileImg = `<img style="position: absolute" src=${node.json.profile_image_url}>`;

    header =    `<h3 style="text-align:center; background-color: rgb(20, 20, 20, 0.1);">
                <a href=https://twitter.com/${node.json.screen_name}>${node.json.name}</a><br>
                ${node.json.friends_count} Following&emsp;
                ${node.json.followers_count} Followers<br><hr style="width:50%;">`;

    description =       `${node.json.description}<br><hr style="width:50%;">
                        Tweet count: ${node.json.statuses_count}&emsp;
                        Favorite count: ${node.json.favourites_count}<br>
                        ${ (node.json.url ? `<a href=${node.json.url}>Link</a>&emsp;` : "")}
                        ${ (node.json.location ? `Location: ${node.json.location}` : "")}<br></h3>`;
    //<h5 style="text-align:center; background-color: rgb(20, 20, 20, 0.1);">${node.json.status.text}</h5>

    return profileImg + header + description;
}

function clusterDetails(cluster){
    let nodesNum = 0;
    let tweetCount = 0;
    let favCount = 0;
    let imgs = "";
    let names = [];

    for(node in data.nodes){
        node = data.nodes[node]
        if(cluster.slice(1) != node.cluster)
            continue;

        nodesNum += 1;
        tweetCount += node.json.statuses_count;
        favCount += node.json.favourites_count;
        imgs += ` <img style="position: relative; " src= ${node.json.profile_image_url} > `;
        names.push("<br>" + node.json.name);
        
    }
    header = `<h3 style="text-align:center;  text-shadow: 2px 2px ${coloring.boxTextShadow};"> ${names[0]}'s Cluster<br>
              Number Of nodes: ${nodesNum}&emsp; Tweet Count: ${tweetCount}&emsp; Favorite Count: ${favCount}&emsp; ID: ${cluster}
              <br></h3><hr style="width:50%;">
              <h3 style="text-align:center; letter-spacing: 1px;">${names}</h3><hr style="width:50%;">`;

    description = imgs;
    return '<div style="background-color: rgb(20, 20, 20, 0.1); text-align:center;">' + header + imgs + "</div>"
}

function clearDetails(){
    /* Clears the details box */
	for (var i = info.children.length - 1; i > 0; i--) 
		info.removeChild(info.children[i]);
	
	infoBox = info.firstElementChild;
	infoBox.innerHTML= "";

	stack = [];
}

function colorNodes(color, active=false){
    /* Returns all nodes to their original color */
	for(node in nodes){
        if (nodes[node].id.includes("c"))  
            continue;

		nodes[node].active = active;
		nodes[node].color = color;
	}
	s.render();
}

function markNodes(id, onColor, offColor, ctrlKey){
    /* Colors all nodes depending on many factors 
    TODO: Change this to be more efficient*/
	for(node in nodes){

        if (nodes[node].id.includes("c"))  
            continue;

		if (nodes[node].active && ctrlKey || id == nodes[node].id){
			nodes[node].color = onColor;
		}
		else{
			nodes[node].active = false;
			nodes[node].color = offColor;
			// TODO: size
		}
	}
	s.render();
}

function colorEdges(color){
    /* Returns all edges to their original color, and size*/
	for(let edge of edges){
        if (edge.id.includes("c"))
            edge.color = idColor(edge.source, coloring.clusterActive, a=1/edge.source.length);
        else{
    		edge.color = color;
    		edge.size = 1;
        }
	}
	s.refresh();
}

function markEdges(id, onColor, offColor, ctrlKey=false){
    /* Colors all edges that connect to node with onColor and other thing
    TODO: remove the else in func and run colorEdges rather than it*/
	for(let edge in edges){

        if(edges[edge].id.includes("c")){
            edges[edge].color = coloring.clusterInactiveEdge;
            continue;
        }

        else if(edges[edge].id.includes(id)){
            edges[edge].color = onColor;
            edges[edge].active = true;
            edges[edge].size = constants.edgeSize * 4;
        }

        else if (ctrlKey && edges[edge].active){} // Skip when user holds ctrlKey and edge already active

        else {
        	edges[edge].color = offColor;
        	edges[edge].size = constants.edgeSize;
        	
        }
    }
    s.refresh();
}

function toggleVisibility(cluster){
    // Hides/Shows all nodes associated with this cluster
    for(let key in nodes){
        id = nodes[key].id;
        if (id.includes("c"))
            continue;
        if (cluster == "c" + data.nodes[id].cluster)
            nodes[key].hidden = !nodes[key].hidden;
    }
    s.refresh()
}

document.getElementById("visibility").onclick = function() {
    b = nodes[nodes.length-1].hidden;
    for(let key in nodes){
        if(nodes[key].id.includes("c"))
            continue;
        nodes[key].hidden = !b;
    }
    s.refresh();
}

document.getElementById("graphInfo").onclick = function() {
    string = `<h1 style="text-align:left;  text-shadow: 2px 2px ${coloring.boxTextShadow};">
         &emsp;Controls:</h1>

         <h2 style="text-align:center;">         
         &emsp;Hold 'Ctrl' key and click node:&emsp;View node info without
         clearing the info box<br><br>

         Hold 'Shift' key and click cluster:&emsp;Stop toggling visibility.
         </h2>

         <h1 style="text-align:left; text-shadow: 2px 2px ${coloring.boxTextShadow};">
         &emsp;Numbers:</h1>
         <h2 style="text-align:center;">
		 Number of nodes:&emsp;${data.variables.nodeNum}<br>
		 Number of clusters:&emsp;${data.variables.numClusters}
		 </h2>

         <h1 style="text-align:left; text-shadow: 2px 2px ${coloring.boxTextShadow};">
         &emsp;References</h1>
         <h3 style="text-align:left;">
         von Luxburg, U. A tutorial on spectral clustering. Stat Comput 17, 395-416 (2007). https://doi.org/10.1007/s11222-007-9033-z
         <br><br>
         McGuffin, M.J. (2012). Simple algorithms for network visualization: A tutorial. Tsinghua Science & Technology, 17, 383-398.
         </h3>
         `
    addbox(false, string);
    keepDetails = true;
}

document.getElementById("about").onclick = function() {
    str = `<h2 style="text-align:center;  text-shadow: 2px 2px ${coloring.boxTextShadow};">Twitgraph</h2>
         <h3 style="text-align:center;  text-shadow: 2px 2px ${coloring.boxTextShadow};">
         <br>A Twitter Network Interactive Visualizer</h3><br>

         <h3 style="text-align:center;">
         This tool utilizes twitter's api to get data about the network of communities
         surrounding any particular twitter account and draws an interactive graph based on it.<br><br>

         The api is accessed via python's <a href="https://www.tweepy.org/">Tweepy</a>,
         <a href="http://sigmajs.org/">Sigmajs</a> handles drawing nodes and edges unto a canvas<br>

         Behind the scenes the data gotten from the API is clustered (grouped) using 
         <a href="https://en.wikipedia.org/wiki/Spectral_clustering">Spectral Clustering</a>.
         Where each cluster indicates a local group of conneced nodes (people).
         Each cluster is a result of partitioning of a bigger cluster.<br><br>

         The intended effect of the clustering is to reveal unseeable patterns
         in the data and present them in an aesthetically pleasing way.</h3>

         <h4 style="font-family: monospace;">Author: <a href="https://github.com/Hawzen">Hawzen</a><h4>
         `
    addbox(false, str);
    keepDetails = true;
}


// ### Sigmajs
let s = new sigma({
    graph: g,
    settings: {
        minNodeSize: constants.minNodeSize,
        maxNodeSize: constants.maxNodeSize,
        minEdgeSize: constants.minEdgeSize,
        maxEdgeSize: constants.maxEdgeSize,

        zoomMin: 0.001,
        zoomMax: 5,
        zoomingRatio: 1.3,

        verbose: true,
        scalingMode: "inside"
    },
});

s.addCamera("main");
s.addCamera("miniCam");

s.addRenderer({
    container: document.getElementById('container'),
    type: 'canvas',
    camera: "main",
    settings: {
        doubleClickEnabled: false,

        edgeHoverSizeRatio: 2,
        hideEdgesOnMove: true,

        labelThreshold: 10,
        defaultLabelColor: coloring.labelColor,

        font: "monospace",
    }
});

s.addRenderer({
    container: document.getElementById("miniMap"),
    type: "canvas",
    camera: "miniCam",
    settings: {
        drawEdges: false,
        drawLabels: false,
        mouseEnabled: false
    }
});

s.refresh();

// # Graph variables
// Modify these to modify graph
const edges = s.graph.edges();
const nodes = s.graph.nodes();
for(node in nodes)
	nodes[node].active = false;


// ### Events


// # Events variables
lights = true; // When this is off, clickNode shouldn't modify edges
keepDetails = false; // When this is on, outNode shouldn't modify DIV details


// # Events
s.bind("overNode", function(e){
    /* Displays details when cursor over node */
	nodegraph = e.data.node; // Node from sigmajs's pov, use to modify behavior
    current = data.nodes[nodegraph.id]; // Node from data pov, use to get data
	nodegraph.active = true;

	if(!keepDetails)
    	displayDetails(nodegraph.id);
})

s.bind("outNode", function(e){
    /* Remove details put by event overNode when cursor out of node */
	if(!keepDetails)
		clearDetails();
})

s.bind('clickNode', function(e) {
    /* Display details when cursor clicks node
    Note: the difference between this event and overNode event is that the former
     isn't nullified by outNode event, but the latter removes details when outNode activates*/
	nodegraph = e.data.node;  
    current = data.nodes[nodegraph.id];  

	nodegraph.active = true;
	keepDetails = true;

    try{
        console.log(current.json.screen_name);
    }
    catch(TypeError){}
    
    if (nodegraph.id.includes("c") && !e.data.captor.shiftKey)
        toggleVisibility(nodegraph.id);
    
    if (lights) {
        displayDetails(nodegraph.id, e.data.captor.ctrlKey);
    }
});

s.bind("doubleClickNode", function(e) {
    /* Displays details in the same way clickNode behaves, and changes the colors to a lights-out mode */
	nodegraph = e.data.node;  

	nodegraph.active = true;
	lights = false

    displayDetails(nodegraph.id, e.data.captor.ctrlKey);
    markEdges(nodegraph.id, coloring.activeEdge, coloring.inactiveEdge, e.data.captor.ctrlKey);
	markNodes(nodegraph.id, coloring.active, coloring.inactive, e.data.captor.ctrlKey);

})

s.bind('doubleClickStage', function(e) {
    /* Removes details when user double clicks anything other than nodes */
	keepDetails = false;
	lights = true;

    colorEdges(coloring.edge);
    colorNodes(coloring.active);
	clearDetails()
});


// ### Extras

let inputBox = document.getElementById('search-input');
inputBox.addEventListener("change", searchChange);

function searchChange(e) {
    var value = e.target.value;

    s.graph.nodes().forEach(function (n) {
      if (n.label == value) {
        console.log(n.label)
        n.color = "#ffff00"
        n.colorEdges = "#ffff00"
        n.size = 1000000000
      }
    });
  }

// Get color function
function idColor(cluster, c, a=undefined){
    let sum = getNumDigits(cluster);
    if(a === undefined)
        return `rgba(${c[0]}, ${c[1] * sum / 10}, ${c[2] * sum / 3}, ${(c.length > 3) ? c[3] : 1})`
    else
        return `rgba(${c[0]}, ${c[1] * sum / 10}, ${c[2] * sum / 3}, ${a})`
}

function getNumDigits(num){
    let str = String(num);
    let sum = 0;
    while(str){
        sum += 1;
        str = str.slice(0, str.length-1);
    }
    return sum;
}

function checknode(nodeId){ // Checking, not used 
    return nodes.some(x => Array(data.nodes[nodeId].edges).includes(x.id));
}

// Execute at start
colorEdges(coloring.edge); // Not sure why, but some colors start wrongly, this sets it up correctly