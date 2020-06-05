// ### Initialize data JSON
data.nodes = Object.fromEntries(Object.entries(data['nodes']));
data.nodes[data.origin.json.id_str] = data.origin;

let counter, counter2, current, id, node, index, origin, temp, name,
 element, elements, originSettings, angle,
clusters, cluster, clusterPoints, clusterSizes, fullSize, sizeLeft,
 box, infoBox, keepDetails, nodegraph, lights, scalingMode;

// ### Initialize variables


// # Initialize constants
const nodeKeys = Object.keys(data.nodes);
const info = document.getElementById("info");
const tau = 2*3.1415;
const circleRule = tau/data.variables.numClusters;
if(nodeKeys.length > 100)
    scalingMode = "outside";
else
    scalingMode = "inside";


const constants = {
    clusterStretch: 0.8,
    ellipseStretch: {x: 1, y: 1},
    nodeStretch: 0.06,

    _edgeSize: 1,
    _clusterSize: 1,
    _nodeSize: 2,

    // Maximum num of nodes in all cluster
    maxCluster: Math.max.apply(Math, Object.values(data.variables.clusterSizes)), 
    minNodeSize: 3,
    maxNodeSize: 10,
    minEdgeSize: 0.1,
    maxEdgeSize: 10,
    maxProfiles: 5,
};

// # Initialize colors
let coloring = {
    off: "#000000",
    inactive: "rgba(135, 121, 82, 0.2)",
    active: "rgba(135, 121, 82, 1)",

    edgeColor: "rgba(135, 121, 82, 0.05)",
    inactiveEdgeColor: "rgba(135, 121, 82, 0.03)",

    origin: "#FFD700",
    red: "#d7385e",

    clusterActive: [230, 121, 82], //"rgba(230, 121, 82, 1)"
    clusterInactive: "rgba(135, 121, 82, 0.2)",
    clusterEdge: "rgba(200, 121, 100, 1)",
    clusterInactiveEdge: "rgba(200, 121, 100, 0.3)",
    protectedCluster: "rgb(250, 40, 200)",

    background: "rgb(252, 241, 212)",
    tBackground: "rgb(252, 230, 200, 0.3)",
    box: "rgba(145, 132, 96, 0.2)",
    boxText: "rgba(0, 0, 0, 0.95)"
}
document.getElementById("container").style["background-color"]= coloring.background;
document.getElementById("miniMap").style["background-color"]= coloring.tBackground;

// # Initialize infoBox
infoBox = info.firstElementChild
infoBox.style["background-color"]= coloring.box;
infoBox.style["color"]= coloring.boxText;


// ### Graph components


// # Graph arrays
let g = {
    nodes: [],
    edges: []
};


// Delete later
g.nodes.push({
    id: 213,
    name: "origin",
    x: 0,
    y: 0,
    size:2,
    color: "black"
})

g.nodes.push({
    id: 123,
    name: "right",
    x: 1,
    y: 0,
    size: 2,
    color: "cyan"
})

g.nodes.push({
    id: 321,
    name: "up",
    x: 0,
    y: 1,
    size: 2,
    color: "grey"
})

// # Add cluster nodes 
clusterPoints = {"": {x: 0, y: 0}, "1": {x: 0, y: 10}, "2": {x: 0, y: -10}};
counter = 0;

const point = function(angle, dependentPoint={x: 0, y: 0}, stretch, up) {
    // Returns an object containing x, y position of a cluster given
    // the angle property and parent node's x, y object
    // if parent node's x, y object is not specified it'll be ignored
    return {x: dependentPoint.x +  2 + 2 * Math.random(),
            y: dependentPoint.y +  stretch * (up ? -1 : 1)};
};

const addClusterPoint = function (cluster, angle) {
    // Given a cluster id and its angle 
    // This function adds the cluster to clusterPoints object specifying its x, y position
    // As well as every ancestor of that cluster
    const parent = cluster.slice(0, cluster.length-1); // Get parent cluster
    
    if(cluster in clusterPoints){}

    else if (parent in clusterPoints) // if parent is already in clusterPoints
        if(parent === "")
            clusterPoints[cluster] = point(angle, clusterPoints[parent], 1, (cluster == 1 ? true : false));    
        else
            // Create object relying on parent position
            clusterPoints[cluster] = point(angle, clusterPoints[parent], 10/(getNumDigits(cluster) ** 1.3),
                        (parseInt(cluster.slice(cluster.length-1)) == 1 ? true : false)); 

    else{
        // When parent is not in clusterPoints and cluster isnt single digit
        addClusterPoint(parent, angle); // Recursively apply function to parent

        // After that create cluster point relying on parent node
        clusterPoints[cluster] = point(angle, clusterPoints[parent], 10/(getNumDigits(cluster) ** 1.3),
                        (parseInt(cluster.slice(cluster.length-1)) == 1 ? true : false)); 
    }
};

