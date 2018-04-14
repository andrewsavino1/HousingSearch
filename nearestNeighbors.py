from node import *
import createSet
import numpy
import statsmodels.api as sm
import urllib.request
from bs4 import BeautifulSoup
import os
import geojson as geo
global sqft_mult, metro_mult, price_delta, sqft_delta, metro_delta

def convertToNode(data, schools, parks, metro, grocery):

    url = "https://www.stlouis-mo.gov/government/departments/sldc/real-estate" \
          "/lra-owned-property-search.cfm?detail=1&parcelId=" \
          + str(data['properties']['ParcelID'])
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, "lxml")
    table = soup.find('table', class_= 'data vertical-table striped')
    info = dict()
    # table_body = table.find('tbody')
    for row in table.findAll('tr'):
        cells = row.findAll('td')
        states = row.findAll('th')
        info[states[0].find(text=True)] = cells[0].find(text=True)

    coords = data['geometry']['coordinates']

    loc = Location(coords[0], coords[1])

    # cosine(38.63*pi/180) * 69.172
    metroDist = findClosestLocation(loc, metro) * 69.172
    schoolDist = findClosestLocation(loc, schools) * 69.172
    groceryDist = findClosestLocation(loc, grocery) * 69.172
    parkDist = findClosestLocation(loc, parks) * 69.172

    node = LotNode(int(info['Parcel ID']), info['Property Address'],
                    info['Value (Standard or Appraised)'],
                    info['Lot Square Feet'], loc.x, loc.y)

    node.setKidFriendly(schoolDist, parkDist)
    node.setMetroDistsance(metroDist)
    node.setNearGrocery(groceryDist)
    print(node)

    return node


def findClosestLocation(house, set):
    min_dist = 99999999
    for loc in set:
        min_dist = min(min_dist, loc.getDistance(house))
    return min_dist


def get_anchor_code(i, j, k):
    return i * 10000 + j * 100 + k


def warmupFill(lot_nodes, anchor_nodes, k, numInitialNodes, sample_size=100):
    global metro_mult, sqft_mult, sqft_delta, metro_delta, price_delta
    anchor_size_initial = 7

    # take random sample of lot nodes and perform regression (can probably import something to do this for us

    # using this: https://towardsdatascience.com/simple-and-multiple-linear-regression-in-python-c928425168f9
    random_sample_nodes = numpy.random.choice(lot_nodes.keys(), size=sample_size, replace=False)
    sqft_vector = map(lambda x: x.sqft, random_sample_nodes)
    price_vector = map(lambda x: x.price, random_sample_nodes)
    metro_vector = map(lambda x: x.distanceToMetro, random_sample_nodes)
    model_metro = sm.OLS(price_vector, metro_vector).fit()
    model_sqft = sm.OLS(price_vector, sqft_vector).fit()

    metro_mult = model_metro.predict(metro_vector)
    sqft_mult = model_sqft.predict(sqft_vector)

    # populate anchor nodes
    price_delta = max(price_vector) / anchor_size_initial
    metro_delta = max(metro_vector) / anchor_size_initial
    sqft_delta = max(sqft_vector) / anchor_size_initial
    for i in range(anchor_size_initial):
        for j in range(anchor_size_initial):
            for k in range(anchor_size_initial):
                anchor_nodes[get_anchor_code(i, j, k)] = AnchorNode(get_anchor_code(i, j, k))
                print(i+j+k)
    print(x for x in anchor_nodes.keys())

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
    for i in range(old_dimensions[0], new_dimensions[0]+1):
        for j in range(old_dimensions[1], new_dimensions[1]+1):
            for k in range(old_dimensions[2], new_dimensions[2] + 1):
                anchorNode = AnchorNode(get_anchor_code(i, j, k))
                for i_ in range(i - 1, i + 2):
                    for j_ in range(j - 1, j + 2):
                        for k_ in range(k - 1, k + 2):
                            if i_ < (new_dimensions[0] and j_ < new_dimensions[1] and k_ < new_dimensions[2]
                                     and i_ > 0 and j_ > 0 and k_ > 0 and i != i_ and j != j_ and k != k_):
                                if not anchorNode.hasNeighbor(anchor_nodes[get_anchor_code(i_, j_, k_)]):
                                    anchorNode.addNeighbor(anchor_nodes[get_anchor_code(i_, j_, k_)])
                anchor_nodes[get_anchor_code(i, j, k)] = anchorNode

    return anchor_nodes


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


