from location import *

# threshold distances
grocery_distance_threshold = 0.3
dist_school_threshold = 0.3
dist_park_threshold = 0.3

# generic node object
# contains a list of neighbors
class Node:
    def __init__(self, id_):
        self.id = id_
        self.neighbors = []  # this will be a list of (node, distance_to_node)

    def __hash__(self):
        return self.id

    def addNeighbor(self, node):
        self.neighbors.append(node)

    def hasNeighbor(self, node):
        return True if node in self.neighbors else False


# lotnode object
# used to store information for houses/lots
class LotNode(Node):
    def __init__(self, id_, address, price, sqft, centerX, centerY, hasParkingSpot=False,
                 vacant=False):
        super(LotNode, self).__init__(id_)

        # continuous variables
        self.price = price
        self.sqft = sqft
        self.distanceToMetro = None

        # binary variables
        self.hasParkingSpot = hasParkingSpot
        self.nearGrocery = False
        self.kidFriendly = False
        self.vacant = vacant

        # geographical identifying info
        self.location = Location(centerX, centerY)
        self.zipCode = ""
        self.address = address

        # nearest neighbors:
        self.numNeighbors = 0  # use this to limit the number of nearest neighbors to k

        # Anchor node
        self.anchor_node = None


    def __str__(self):
        return (self.address + '\n\tPrice: ' + str(self.price) + '\n\tsqft: ' + str(self.sqft)
                + '\n\tDistance to Metro: ' + str(self.distanceToMetro))

    def addNeighbor(self, node_tuple):
        self.neighbors.append(node_tuple)
        self.numNeighbors += 1

    def setAnchor(self, anchor):
        self.anchor_node = anchor

    # get 'distance' from another node, where the difference in attributes is scaled to be
    # an equivalent difference in price. See modified Euclidean distance in the presentation
    # or check the warmupFill method in nearestNeighbors.py
    def getDistance(self, node2, sqft_mult, metro_mult):
        return ((self.price - node2.price) ** 2 + (sqft_mult*(self.sqft - node2.sqft)) ** 2 +
                (metro_mult*(self.distanceToMetro - node2.distanceToMetro)) ** 2) ** 0.5

    def setMetroDistance(self, dist):
        self.distanceToMetro = dist

    def setNearGrocery(self, dist):
        if dist < grocery_distance_threshold:
            self.nearGrocery = True

    def setKidFriendly(self, dist_school, dist_park):
        if dist_school < dist_school_threshold and dist_park < dist_park_threshold:
            self.kidFriendly = True

    def setKidFriendly_known(self, kf_bool):
        self.kidFriendly = kf_bool

    def setNearGrocery_known(self, groc_bool):
        self.nearGrocery = groc_bool

    # given a query argv, check how many conditions this lotnode violates
    # used to determine if the property can be an exact match or a close match
    def matches_conditions(self, argv):
        ctr = 0
        ctr += 1 if self.price < argv['minPrice'] or self.price > argv['maxPrice'] else 0
        ctr += 1 if self.sqft < argv['minSqft'] else 0
        ctr += 1 if self.distanceToMetro > argv['distanceToMetro'] else 0
        ctr += 1 if not self.kidFriendly and argv['kidFriendly'] else 0
        ctr += 1 if (argv['grocery'] and not self.nearGrocery) else 0
        ctr += 2 if self.vacant and not argv['vacant'] else 0  # if it's vacant and shouldn't be then it's not a near match
        return ctr


# class for anchor nodes
class AnchorNode(Node):
    def __init__(self, id_):
        super(AnchorNode, self).__init__(id_)

    def __str__(self):
        return 'Anchor Node with ' + str(len(self.neighbors)) + ' neighbors.'
