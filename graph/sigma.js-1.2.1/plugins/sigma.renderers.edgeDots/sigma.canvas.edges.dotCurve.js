
/**
 * This example shows how the edgeDots plugin can be used to display dots
 * on the edges near the nodes in the graph.
 */
var i,
    s,
    N = 2,
    E = 1,
    g = {
        nodes: [],
        edges: []
    };

// Generate a random graph:
for (i = 0; i < N; i++)
    g.nodes.push({
        id: 'n' + i,
        label: 'Node ' + i,
        x: Math.random(),
        y: Math.random(),
        size: Math.random(),
        color: '#666'
    });
// Some colors to use on the dots
var colors = ["#ff0000", "#00ff00", "#0000ff"];
for (i = 0; i < E; i++)
    g.edges.push({
        id: 'e' + i,
        label: 'Edge ' + i,
        source: 'n0',
        target: 'n1',
        size: Math.random(),
        color: '#ccc',
        type: 'curve',
        dotOffset:4,
        dotSize:1.2,
        sourceDotColor:colors[i%colors.length],
        targetDotColor:colors[(i+1)%colors.length]
    });

// Instantiate sigma:
s = new sigma({
    graph: g,
    renderer: {
        container: document.getElementById('graph-container'),
        type: 'canvas'
    }
});
