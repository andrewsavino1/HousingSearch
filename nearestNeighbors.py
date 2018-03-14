import node
import createSet


def convertToNode(data):
    # TODO getData

    return node


def warmupFill(lot_nodes, anchor_nodes, numInitialNodes=100):
    # TODO

    # take random sample of lot nodes and perform regression (can probably import something to do this for us

    # populate anchor nodes

    # connect anchor nodes (up, down, left, right, AND diagonal)

    for node in lot_nodes:
        # assign it to its nearest anchor node

        # calculate distances between nodes (note - let's not do it redundantly.  If we know a->b, we know b->a.
        # i.e. we should fill out an upper-triangular distance matrix and get the smallest (non-zero/None) distances
        # to determine our nearest-neighbors

        # idea: (probably need to use numpy)
        # A = distance matrix - generate by:
        # i:0->100
        #   j:0->100
        #       if(j<i): calculate distance (strictly < so diagonal is all 0's)
        # then do A + transpose(A), now we can find the min values on each row to find the k-n-n


def findAnchorNode(lot_node, anchor_nodes, price_delta, sqft_delta, metro_delta=None):
    price_coord = lot_node.price / price_delta # TODO floor this
    sqft_coord = lot_node.sqft / sqft_delta
    if metro_delta is not None:
        metro_coord = lot_node.distanceToMetro / metro_delta
        return anchor_nodes[price_coord][sqft_coord][metro_coord]
    return anchor_nodes[price_coord][sqft_coord]


def populate_database():
    # important constants
    warmup_size = 100

    # node lists (anchor nodes need to be Random access, lot nodes theoretically don't - this is only used for
    # initialization
    lot_nodes = []
    anchor_nodes = [[[]]] # TODO - do this correctly lol

    # create set of grocery stores
    grocery_stores = createSet.populateGroceryStoreList()

    # create set of metro stops
    metro_stops = createSet.populateMetroList()

    # create set of schools
    schools = createSet.populateSchoolList()

    # create set of parks
    parks_and_playgrounds = createSet.populateParksandPlaygroundsList()

    # call convertToNode on every row of the data file
    file = None # TODO - whatever stores the raw data
    for dataline in file:
        node = convertToNode(dataline)
        lot_nodes.append(node)


    # run warmupFill to start populating the database (split the list into 2 sublists, warmup and all else (or just
    # pick an index to be the cutoff
    warmupFill(lot_nodes, anchor_nodes, warmup_size)

    # do fill up everything else
    for datapoint in datapoint_list:


