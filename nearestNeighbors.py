from node import *
import createSet
import numpy
import statsmodels.api as sm


def convertToNode(data):
    # TODO getData

    return data


def warmupFill(lot_nodes, anchor_nodes, k, numInitialNodes, sample_size=100):
    # TODO
    anchor_size_initial = 7

    # take random sample of lot nodes and perform regression (can probably import something to do this for us

    # using this: https://towardsdatascience.com/simple-and-multiple-linear-regression-in-python-c928425168f9
    random_sample_nodes = numpy.random.choice(lot_nodes, sample_size, replace=False)
    sqft_vector = map(lambda x: x.sqft, random_sample_nodes)
    price_vector = map(lambda x: x.price, random_sample_nodes)
    metro_vector = map(lambda x: x.distanceToMetro, random_sample_nodes)
    model = sm.OLS(price_vector, metro_vector).fit()
    predictions = model.predict(metro_vector)
    # TODO - make this work!!!

    # populate anchor nodes
    price_delta = max(price_vector) / anchor_size_initial
    metro_delta = max(metro_vector) / anchor_size_initial
    sqft_delta = max(sqft_vector) / anchor_size_initial
    for i in range(anchor_size_initial):
        for j in range(anchor_size_initial):
            for k in range(anchor_size_initial):
                anchor_nodes[i][j].append(AnchorNode(i * 10000 + j * 100 + k))

    # connect anchor nodes (up, down, left, right, AND diagonal)
    for i in range(7):
        for j in range(7):
            for k in range(7):
                for i_ in range(i - 1, i + 2):
                    for j_ in range(j - 1, j + 2):
                        for k_ in range(k - 1, k + 2):
                            if i_ < (anchor_size_initial and j_ < anchor_size_initial and k_ < anchor_size_initial
                                     and i_ > 0 and j_ > 0 and k_ > 0 and i != i_ and j != j_ and k != k_):
                                anchor_nodes[i][j][k].addNeighbor(anchor_nodes[i_][j_][k_])
        # ... eww ^

    for node in lot_nodes:
        # assign it to its nearest anchor node
        node.addNeighbor(findAnchorNode(node, anchor_nodes, price_delta, sqft_delta, metro_delta))

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
                A[i][j] = lot_nodes[i].getDistance(lot_nodes[j])
    A = A + numpy.transpose(A)

    # now we find the smallest values in each row, return their indexes, and set those as the (initial) k-n-n
    for i in range(numInitialNodes):
        idx = numpy.argpartition(A[i], k)  # get indexes of smallest values (closest distances
        for n in idx:
            lot_nodes[i].addNeighbor(lot_nodes[n])


def findAnchorNode(lot_node, anchor_nodes, price_delta, sqft_delta, metro_delta=None):
    price_coord = lot_node.price / price_delta  # TODO floor this
    sqft_coord = lot_node.sqft / sqft_delta
    if metro_delta is not None:
        metro_coord = lot_node.distanceToMetro / metro_delta
        return anchor_nodes[price_coord][sqft_coord][metro_coord]
    return anchor_nodes[price_coord][sqft_coord]


def populate_database():
    # important constants
    warmup_size = 100
    sample_size = 100
    k = 5

    # node lists (anchor nodes need to be Random access, lot nodes theoretically don't - this is only used for
    # initialization
    lot_nodes = []
    anchor_nodes = [[[]]]  # TODO - do this correctly lol

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

    # run warmupFill to start populating the database (split the list into 2 sublists, warmup and all else (or just
    # pick an index to be the cutoff
    warmupFill(lot_nodes, anchor_nodes, k, warmup_size, sample_size)

    # do fill up everything else
    # for datapoint in datapoint_list:
