from node import *
import createSet
import numpy
import statsmodels.api as sm
import urllib.request
from bs4 import BeautifulSoup

global sqft_mult, metro_mult, price_delta, sqft_delta, metro_delta


def convertToNode(data):
    # TODO getData
    url = "https://www.stlouis-mo.gov/government/departments/sldc/real-estate" \
          "/lra-owned-property-search.cfm?detail=1&parcelId=" \
          + str(data['ParcelID'])
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, "lxml")
    table = soup.find('table', class_='data vertical-table striped')
    info = dict()
    for row in table.findAll('tr'):
        cells = row.findAll('td')
        states = row.findAll('th')
        info[states[0].find(text=True)] = cells[0].find(text=True)

    node = LotNode(int(info['Parcel ID']), info['Property Address'],
                    info['Value (Standard or Appraised)'],
                    info['Lot Square Feet'], data['centerX'], data['centerY'])
    return node


def get_anchor_code(i, j, k):
    return i * 10000 + j * 100 + k


def warmupFill(lot_nodes, anchor_nodes, k, numInitialNodes, sample_size=100):
    # TODO: how do to a 3d array for anchor nodes in python? dimensions must all be expandable
    global metro_mult, sqft_mult, sqft_delta, metro_delta, price_delta
    anchor_size_initial = 7

    # take random sample of lot nodes and perform regression (can probably import something to do this for us

    # using this: https://towardsdatascience.com/simple-and-multiple-linear-regression-in-python-c928425168f9
    random_sample_nodes = numpy.random.choice(lot_nodes, sample_size, replace=False)
    sqft_vector = map(lambda x: x.sqft, random_sample_nodes)
    price_vector = map(lambda x: x.price, random_sample_nodes)
    metro_vector = map(lambda x: x.distanceToMetro, random_sample_nodes)
    model = sm.OLS(price_vector, metro_vector).fit()
    predictions = model.predict(metro_vector)
    # TODO - make this work -> and populate these values:
    metro_mult = 1
    sqft_mult = 1

    # populate anchor nodes
    price_delta = max(price_vector) / anchor_size_initial
    metro_delta = max(metro_vector) / anchor_size_initial
    sqft_delta = max(sqft_vector) / anchor_size_initial
    for i in range(anchor_size_initial):
        for j in range(anchor_size_initial):
            for k in range(anchor_size_initial):
                anchor_nodes[get_anchor_code(i, j, k)] = AnchorNode(get_anchor_code(i, j, k))

    # connect anchor nodes (up, down, left, right, AND diagonal)
    for i in range(7):
        for j in range(7):
            for k in range(7):
                for i_ in range(i - 1, i + 2):
                    for j_ in range(j - 1, j + 2):
                        for k_ in range(k - 1, k + 2):
                            if i_ < (anchor_size_initial and j_ < anchor_size_initial and k_ < anchor_size_initial
                                     and i_ > 0 and j_ > 0 and k_ > 0 and i != i_ and j != j_ and k != k_):
                                anchor_nodes[get_anchor_code(i, j, k)].addNeighbor(anchor_nodes[get_anchor_code(i_, j_, k_)])
        # ... eww ^

    for node in lot_nodes:
        # assign it to its nearest anchor node
        node.addNeighbor(findAnchorNode(node, anchor_nodes))

    # calculate distances between nodes (note - let's not do it redundantly.  If we know a->b, we know b->a.
    # i.e. we should fill out an upper-triangular distance matrix and get the smallest (non-zero/None) distances
    # to determine our nearest-neighbors

    # idea: (probably need to use numpy)
    # A = distance matrix - generate by:
    # i:0->100
    #   j:0->100
    #       if(j<i): calculate distance (strictly < so diagonal is all 0's)
    # then do A + transpose(A), now we can find the min values on each row to find the k-n-n
    A = numpy.zeros((numInitialNodes, numInitialNodes))
    for i in range(numInitialNodes):
        for j in range(numInitialNodes):
            if j < i:
                A[i][j] = lot_nodes[i].getDistance(lot_nodes[j], sqft_mult, metro_mult)
    A = A + numpy.transpose(A)

    # now we find the smallest values in each row, return their indexes, and set those as the (initial) k-n-n
    for i in range(numInitialNodes):
        idx = numpy.argpartition(A[i], k)  # get indexes of smallest values (closest distances
        for n in idx:
            lot_nodes[i].addNeighbor(lot_nodes[n])

    return sqft_mult, metro_mult


