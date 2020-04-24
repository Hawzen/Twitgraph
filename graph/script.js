data.nodes = Object.fromEntries(Object.entries(data['nodes']).slice(0, 50));
data.nodes[data.origin.json.id_str] = data.origin;

const nodeKeys = Object.keys(data.nodes);
const numFriends = Object.keys(data.nodes).length - 1; // Dont count origin
const box = document.getElementById("info").innerHTML;
const nodeSize= 8/numFriends;
const circleRule = 2*3.1415/numFriends;

const coloring = {
	off: "#000000",
	inactive: "#3b3b3b",
	active: "#b5b5b5"
}

let friend, current, counter, angle, id, index, node,
	origin, originSettings, nodegraph, dobule;


origin = data['origin']
originSettings = {
	   id: origin.json.id_str,
	   label: origin['json']["name"],
	   x: 0,
	   y: 0,
	   size: nodeSize*2,
	   color: "#DC143C"
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
for (node in data['nodes']){
    current = data['nodes'][node]['json'];
    angle = circleRule * counter;
    counter++;

    g.nodes.push({
        id: current.id_str,
        label: current.name,
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

// for (index in data['origin']['edges']) {
// 	if(nodeKeys.includes(String(data.origin.json[index]))){
// 	    g.edges.push({
// 	        id: '0' + counter, //o: origin, e.g. 'o4' (meaning edge 4)
// 	        source: origin.json.id_str, //0 is the origin's id
// 	        target: String(data.origin.json[index]),
// 	        size: 1,
// 	        color: coloring.active,
// 	        type: "tapered",
// 	        dotOffset:4,
// 	        dotSize:1.2,
// 	        sourceDotColor: "#00ff00",
// 	        targetDotColor:"#ff0000"
// 	    });
// 	    counter++;
// 	}
// }

counter = 0;
for (node in data.nodes) {
    current = data.nodes[node];

    for (index in current.edges) {
        id = String(current.edges[index]) //Id of target

        if (nodeKeys.includes(String(id))) { 
            g.edges.push({
                id: "e_" + current.json.id_str + "_" + counter,
                source: current.json.id_str,
                target: id,
                size: 0.05,
                color: coloring.active,
                type: "cruve"
            });
            counter++;
        }
    }
}

//### Functions

function getNodeFromId(id){
    return data.nodes.find(node => node.id_str == id);
}

function displayDetails(node){
    let string = `<h3 style="text-align:center;">${node.json.name}<hr>
            ${node.json.description}<br>
            ${node.json.friends_count} Following&emsp;
            ${node.json.followers_count} Followers</h3>` + box;

    document.getElementById("info").innerHTML = string;
}

function markEdges(node, ctrlKey, offcolor=coloring.active){
	for(let edge in edges){	
        if(edges[edge].id.includes(node.json.id_str)){
            edges[edge].color = "#e60000";
            edges[edge].active = true;
            edges[edge]["read_cam0:size"] = 5
        }
        else if (edges[edge].active && ctrlKey){} // Skip when user holds ctrlKey
        else {
        	edges[edge].color = offcolor;
        	// edges[edge].active = false;
        	edges[edge]["read_cam0:size"] = 1
        }
    }
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
* FIXME: Line 161
*   1. Should change properties upon clicking but revert upon clicking again	DONE
*   2. Should change other properties than the listed ones 	DONE
*   3. Should change properties the instance clicked, not after dragging	Canceled
*
* FIXME: Line 150
*   1. Complete showing the details
*   2. Change the look of the DIV box
*   3. Make the DIV box appear on the right side Canceled
*   4. Make text size smaller
*
* FIXME:
*   1. Change all properties of nodes first initialised DONE
*   2. Change all properties of edges first initialised DONE
*   3. Make clickStage event, return the nodes as they were 
*   4. Add Dark mode button
* */


// Modify these to modify graph
const edges = s.graph.edges();
const nodes = s.graph.nodes();
for(node in nodes)
	nodes[node].active = false;

//overNode outNode
double = false;
s.bind('clickNode', function(e) {
	nodegraph = e.data.node; // Node from sigmajs's pov, use to modify behavior
    current = data.nodes[nodegraph.id]; // Node from data pov, use to get data
	nodegraph.active = true;

    displayDetails(current)
    if (!double)
    	markEdges(current, e.data.captor.ctrlKey)
});

s.bind("doubleClickNode", function(e) {
	nodegraph = e.data.node; // Node from sigmajs's pov, use to modify behavior
    current = data.nodes[nodegraph.id]; // Node from data pov, use to get data

    if(!e.data.captor.ctrlKey)
    	double = !double
    markEdges(current, e.data.captor.ctrlKey, coloring.inactive)

	nodegraph.active = true;

	for(node in nodes){
		if (nodes[node].active && e.data.captor.ctrlKey || nodegraph.id == nodes[node].id){
			nodes[node].color = "#b5b5b5"
			if (nodes[node].id == origin.json.id_str)
				nodes[node].color = "#DC143C"
		}
		else{
			nodes[node].active = false
			nodes[node].color = coloring.inactive
			//size
		}
	}
})

s.bind('overEdge outEdge clickEdge doubleClickEdge rightClickEdge', function(e) {
    console.log(e.type, e.data.edge, e.data.captor);
});
s.bind('clickStage', function(e) {
    console.log(e.type, e.data.captor);
});
s.bind('doubleClickStage rightClickStage', function(e) {
    for (edge in edges){
    	edges[edge].color = coloring.active;
    	// edges[edge].active = false;
    	edges[edge]["read_cam0:size"] = 1
    }

    for(node in nodes)
			nodes[node].active = true
			nodes[node].color = coloring.active
			//size
});

console.log(s.graph);