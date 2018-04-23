from node import *
import time
num_results = 10
ctr_ = 0

def iterativeSearch(nodes, search_node, sqft_mult, metro_mult, k, argv):
    global ctr_
    nodes_and_distances = []
    for node in nodes:
        ctr_ += 1
        if node.matches_conditions(argv) == 0:
            nodes_and_distances.append((node, search_node.getDistance(node, sqft_mult, metro_mult)))
    nodes_and_distances.sort(key=(lambda x: x[1]))

    print('Iterative: '+ str(ctr_))

    return nodes_and_distances[0:num_results]

