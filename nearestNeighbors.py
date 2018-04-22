from node import *
import createSet
import numpy
import urllib.request
from bs4 import BeautifulSoup
import os
import geojson as geo
import pandas as pd
import csv

global sqft_mult, metro_mult, price_delta, sqft_delta, metro_delta
global grid_dim
from sklearn.linear_model import LinearRegression
import time
from iterativeSearch import *


def print_to_csv(nodes):
    with open('housingData.csv', 'w', newline='') as csvfile:
        fieldnames = ['parcel_id', 'address', 'price', 'sqft', 'metro_dist', 'grocery', 'kid_friendly', 'status',
                      'zipcode']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for node in nodes:
            kf = 'Y' if node.kidFriendly else 'N'
            gro = 'Y' if node.nearGrocery else 'N'
            stat = 'Vacant' if node.vacant else 'Built'
            writer.writerow({
                'parcel_id': node.id,
                'address': node.address,
                'price': node.price,
                'sqft': node.sqft,
                'metro_dist': node.distanceToMetro,
                'kid_friendly': kf,
                'grocery': gro,
                'status': stat
                # 'zipcode': node.zipcode
            })


def read_from_csv(file):
    nodes_list = []
    with open(os.getcwd() + 'housingData.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter = ' ')
        for row in reader:
            id = row[0]
            address = row[1]
            price = row[2]
            sqft = row[3]
            metro_dist = row[4]
            kf = True if row[5] is 'Y' else False
            groc = True if row[6] is 'Y' else False
            stat = True if row[7] is 'Y' else False
            node = LotNode(id, address, price, sqft,0,0,vacant=stat)
            node.setKidFriendly_known(kf)
            node.setNearGrocery_known(groc)
            node.setMetroDistance(metro_dist)
            nodes_list.append(node)
    return nodes_list


def convertToNode(data, schools, parks, metro, grocery, price_dict):
    try:
        url = "https://www.stlouis-mo.gov/government/departments/sldc/real-estate" \
              "/lra-owned-property-search.cfm?detail=1&parcelId=" \
              + str(data['properties']['ParcelID'])
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, "lxml")
        table = soup.find('table', class_='data vertical-table striped')
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

        price = info['Value (Standard or Appraised)']
        try:
            price = int(price.replace('$', ''))
        except:
            neighborhood = info["Neighborhood"]
            line = '123456789()\n'
            for char in line:
                neighborhood = neighborhood.replace(char, '')
            try:
                price = price_dict[neighborhood.rstrip()]
            except:
                price = 1000
            if price == 0:
                price = 1000

        node = LotNode(int(info['Parcel ID']), info['Property Address'],
                       price,
                       int(info['Lot Square Feet']), loc.x, loc.y)

        node.setKidFriendly(schoolDist, parkDist)
        node.setMetroDistance(metroDist)
        node.setNearGrocery(groceryDist)
        print(node)

        return node
    except Exception as e:
        print(e)
        print(data['properties']['fullAddress'])
        print(url + '\n')


def findClosestLocation(house, set):
    min_dist = 99999999
    for loc in set:
        min_dist = min(min_dist, loc.getDistance(house))
    return min_dist


def get_anchor_code(i, j, k):
    return i * 10000 + j * 100 + k


def warmupFill(lot_nodes, anchor_nodes, k, numInitialNodes, sample_size=10):
    global metro_mult, sqft_mult, sqft_delta, metro_delta, price_delta
    anchor_size_initial = 10

    # take random sample of lot nodes and perform regression (can probably import something to do this for us

    # using this: https://towardsdatascience.com/simple-and-multiple-linear-regression-in-python-c928425168f9

    random_sample_nodes = numpy.random.choice(lot_nodes, size=sample_size, replace=False)
    sqft_vector = list(map(lambda x: x.sqft, random_sample_nodes))
    price_vector = list(map(lambda x: x.price, random_sample_nodes))
    metro_vector = list(map(lambda x: x.distanceToMetro, random_sample_nodes))
    X = numpy.array([sqft_vector, metro_vector]).transpose()

    regression = LinearRegression()  # sm.OLS(price_vector, metro_vector).fit()
    print(X)

    regression.fit(X, price_vector)

    # model_sqft = LinearRegression()#m.OLS(price_vector, sqft_vector).fit()
    # model_metro.fit(price_vector, metro_vector)
    # model_sqft.fit(price_vector, sqft_vector)

    metro_mult = regression.coef_[0]
    sqft_mult = regression.coef_[1]

    print(metro_mult)
    print(sqft_mult)

    # populate anchor nodes
    price_delta = max(price_vector) / anchor_size_initial
    metro_delta = max(metro_vector) / anchor_size_initial
    sqft_delta = max(sqft_vector) / anchor_size_initial
    for i in range(anchor_size_initial):
        for j in range(anchor_size_initial):
            for k in range(anchor_size_initial):
                anchor_nodes[get_anchor_code(i, j, k)] = AnchorNode(get_anchor_code(i, j, k))
                # print(i+j+k)
    print(x for x in anchor_nodes.keys())

    # connect anchor nodes (up, down, left, right, AND diagonal)
    global grid_dim
    grid_dim = (anchor_size_initial, anchor_size_initial, anchor_size_initial)
    for i in range(anchor_size_initial):
        for j in range(anchor_size_initial):
            for k in range(anchor_size_initial):
                for i_ in range(i - 1, i + 2):
                    for j_ in range(j - 1, j + 2):
                        for k_ in range(k - 1, k + 2):
                            if (i_ < anchor_size_initial and j_ < anchor_size_initial and k_ < anchor_size_initial and
                                        i_ > 0 and j_ > 0 and k_ > 0 and (i != i_ or j != j_ or k != k_)):
                                anchor_nodes[get_anchor_code(i, j, k)].addNeighbor(
                                    anchor_nodes[get_anchor_code(i_, j_, k_)])
                                # ... eww ^

    for node in lot_nodes:
        # assign it to its nearest anchor node
        node.setAnchor(findAnchorNode(node, anchor_nodes))
        findAnchorNode(node, anchor_nodes).addNeighbor(node)

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


def expand_anchor_grid(anchor_nodes, new_dimensions):
    global grid_dim
    old_dimensions = grid_dim
    for i in range(0, int(new_dimensions[0]) + 1):
        for j in range(0, int(new_dimensions[1]) + 1):
            for k in range(0, int(new_dimensions[2]) + 1):
                if not get_anchor_code(i, j, k) in anchor_nodes:
                    anchor_nodes[get_anchor_code(i, j, k)] = AnchorNode(get_anchor_code(i, j, k))

    for i in range(0, int(new_dimensions[0]) + 1):
        for j in range(0, int(new_dimensions[1]) + 1):
            for k in range(0, int(new_dimensions[2]) + 1):
                for i_ in range(i - 1, i + 2):
                    for j_ in range(j - 1, j + 2):
                        for k_ in range(k - 1, k + 2):
                            if (i_ < new_dimensions[0] and j_ < new_dimensions[1] and k_ < new_dimensions[2]
                                and i_ > 0 and j_ > 0 and k_ > 0 and (i != i_ or j != j_ or k != k_)):
                                if not anchor_nodes[get_anchor_code(i, j, k)].hasNeighbor(
                                        anchor_nodes[get_anchor_code(i_, j_, k_)]):
                                    anchor_nodes[get_anchor_code(i, j, k)].addNeighbor(
                                        anchor_nodes[get_anchor_code(i_, j_, k_)])

    grid_dim = new_dimensions
    return anchor_nodes


def findAnchorNode(lot_node, anchor_nodes):
    global price_delta, sqft_delta, metro_delta, grid_dim
    price_coord = lot_node.price // price_delta
    sqft_coord = lot_node.sqft // sqft_delta
    try:
        if metro_delta is not None:
            metro_coord = lot_node.distanceToMetro // metro_delta
            return anchor_nodes[get_anchor_code(price_coord, sqft_coord, metro_coord)]
        return anchor_nodes[get_anchor_code(price_coord, sqft_coord, 0)]
    except:
        if metro_delta is not None:
            metro_coord = lot_node.distanceToMetro // metro_delta
            # print(len(anchor_nodes.keys()))
            expand_anchor_grid(anchor_nodes, (
                max(price_coord, grid_dim[0]), max(sqft_coord, grid_dim[1]), max(metro_coord, grid_dim[2])))
            # print(len(anchor_nodes.keys()))
            return anchor_nodes[get_anchor_code(price_coord, sqft_coord, metro_coord)]
        expand_anchor_grid(anchor_nodes, (
            max(price_coord, grid_dim[0]), max(sqft_coord, grid_dim[1]), max(0, grid_dim[2])))
        return anchor_nodes[get_anchor_code(price_coord, sqft_coord, 0)]


def find_nearest_neighbors(starting_node, searching_node, k, neighbor_list, neighbor_counter, close_matches_list=[],
                           first_search=True, argv={}):
    # TODO - neighbor_counter needs to be updated simultaneously on all branches - should be by ref, not value
    start = time.time()
    global sqft_mult, metro_mult

    # assert starting_node.anchor_node  # verify the node has an anchor node

    if neighbor_counter < k:
        possible_new_neighbors = []

        # first, add the nodes at this level of recursion
        # [print(n) for n in searching_node.neighbors]
        # print(searching_node.neighbors[0][0].neighbors)
        immediate_neighbors = []
        if first_search:
            immediate_neighbors.append(starting_node.anchor_node)
            # print(starting_node.anchor_node.neighbors)
            for a_node in starting_node.anchor_node.neighbors:

                if type(a_node) is AnchorNode:
                    # print('Wooo anchor nodessss 4 dayzzz')
                    immediate_neighbors.append(a_node)
        else:
            immediate_neighbors.append(searching_node[0].anchor_node)

        # [print(n) for n in immediate_neighbors]

        for a_node in immediate_neighbors:
            for connected_node_tuple in a_node.neighbors:
                if type(connected_node_tuple) is LotNode and type(searching_node) is LotNode:
                    lot_tuple = connected_node_tuple, starting_node.getDistance(connected_node_tuple, sqft_mult,
                                                                                   metro_mult)
                    if lot_tuple not in searching_node.neighbors:
                        if argv == {}:

                            if connected_node_tuple[0].getDistance(starting_node, sqft_mult, metro_mult) \
                                    < searching_node.neighbors[-1][1]:
                                # replace furthest neighbor of the searching node with this new node, then sort

                                searching_node.neighbors[-1] = (starting_node,
                                                                connected_node_tuple[0].getDistance(starting_node,
                                                                                                    sqft_mult,
                                                                                                    metro_mult))
                                searching_node.sort(key=(lambda x: x[1]))

                            if lot_tuple not in possible_new_neighbors:
                                possible_new_neighbors.append(lot_tuple)
                                neighbor_counter[0] += 1

                        else:
                            if connected_node_tuple[0].matches_conditions(argv) == 0:
                                if lot_tuple not in possible_new_neighbors:
                                    possible_new_neighbors.append(lot_tuple)
                                    neighbor_counter[0] += 1

                            elif connected_node_tuple[0].matches_conditions(argv) == 1:
                                if lot_tuple not in close_matches_list:
                                    close_matches_list.append(lot_tuple)

        for next_node in possible_new_neighbors:
            find_nearest_neighbors(starting_node, next_node, k, neighbor_list, neighbor_counter, first_search=False)

        #print(possible_new_neighbors)
        neighbor_list += possible_new_neighbors

        neighbor_list.sort(key=(lambda x: x[1]))
        if len(neighbor_list) > k:
            neighbor_list = neighbor_list[0::k]

        end = time.time()

        print('Time elapsed in fancy search: ' + str(end - start) + 's')

        return neighbor_list


def add_node_to_database(node, k, anchor_nodes):
    # node.addNeighbor(findAnchorNode(node, anchor_nodes))  # add the anchor node
    node.setAnchor(findAnchorNode(node, anchor_nodes))
    findAnchorNode(node, anchor_nodes).addNeighbor(node)

    # add the neighbor nodes
    k_nearest_neighbors = find_nearest_neighbors(node, findAnchorNode(node, anchor_nodes), k, [], 0)
    for n in k_nearest_neighbors:
        node.addNeighbor(n)