const addNode = function(cluster){
    // Given a cluster id, adds it to g.nodes
    // Note: cluster should be in clusterPoints 
    if(g.nodes.some(x => x.id == "c" + cluster )) // check if exists already
        return;

    let name = "";
    let hidden = false;
    let size = 0.001;
    let color = clusterColor(cluster);

    if(data.variables.clusters.some(x => cluster == x)){
        loop1: // Get name from cluster's children, assign as label
        for(node in data.nodes)
            if(data.nodes[node].cluster == cluster){
                name = data.nodes[node].json.name;
                break loop1;
            }
        hidden = false;
        size = data.variables.clusterSizes[cluster]/constants.maxCluster * constants._clusterSize;
    }

    if(cluster == "5"){
        name = "Outlier";
        size = 1;
    }
    if(cluster == "4"){
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


// Add all clusters to clusterPoints
for(key in data.variables.clusters){
    cluster = data.variables.clusters[key]

    angle = counter * circleRule;
    counter += 1;

    loopWhile:
    while(true){
        addClusterPoint(cluster, angle);
        cluster = cluster.slice(0, cluster.length-1);
        if(cluster === "")
            break loopWhile;
    }
}


// Add all clusters to g.nodes
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

const getClusterEdge = function(cluster) {
    while(true){
        cluster = cluster.slice(0, cluster.length-1);;
        if (cluster == "")   return null
        if (g.nodes.some(x => x.id == "c" + cluster))
            return cluster
    }
}

let check = [];
for(key in data.variables.clusters){
    cluster = data.variables.clusters[key];
    
    whileLoop:
    while(true){
        const prev = getClusterEdge(cluster);

        if (prev != null){
            g.edges.push({
                id: "e_c" + cluster + "_c" + prev,
                source: "c" + cluster,
                target: "c" + prev,
                size: constants._edgeSize * 4,
                color: coloring.clusterEdge,
                type: "dashed"
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


// # Add nodes
// We determine the x, y position of nodes by randomly spacing them around the cluster point associated 
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
        x: clusterPoints[current.cluster].x + Math.sin(angle) * constants.nodeStretch,
        y: clusterPoints[current.cluster].y + Math.cos(angle) * constants.nodeStretch,
        size: data.variables.clusterSizes[current.cluster]/constants.maxCluster * 
                                constants._clusterSize * constants._nodeSize / 5,
        color: coloring.active,
    });
    clusterSizes[current.cluster] += -1
}


// # Add origin Node

origin = data.origin;
fullSize = data.variables.clusterSizes[origin.cluster];
sizeLeft = clusterSizes[origin.cluster];
angle = tau/fullSize * (fullSize - sizeLeft-1);
originSettings = {
    id: origin.json.id_str,
    label: origin.json.name,
    x: clusterPoints[origin.cluster].x + Math.sin(angle) * constants.nodeStretch,
    y: clusterPoints[origin.cluster].y + Math.cos(angle) * constants.nodeStretch,
    size: data.variables.clusterSizes[current.cluster]/constants.maxCluster * 
                            constants._clusterSize * constants._nodeSize / 5,
    color: coloring.origin
    }

index = g.nodes.findIndex(node => node.id == origin.json.id_str);
g.nodes[index] = originSettings;


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
                size: constants._edgeSize,
                color: coloring.edgeColor,
                type: "cruve"
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
        if(!data.variables.clusters.includes(id.slice(1))) // if cluster doesnt have nodes then ignore it
            return;
        else
            result = clusterDetails(id); 
    else
        result = profileDetails(data.nodes[id]);

    if (result == -1)
        return;

    if(stack.length == constants.maxProfiles && append)
        return; // if at max and trying to append

    if (append){
        element = document.createElement("div.infoBox");
        element.innerHTML = result;
        //element.style = infoBox.style;
        

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
    header = `<h3 style="text-align:center;  text-shadow: 2px 2px white;"> ${names[0]}'s Cluster<br>
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
        if (nodes[node].id == origin.json.id_str) // if origin, then origin color
            nodes[node].color = coloring.origin;
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
            if (nodes[node].id == origin.json.id_str) // if origin, then origin color
                nodes[node].color = coloring.origin;
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
    for(let edge in edges){
        if (edges[edge].id.includes("c"))
            edges[edge].color = coloring.clusterEdge;
        else{
            edges[edge].color = color;
            edges[edge].size = 1;
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
            edges[edge].size = constants._edgeSize * 4;
        }

        else if (ctrlKey && edges[edge].active){} // Skip when user holds ctrlKey and edge already active

        else {
            edges[edge].color = offColor;
            edges[edge].active = false; // Why is this not needed? TODO DELETE it
            edges[edge].size = constants._edgeSize;
            
        }
    }
    s.refresh();
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
        zoomingRatio: 3,

        verbose: true,
        scalingMode: scalingMode
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

        labelThreshold: 7,
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
lights = true; // When this is off, clickNode shouldnt modify edges
keepDetails = false; // When this is on, outNode shouldnt modify DIV details


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

    
    if (lights) {
        displayDetails(nodegraph.id, e.data.captor.ctrlKey);
        //markEdges(current, coloring.red, coloring.inactiveEdgeColor, e.data.captor.ctrlKey);
    }
});

s.bind("doubleClickNode", function(e) {
    /* Displays details in the same way clickNode behaves, and changes the colors to a lights-out mode */
    nodegraph = e.data.node;  

    nodegraph.active = true;
    lights = false

    displayDetails(nodegraph.id, e.data.captor.ctrlKey);
    markEdges(nodegraph.id, coloring.red, coloring.inactiveEdgeColor, e.data.captor.ctrlKey);
    markNodes(nodegraph.id, coloring.active, coloring.inactive, e.data.captor.ctrlKey);
})

s.bind('doubleClickStage', function(e) {
    /* Removes details when user double clicks anything other than nodes */
    keepDetails = false;
    lights = true;

    colorEdges(coloring.edgeColor);
    colorNodes(coloring.active);
    clearDetails()
});


// ### Extras

// Get color function
function clusterColor(cluster){
    // Determines color of cluster based on cluster ID 
    let c = coloring.clusterActive;
    let sum = getNumDigits(cluster);
    return `rgba(${c[0]}, ${c[1] * sum / 10}, ${c[2] * sum / 10}, 1)`
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