def populate_database(k, warmup_size = 100, sample_size=100):
    global sqft_mult, metro_mult
    # important constants
    warmup_size = 100
    sample_size = 100

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
    callstr = os.getcwd() + '\\Data\\lra.geojson'
    file = geo.load(open(callstr))
    for dataline in file['features']:
        node = convertToNode(dataline, schools, parks_and_playgrounds, metro_stops, grocery_stores)
        lot_nodes.append(node)

    # run warmupFill to start populating the database (split the list into 2 sublists, warm-up and all else (or just
    # pick an index to be the cutoff
    sqft_mult, metro_mult = warmupFill(lot_nodes[::warmup_size], anchor_nodes, k, warmup_size, sample_size)

    # do fill up everything else
    for node in lot_nodes[warmup_size::]:
        add_node_to_database(node, k, anchor_nodes)


def get_search_parameters():
    price_min_input = input("Enter a price minimum (or 'N' if not applicable): ")
    while not checkInt(price_min_input):
        print("Error. Price minimum must be a integer value.")
        price_min_input = input("Enter a price minimum (or 'N' if not applicable): ")

    price_max_input = input("Enter a price maximum (or 'N' if not applicable): ")
    while not checkInt(price_max_input):
        print("Error. Price maximum must be a integer value.")
        price_max_input = input("Enter a price maximum (or 'N' if not applicable): ")

    metro_dist_input = input("Enter a maximum acceptable distance to a metro stop (or 'N' if not applicable): ")
    while not checkInt(metro_dist_input):
        print("Error. Distance maximum must be a integer value.")
        price_min_input = input("Enter a maximum acceptable distance to a metro stop (or 'N' if not applicable):")

    acreage_min_input = input("Enter a minimum acceptable acreage (or 'N' if not applicable): ")
    while not checkInt(acreage_min_input):
        print("Error. Acreage minimum must be an integer value.")
        acreage_min_input = input("Enter a minimum acceptable acreage (or 'N' if not applicable): ")

    parking_input = input("Do you require a parking spot? Y/N: ")
    while not checkBin(parking_input):
        print("Error. Entered value must be either 'Y' or 'N'.")
        parking_input = input("Do you require a parking spot? Y/N: ")

    grocery_input = input("Do you need to be within walking distance of a grocery store? Y/N: ")
    while not checkBin(grocery_input):
        print("Error. Entered value must be either 'Y' or 'N'.")
        grocery_input = input("Do you need to be within walking distance of a grocery store? Y/N: ")

    family_input = input("Do you require a family-friendly property? Y/N: ")
    while not checkBin(family_input):
        print("Error. Entered value must be either 'Y' or 'N'.")
        family_input = input("Do you require a family-friendly property? Y/N: ")

    property_input = input("Do you wish to search over empty lots? Y/N: ")
    while not checkBin(property_input):
        print("Error. Entered value must be either 'Y' or 'N'.")
        family_input = input("Do you require a family-friendly property? Y/N: ")

    price_min = 0 if price_min_input == 'N' else int(str(price_min_input))
    price_max = 99999999 if price_max_input == 'N' else int(str(price_max_input))
    metro_dist = 99999999 if metro_dist_input == 'N' else int(str(metro_dist_input))
    acreage_min = 0 if acreage_min_input == 'N' else int(str(acreage_min_input))

    parking = True if str(parking_input) == "Y" else False
    grocery = True if str(grocery_input) == "Y" else False
    family = True if str(family_input) == "Y" else False
    property = True if str(property_input) == "Y" else False

    dummy_node = LotNode('', price_min, acreage_min, 0, 0)
    dummy_node.setNearGrocery(grocery)
    dummy_node.setMetroDistsance(metro_dist)
    dummy_node.setKidFriendly(family)

    return dummy_node


# check that user argument is a valid integer
def checkInt(s):
    try:
        int(str(s))
        return True
    except ValueError:
        if str(s) == 'N':
            return True
        return False

# check that user argument is valid binary value
def checkBin(s):
    if str(s) == 'N' or str(s) == 'Y':
        return True
    return False


def main():
    # parameters:
    anchor_nodes = {}
    k = 5
    lot_nodes = {}

    populate_database(k)
    while True:
        get_search_parameters()


if __name__ == '__main__': main()
