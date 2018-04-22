from node import *
import time


def iterativeSearch(nodes, search_node, sqft_mult, metro_mult, k, argv):
    start = time.time()

    nodes_and_distances = []
    for node in nodes:
        if node.matches_conditions(argv) == 0:
            nodes_and_distances.append((node, search_node.getDistance(node, sqft_mult, metro_mult)))
    nodes_and_distances.sort(key=(lambda x: x[1]))

    end = time.time()

    print ('Time elapsed in iterative search: ' + str(end - start) + 's')
    return nodes_and_distances[0:k]

