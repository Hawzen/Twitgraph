console.log(data);
const numFriends = Object.keys(data['friends']).length;
let friend, current, counter, angle, size, friend2;

g = {
    nodes: [],
    edges: []
};

//Adding All nodes

//Adding target Node
nodeSize = 8/numFriends;
g.nodes.push({
   id: 0,
   label: data['target']['username'],
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
for (friend in data['friends']){
    current = data['friends'][friend]['json'];
    angle = circleRule * counter;
    counter++;

    g.nodes.push({
        id: current['id'],
        label: friend,
        x: Math.cos(angle),
        y: Math.sin(angle),
        size: nodeSize,
        color: "#000000"
    });
}

//Adding edges

counter = 1;
var colors = ["#ff0000", "#00ff00", "#0000ff"];

for (friend in data['friends']) {
    current = data['friends'][friend]['json'];

    g.edges.push({
        id: 'o' + counter, //o: origin, e.g. 'o4' (meaning edge 4)
        source: 0, //0 is the origin node
        target: current['id'],
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

let friendsIds;
counter = 0;
for (friend in data["friends"]) {
    friendsIds = data['friends'][friend]['friends ids'];
    current = data["friends"][friend]["json"];
    for (friend2 in data["friends"]){
        if(friendsIds.includes(data["friends"][friend2]["json"]["id"])) {
            g.edges.push({
                id: "oo" + counter,
                source: current["id"],
                target: data["friends"][friend2]["json"]["id"],
                size: 0.5,
                color: "#000",
                type: "curve"   
            })
            counter++;
        }
    }
}
s = new sigma({
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
console.log(s.graph)