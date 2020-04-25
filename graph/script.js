data.nodes = Object.fromEntries(Object.entries(data['nodes']).slice(0, 50));
data.nodes[data.origin.json.id_str] = data.origin;

let friend, current, counter, angle, id, index, node, element, elements, box, // Structure this
	origin, originSettings, nodegraph, lights, keepDetails, infoBox;

const nodeKeys = Object.keys(data.nodes);
const numFriends = Object.keys(data.nodes).length - 1; // Dont count origin
const info = document.getElementById("info");
const nodeSize= 8/numFriends;
const circleRule = 2*3.1415/numFriends;

let coloring = {
	off: "#000000",
	inactive: "rgba(135, 121, 82, 0.2)",
	active: "rgba(135, 121, 82, 1)",

	origin: "#DC143C",
	red: "#d7385e",

	// Not yet done
	background: "rgb(252, 241, 212)",
	box: "rgba(145, 132, 96, 0.2)",
	boxText: "rgba(0, 0, 0, 0.95)"
}
document.getElementById("container").style["background-color"]= coloring.background;

infoBox = info.firstElementChild
infoBox.style["background-color"]= coloring.box;
infoBox.style["color"]= coloring.boxText;

origin = data.origin
originSettings = {
	   id: origin.json.id_str,
	   label: origin.json.name,
	   x: 0,
	   y: 0,
	   size: nodeSize*2,
	   color: coloring.origin
	}

var g = {
    nodes: [],
    edges: []
};

//Adding nodes

//We determine the x, y position of nodes by equally spacing them
//across a circle using polar coordinates then converting them to cartesian coordinates
//see https://en.wikipedia.org/wiki/Polar_coordinate_system

counter = 1;
for (node in data.nodes){
    current = data.nodes[node];
    angle = circleRule * counter;
    counter++;

    g.nodes.push({
        id: current.json.id_str,
        label: current.json.name,
        x: Math.sin(angle),
        y: Math.cos(angle),
        size: nodeSize,
        color: coloring.active
    });
}

//Modifying origin Node

index = g.nodes.findIndex(node => node.id == origin.json.id_str);
g.nodes[index] = originSettings;

//Adding edges

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

//### Functions
let stack = []; // How many profile details are displayed

function getNodeFromId(id){
    return data.nodes.find(node => node.id_str == id);
}

function displayDetails(node, append=false){
	if(stack.length == 5 && append)
		return;
	if (stack.includes(node.json.id_str))
		return;
	else
		stack.push(node.json.id_str)

	let image = `<img src=${node.json.profile_image_url}>`;

    let header = `<h3 style="text-align:center;">
    		<a href=https://twitter.com/${node.json.screen_name}>${node.json.name}"</a><br>
            ${node.json.friends_count} Following&emsp;
            ${node.json.followers_count} Followers<br><hr style="width:50%;">`;

    let description = `${node.json.description}<br><hr style="width:50%;">
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
	stackSize = 0;
	for (var i = info.children.length - 1; i > 0; i--) 
		info.removeChild(info.children[i]);
	
	infoBox = info.firstElementChild;
	infoBox.innerHTML= "";

	stack = [];
}

function colorNodes(color, active=false){
	for(node in nodes){
		nodes[node].active = active;
		nodes[node].color = color;
		if (nodes[node].id == origin.json.id_str) // if origin, then origin color
			nodes[node].color = coloring.origin;
	}
	s.render();
}

function markNodes(node, onColor, offColor, ctrlKey){
	for(node in nodes){
		if (nodes[node].active && ctrlKey || nodegraph.id == nodes[node].id){
			nodes[node].color = onColor;
			if (nodes[node].id == origin.json.id_str) // if origin, then origin color
				nodes[node].color = coloring.origin;
		}
		else{
			nodes[node].active = false;
			nodes[node].color = offColor;
			//size
		}
	}
	s.render();
}

function colorEdges(color){
	for(let edge in edges){
		edges[edge].color = color
		edges[edge]["read_cam0:size"] = 1;
	}
	s.render();
}

function markEdges(node, onColor, offColor, ctrlKey=false){
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

//### Sigmajs

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

/*
* TIP: DONE
*   Create an array to store properties for each edge, node and edit them when you
*      want to change the properties, of the nodes or edges
*
* FIXME: Line 161 DONE
*   1. Should change properties upon clicking but revert upon clicking again	DONE
*   2. Should change other properties than the listed ones 	DONE
*   3. Should change properties the instance clicked, not after dragging	Canceled
*
* FIXME: Line 150
*   1. Complete showing the details DONE
*   2. Change the look of the DIV box DONE
*   3. Make the DIV box appear on the right side Canceled
*   4. Make text size smaller DONE
*
* FIXME: DONE
*   1. Change all properties of nodes first initialised DONE
*   2. Change all properties of edges first initialised DONE
*   3. Make clickStage event, return the nodes as they were DONE
*   4. Add color pallets DONE
* */


// Modify these to modify graph
const edges = s.graph.edges();
const nodes = s.graph.nodes();
for(node in nodes)
	nodes[node].active = false;

//overNode outNode
lights = true; // When this is off, clickNode shouldnt modify edges
keepDetails = false; // When this is on, outNode shouldnt modify DIV details

s.bind("overNode", function(e){
	nodegraph = e.data.node; // Node from sigmajs's pov, use to modify behavior
    current = data.nodes[nodegraph.id]; // Node from data pov, use to get data
	nodegraph.active = true;

	if(!keepDetails)
    	displayDetails(current);
})

s.bind("outNode", function(e){
	if(!keepDetails)
		clearDetails();
})

s.bind('clickNode', function(e) {
	nodegraph = e.data.node;  
    current = data.nodes[nodegraph.id];  
	nodegraph.active = true;
	keepDetails = true;

    displayDetails(current, e.data.captor.ctrlKey);
    if (lights) 
    	markEdges(current, coloring.red, coloring.active, e.data.captor.ctrlKey);
});

s.bind("doubleClickNode", function(e) {
	nodegraph = e.data.node;  
    current = data.nodes[nodegraph.id];  
	nodegraph.active = true;
	lights = false

    if (!lights)
    	markEdges(current, coloring.red, coloring.inactive, e.data.captor.ctrlKey);
	markNodes(current, coloring.active, coloring.inactive, e.data.captor.ctrlKey);
})

// overEdge outEdge clickEdge doubleClickEdge rightClickEdge clickStage

s.bind('doubleClickStage', function(e) {
	keepDetails = false;
	lights = true;

    colorEdges(coloring.active);
    colorNodes(coloring.active);
	clearDetails()
});


function checknode(nodeId){ // Checking, not used 
    return nodes.some(x => Array(data.nodes[nodeId].edges).includes(x.id));
}