def expand_anchor_grid(anchor_nodes, old_dimensions, new_dimensions):
    # TODO - write this function

    for i in range(old_dimensions[0], new_dimensions[0]+1):
        for j in range(old_dimensions[1], new_dimensions[1]+1):
            for k in range(old_dimensions[2], new_dimensions[2] + 1):
                anchor_nodes[get_anchor_code(i, j, k)] = AnchorNode(get_anchor_code(i, j, k))

    raise ValueError('This method has not been implemented yet')


def findAnchorNode(lot_node, anchor_nodes):
    global price_delta, sqft_delta, metro_delta
    price_coord = lot_node.price // price_delta
    sqft_coord = lot_node.sqft // sqft_delta
    if metro_delta is not None:
        metro_coord = lot_node.distanceToMetro // metro_delta
        return anchor_nodes[get_anchor_code(price_coord, sqft_coord, metro_coord)]
    return anchor_nodes[get_anchor_code(price_coord, sqft_coord, 0)]


def find_nearest_neighbors(starting_node, searching_node, k, neighbor_list, neighbor_counter):
    # TODO - neighbor_counter needs to be updated simultaneoulsy on all branches - should be by ref, not value
    global sqft_mult, metro_mult
    assert starting_node.anchor_node  # verify the node has an anchor node

    if neighbor_counter[0] < k:
        possible_new_neighbors = []

        # first, add the nodes at this level of recursion
        for connected_node_tuple in searching_node.neighbors[0].neighbors:
            lot_tuple = connected_node_tuple[0], starting_node.getDistance(connected_node_tuple[0], sqft_mult,
                                                                           metro_mult)
            if lot_tuple not in searching_node.neighbors:
                if connected_node_tuple[0].getDistance(starting_node, sqft_mult, metro_mult) \
                        < searching_node.neighbors[-1][1]:
                    # replace furthest neighbor of the searching node with this new node, then sort so order maintained
                    searching_node.neighbors[-1] = (starting_node, connected_node_tuple[0].getDistance(starting_node,
                                                                                                       sqft_mult,
                                                                                                       metro_mult))
                    searching_node.sort(key=(lambda x: x[1]))

                if lot_tuple not in possible_new_neighbors:
                    possible_new_neighbors.append(lot_tuple)
                    neighbor_counter[0] += 1
        for next_node in possible_new_neighbors:
            find_nearest_neighbors(starting_node, next_node, k, neighbor_list, neighbor_counter)

        (neighbor_list.append(possible_new_neighbors)).sort(key=(lambda x: x[1]))
        if len(neighbor_list) > k:
            neighbor_list = neighbor_list[0::k]

        return neighbor_list


def add_node_to_database(node, k, anchor_nodes):
    node.addNeighbor(findAnchorNode(node, anchor_nodes))  # add the anchor node

    # add the neighbor nodes
    k_nearest_neighbors = find_nearest_neighbors(node, node, k, [], [0])
    for n in k_nearest_neighbors:
        node.addNeighbor(n)


def populate_database():
    global sqft_mult, metro_mult
    # important constants
    warmup_size = 100
    sample_size = 100
    k = 5

    # node lists (anchor nodes need to be Random access, lot nodes theoretically don't - this is only used for
    # initialization
    lot_nodes = []
    anchor_nodes = {}

    # create set of grocery stores
    grocery_stores = createSet.populateGroceryStoreList()

    # create set of metro stops
    metro_stops = createSet.populateMetroList()

    # create set of schools
    schools = createSet.populateSchoolList()

    # create set of parks
    parks_and_playgrounds = createSet.populateParksandPlaygroundsList()

    # call convertToNode on every row of the data file
    file = None  # TODO - whatever stores the raw data
    for dataline in file:
        node = convertToNode(dataline)
        lot_nodes.append(node)

    # run warmupFill to start populating the database (split the list into 2 sublists, warm-up and all else (or just
    # pick an index to be the cutoff
    sqft_mult, metro_mult = warmupFill(lot_nodes, anchor_nodes, k, warmup_size, sample_size)

    # do fill up everything else
    for node in lot_nodes[warmup_size::]:
        add_node_to_database(node, k, anchor_nodes)
