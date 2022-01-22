function forceDirectedLayout(){
	// Add all clusters to clusterPoints
	let clusterPoints = {};
	let ccc = [{x: 0, y: 0, cluster: ""}]
	for(cluster of data.variables.clusters){
	    loopWhile:
	    while(true){
	    	if(!ccc.some(x => x.cluster == cluster))
	        	ccc.push({x: 0, y: 0, cluster: cluster});
	        cluster = cluster.slice(0, cluster.length-1);
	        if(cluster === "")
	            break loopWhile;
	    }
	}

	let L = 0.5; // Spring rest length
	let Kr = 0.2; // repulsive force constant
	let Ks = 0.3; // spring constant
	let deltaT = 1; // time step

	let N = ccc.length;

	for(let iii=0; iii < 3000; iii++){
		// Initialize net forces
		for (key in ccc){
		    ccc[key].forceX = 0;
		    ccc[key].forceY = 0;
		}

		// Repulsion between all pairs
		let flag = false
		for(let i1=0; i1 < ccc.length-1; i1++){
			node1 = ccc[i1];
			for(let i2=i1+1; i2 < ccc.length; i2++){
				node2 = ccc[i2];
				flag = (node2.cluster.slice(0, -1) == node1.cluster.slice(0, -1) ? true : false)
				dx = node2.x - node1.x;
				dy = node2.y - node1.y;
				if (dx != 0 || dy != 0){
					let distanceSquared = dx ** 2 + dy ** 2;
					let distance = Math.sqrt(distanceSquared);
					let force = Kr / distanceSquared;
					let fx = force * dx / distance;
					let fy = force * dy / distance;
					node1.forceX = node1.forceX - fx;
					node1.forceY = node1.forceY - fy;
					node2.forceX = node2.forceX + fx;
					node2.forceY = node2.forceY + fy;
				}
				else if(dx == 0 && dy == 0){
					node1.forceX = Math.random() * 0.1;
					node1.forceY = Math.random() * 0.1;
					node2.forceX = Math.random() * 0.1;
					node2.forceY = Math.random() * 0.1;
				}
			}
		}

		// Spring force between adjacent pairs 
		for(let i1=0; i1 < ccc.length; i1++){
			node1 = ccc[i1];
			for(let i2=0; i2 < ccc.length; i2++){
				// If two not neighbors continue
				if (!(node1.cluster.slice(0, cluster.length-1) == ccc[i2].cluster
					|| ccc[i2].cluster.slice(0, cluster.length-1) == node1.cluster))
					continue;

				node2 = ccc[i2];
				if (i1 < i2){
					let dx = node2.x - node1.x;
					let dy = node2.y - node1.y;
					if(dx != 0 || dy != 0){
						let distance = (dx ** 2 + dy ** 2);
						let force = Ks * (distance - L);
						let fx = force * dx / distance;
						let fy = force * dy / distance;
						node1.forceX = node1.forceX + fx;
						node1.forceY = node1.forceY + fy;
						node2.forceX = node2.forceX - fx;
						node2.forceY = node2.forceY - fy;
					}
				}
			}
		}
		
		// Update positions
		for(let i=0; i < N; i++){
		node = ccc[i];
		let dx = deltaT * node.forceX;
		let dy = deltaT * node.forceY;
		let displacementSquared = dx ** 2 + dy ** 2;
		if (displacementSquared > 1000){
			let s = Math.sqrt(1000/displacementSquared);
			dx = dx * s;
			dy = dy * s;
		}
		node.x = node.x + dx;
		node.y = node.y + dy;
		}
	}

	for(let i=0; i < ccc.length; i++){
		cluster = ccc[i];
		clusterPoints[cluster.cluster] = {x: cluster.x, y: cluster.y};
	}
	
	console.log(JSON.stringify(clusterPoints))
	return clusterPoints;
}