def populate_database(k, lot_nodes, anchor_nodes, warmup_size=50, sample_size=10):
    global sqft_mult, metro_mult

    # node lists (anchor nodes need to be Random access, lot nodes theoretically don't - this is only used for
    # initialization

    # create set of grocery stores
    grocery_stores = createSet.populateGroceryStoreList()

    # create set of metro stops
    metro_stops = createSet.populateMetroList()

    # create set of schools
    schools = createSet.populateSchoolList()

    # create set of parks
    parks_and_playgrounds = createSet.populateParksandPlaygroundsList()

    file_loc = "https://raw.githubusercontent.com/andrewsavino1/HousingSearch/master/Data/missing_price.csv"

    price_list = pd.read_csv(file_loc)

    price_dict = dict(zip(price_list.Neighborhood, price_list.Price))
    # print(price_dict)

    # call convertToNode on every row of the data file
    callstr = os.getcwd() + '\\Data\\lra.geojson'
    file = geo.load(open(callstr))

    for dataline in file['features']:
        node = convertToNode(dataline, schools, parks_and_playgrounds, metro_stops, grocery_stores, price_dict)
        if node is not None:
            # node.setAnchor(anchor_nodes[get_anchor_code(node.price, node.sqft, node.distanceToMetro)])
            lot_nodes.append(node)
            # anchor_nodes[get_anchor_code(node.price, node.sqft, node.distanceToMetro)].addNeighbor(node)
        #if len(lot_nodes) > warmup_size:
        #    break

    # run warmupFill to start populating the database (split the list into 2 sublists, warm-up and all else (or just
    # pick an index to be the cutoff
    # print(len(lot_nodes))
    sqft_mult, metro_mult = warmupFill(lot_nodes[:warmup_size], anchor_nodes, k, warmup_size, sample_size)

    # do fill up everything else
    for node in lot_nodes[warmup_size:]:
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

    acreage_min_input = input("Enter a minimum acceptable square footage (or 'N' if not applicable): ")
    while not checkInt(acreage_min_input):
        print("Error. Square footage minimum must be an integer value.")
        acreage_min_input = input("Enter a minimum acceptable square footage (or 'N' if not applicable): ")

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
        family_input = input("Do you ish to search over empty lots? Y/N:  ")

    price_min = 0 if price_min_input == 'N' else int(str(price_min_input))
    price_max = 99999999 if price_max_input == 'N' else int(str(price_max_input))
    metro_dist = 99999999 if metro_dist_input == 'N' else int(str(metro_dist_input))
    acreage_min = 0 if acreage_min_input == 'N' else int(str(acreage_min_input))

    parking = True if str(parking_input) == "Y" else False
    grocery = True if str(grocery_input) == "Y" else False
    family = 0 if str(family_input) == "Y" else 99999
    property = True if str(property_input) == "Y" else False

    dummy_node = LotNode(0, '', price_min, acreage_min, 0, 0)
    dummy_node.setNearGrocery(grocery)
    dummy_node.setMetroDistance(metro_dist)
    dummy_node.setKidFriendly(family, family)

    argv = {
        'minPrice': price_min,
        'maxPrice': price_max,
        'vacant': property,
        'minSqft': acreage_min,
        'kidFriendly': family,
        'distanceToMetro': metro_dist,
        'grocery': grocery
    }

    return dummy_node, argv


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


def runIt():
    # parameters:
    k = 5
    anchor_nodes = {}

    lot_nodes = read_from_csv('housingData.csv')

    while True:
        neighbor_list = []
        close_matches = []
        neighbor_counter = 0

        dummy_node, argv = get_search_parameters()
        dummy_node.setAnchor(findAnchorNode(dummy_node, anchor_nodes))
        neighbors = find_nearest_neighbors(dummy_node, findAnchorNode(dummy_node, anchor_nodes), k, neighbor_list,
                                           neighbor_counter, close_matches, argv)
        neighbors_2 = iterativeSearch(lot_nodes, dummy_node, sqft_mult, metro_mult, k, argv)
        try:
            assert set(neighbors) == set(neighbors_2)
            print('Success! The lists returned by the iterative search and the nearest-neighbors search are identical.')
            [print(n[0]) for n in neighbors]
        except:
            print('Error: The lists returned by the iterative search and the nearest-neighbors search are different.')
            print('Nearest neighbor search results:')
            [print(n[0]) for n in neighbors]
            print('\nIterative search results:')
            [print(n[0]) for n in neighbors_2]


def populate_csv():
    k = 5
    lot_nodes = []
    anchor_nodes = {}
    populate_database(k, lot_nodes, anchor_nodes)
    print_to_csv(lot_nodes)


if __name__ == '__main__': populate_csv()
