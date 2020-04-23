console.log(data);
var data;
//data['nodes'] = Object.fromEntries(Object.entries(data['nodes']).slice(0, 10));
const nodeKeys = Object.keys(data['nodes'])
const numFriends = Object.keys(data['nodes']).length;
let friend, current, counter, angle, size;
const box = document.getElementById("info").innerHTML;

let id;

g = {
    nodes: [],
    edges: []
};

//Adding All nodes

//Adding target Node
nodeSize = 8/numFriends;
g.nodes.push({
   id: 0,
   label: data['origin']['json']["name"],
   x: 0,
   y: 0,
   size: nodeSize*2,
   color: "#DC143C"
});

//Adding friends nodes

//We determine the x, y position of nodes by equally spacing them
//across a circle using polar coordinates then converting them to cartesian coordinates
//see https://en.wikipedia.org/wiki/Polar_coordinate_system
counter = 1;
circleRule = 2*3.1415 / numFriends;
for (node in data['nodes']){
    current = data['nodes'][node]['json'];
    angle = circleRule * counter;
    counter++;

    g.nodes.push({
        id: current['id'],
        label: current["name"],
        x: Math.sin(angle),
        y: Math.cos(angle),
        size: nodeSize,
        color: "#b5b5b5"
    });
}

//Adding edges

counter = 1;
var colors = ["#ff0000", "#00ff00", "#0000ff"];

for (id in data['origin']['edges']) {
	if(nodeKeys.includes(String(data['origin']['edges'][id]))){
	    g.edges.push({
	        id: '0' + counter, //o: origin, e.g. 'o4' (meaning edge 4)
	        source: 0, //0 is the origin's id
	        target: data['origin']['edges'][id],
	        size: 1,
	        color: "#000",
	        type: "tapered",
	        dotOffset:4,
	        dotSize:1.2,
	        sourceDotColor: "#00ff00",
	        targetDotColor:"#ff0000"
	    });

	    counter++;
	}
}

counter = 0;
for (let nodeid in data["nodes"]) {
    current = data['nodes'][nodeid]

    for (let num in current["edges"]) {
        id = current['edges'][num]

        if (nodeKeys.includes(String(id))) { // FIXME
            g.edges.push({
                id: "oo" + id + "-" + counter,
                source: current['json']['id'],
                target: id,
                size: 0.5,
                color: "#b5b5b5",
                type: "line "
            });
            counter++;
        }
    }
}

function getNodeFromId(id){
    return data['nodes'][id]
}

var s = new sigma({
    graph: g,
    renderer: {
        container: document.getElementById('container'),
        type: 'canvas',
        settings: {
            minNodeSize: 1,
            maxNodeSize: 10,
            minEdgeSize: 0.01,
            maxEdgeSize: 0.01,
            enableEdgeHovering: true,
            edgeHoverSizeRatio: 2
        }
    }
});

/*
* TIP:
*   Create an array to store properties for each edge, node and edit them when you
*      want to change the properties, of the nodes or edges
*
* FIXME: Line 161
*   1. Should change properties upon clicking but revert upon clicking again
*   2. Should change other properties than the listed ones
*   3. Should change properties the instance clicked, not after dragging
*
* FIXME: Line 150
*   1. Complete showing the details
*   2. Change the look of the DIV box
*   3. Make the DIV box appear on the right side
*   4. Make text size smaller
*
* FIXME:
*   1. Change all properties of nodes first initialised
*   2. Change all properties of edges first initialised
*   3. Make clickStage event, return the nodes as they were
*   4. Add Dark mode button
* */

let edges = s.graph.edges();
//overNode outNode
s.bind(' clickNode', function(e) {
    let node;
    e.data.node.toString = function () { return JSON.stringify(this) };
    if(e.data.node.id === 0)
        node = data['origin'];
    else
        node = data['nodes'][String(e.data.node.id)];

    console.log(node);
    let string = `<h3 style="text-align:center;">${node.json.name}<hr>
            ${node.json.description}<br>
            ${node.json.friends_count} Following&emsp;
            ${node.json.followers_count} Followers</h3>` + box;
    try {
        document.getElementById("info").innerHTML = string;
    } catch(TypeError){
        document.getElementById("info").innerHTML = `Name:\t${e.data.node.label} ` + box // FIXME: Why happens?
    }
    let bool = false;

    for(let edge in edges){
        if(edges[edge].id.includes(node.json.id)){
            edges[edge].color = "#e60000";
            edges[edge].size = 50;
        }
    }
});

s.bind('overEdge outEdge clickEdge doubleClickEdge rightClickEdge', function(e) {
    console.log(e.type, e.data.edge, e.data.captor);
});
s.bind('clickStage', function(e) {
    console.log(e.type, e.data.captor);
});
s.bind('doubleClickStage rightClickStage', function(e) {
    console.log(e.type, e.data.captor);
});

console.log(s.graph);