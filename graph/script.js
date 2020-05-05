// ### Initialize data JSON

data.nodes = Object.fromEntries(Object.entries(data['nodes']));
data.nodes[data.origin.json.id_str] = data.origin;

let counter, current, id, node, index, origin,
 element, elements, originSettings, angle, clusters,
 box, infoBox, keepDetails, nodegraph, lights;

// ### Initialize variables


// # Initialize constants
const nodeKeys = Object.keys(data.nodes);
const numFriends = Object.keys(data.nodes).length - 1; // Dont count origin
const info = document.getElementById("info");
const nodeSize= 8/numFriends;
const circleRule = 2*3.1415/numFriends;
const maxProfiles = 5;


// # Initialize colors
let coloring = {
	off: "#000000",
	inactive: "rgba(135, 121, 82, 0.2)",
	active: "rgba(135, 121, 82, 1)",

	origin: "#DC143C",
	red: "#d7385e",

	background: "rgb(252, 241, 212)",
	box: "rgba(145, 132, 96, 0.2)",
	boxText: "rgba(0, 0, 0, 0.95)"
}
document.getElementById("container").style["background-color"]= coloring.background;


// # Initialize infoBox
infoBox = info.firstElementChild
infoBox.style["background-color"]= coloring.box;
infoBox.style["color"]= coloring.boxText;


// # Initialize origin 
origin = data.origin
originSettings = {
	   id: origin.json.id_str,
	   label: origin.json.name,
	   x: 0,
	   y: 0,
	   size: nodeSize*2,
	   color: coloring.origin
	}


// ### Graph components


// # Graph arrays
var g = {
    nodes: [],
    edges: []
};


// # Add cluster points 
// map each clusterId to natural number starting from 1
// clusterId = [23, 5, 23, 23, 1, 5, 23], clusters = {23: 1, 5: 2, 1: 3}

clusters = {} // {clusterId: cluster} 
counter = 1
for(cluster in data.variables.clusters){
    if (clusters.hasOwnProperty(data.variables.clusters[cluster]))
        continue;
    clusters[data.variables.clusters[cluster]] = counter;
    counter += 1;
}

// Construct origin point for each cluster, where points are uniformly distributed along an ellipse
const ellipseRule = 2*3.1415/(counter - 2);
clusterPoints = {0: {x: 0, y: 0}};
counter = 0;
for(key in clusters){
    angle = ellipseRule * counter;
    clusterPoints[key] = {x: Math.sin(angle), y: Math.cos(angle)};

    counter += 1;
}


// # Add nodes
// We determine the x, y position of nodes by randomly spacing them around the cluster point associated 
//  with the cluster they're in
// see https://en.wikipedia.org/wiki/Polar_coordinate_system

counter = 1;
for (node in data.nodes){
    current = data.nodes[node];
    angle = circleRule * counter;
    counter++;

    g.nodes.push({
        id: current.json.id_str,
        label: current.json.name,
        x: clusterPoints[current.cluster].x - Math.random()/5,
        y: clusterPoints[current.cluster].y - Math.random()/5,
        size: nodeSize,
        color: coloring.active
    });
}


// # Modify origin Node

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
                size: 0.05,
                color: coloring.active,
                type: "cruve",
            });
            counter++;
        }
    }
}

// ### Functions


// # Function variables

let iamge, header, description
let stack = []; // How many profile details are displayed


// # Functions

function getNodeFromId(id){
    return data.nodes.find(node => node.id_str == id);
}

function displayDetails(node, append=false){
    /* Displays the details of the node given */

	if(stack.length == maxProfiles && append) 
		return; // if at max and trying to append

	if (stack.includes(node.json.id_str))
		return; // if node already in box
	else
		stack.push(node.json.id_str)

	image = `<img src=${node.json.profile_image_url}>`;

    header = `<h3 style="text-align:center;">
    		<a href=https://twitter.com/${node.json.screen_name}>${node.json.name}</a><br>
            ${node.json.friends_count} Following&emsp;
            ${node.json.followers_count} Followers<br><hr style="width:50%;">`;

    description = `${node.json.description}<br><hr style="width:50%;">
    					Tweet count: ${node.json.statuses_count}&emsp;
    					Favorite count: ${node.json.favourites_count}<br>
    					<a href=${node.json.url}>Link</a>&emsp;
    					Location: ${node.json.location}</h3>`;

    if (append){
    	element = document.createElement("div.infoBox");
    	element.innerHTML = image + header + description;
    	element.style = infoBox.style;

    	element.style["background-color"]= coloring.box;
    	element.style["color"]= coloring.boxText;

    	infoBox.appendChild(element)
    }
    else
    	infoBox.innerHTML = image + header + description;
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
		nodes[node].active = active;
		nodes[node].color = color;
		if (nodes[node].id == origin.json.id_str) // if origin, then origin color
			nodes[node].color = coloring.origin;
	}
	s.render();
}

function markNodes(node, onColor, offColor, ctrlKey){
    /* Colors all nodes depending on many factors 
    TODO: Change this to be more efficient*/
	for(node in nodes){
		if (nodes[node].active && ctrlKey || nodegraph.id == nodes[node].id){
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
		edges[edge].color = color
		edges[edge]["read_cam0:size"] = 1;
	}
	s.render();
}

function markEdges(node, onColor, offColor, ctrlKey=false){
    /* Colors all edges that connect to node with onColor and other thing
    TODO: remove the else in func and run colorEdges rather than it*/
	for(let edge in edges){	
        if(edges[edge].id.includes(node.json.id_str)){
            edges[edge].color = onColor;
            edges[edge].active = true;
            edges[edge]["read_cam0:size"] = 5;
        }
        else if (ctrlKey && edges[edge].active){} // Skip when user holds ctrlKey and edge already active
        else {
        	edges[edge].color = offColor;
        	// edges[edge].active = false; // Why is this not needed?
        	edges[edge]["read_cam0:size"] = 1;
        	
        }
    }
    s.render();
}

// ### Sigmajs

var s = new sigma({
    graph: g,
    renderer: {
        container: document.getElementById('container'),
        type: 'canvas',
        settings: {
            minNodeSize: 0.1,
            maxNodeSize: 100,
            minEdgeSize: 0.01,
            maxEdgeSize: 1,
            enableEdgeHovering: true,
            edgeHoverSizeRatio: 2,
            doubleClickEnabled: false
        }
    }
});


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
    	displayDetails(current);
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

    displayDetails(current, e.data.captor.ctrlKey);
    if (lights) 
    	markEdges(current, coloring.red, coloring.active, e.data.captor.ctrlKey);
});

s.bind("doubleClickNode", function(e) {
    /* Displays details in the same way clickNode behaves, and changes the colors to a lights-out mode */
	nodegraph = e.data.node;  
    current = data.nodes[nodegraph.id];  
	nodegraph.active = true;
	lights = false

    if (!lights)
    	markEdges(current, coloring.red, coloring.inactive, e.data.captor.ctrlKey);
	markNodes(current, coloring.active, coloring.inactive, e.data.captor.ctrlKey);
})

s.bind('doubleClickStage', function(e) {
    /* Removes details when user double clicks anything other than nodes */
	keepDetails = false;
	lights = true;

    colorEdges(coloring.active);
    colorNodes(coloring.active);
	clearDetails()
});

// overEdge outEdge clickEdge doubleClickEdge rightClickEdge clickStage overNode outNode


// ### Extras

function checknode(nodeId){ // Checking, not used 
    return nodes.some(x => Array(data.nodes[nodeId].edges).includes(x.id));
}