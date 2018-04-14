from location import *

# threshold distances for
grocery_distance_threshold = 0.3
dist_school_threshold = 0  # TODO
dist_park_threshold = 0  # TODO


class Node:
    def __init__(self, id_):
        self.id = id_
        self.neighbors = []  # this will be a list of (node, distance_to_node)

    def __hash__(self):
        return self.id

    def addNeighbor(self, node):
        self.neighbors.append((node, 0))


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
        self.neighbors.append(self, node_tuple)

    def hasNeighbor(self, node):
        return True if node in self.neighbors else False

    def setAnchor(self, anchor):
        self.anchor_node = anchor

    def getDistance(self, node2, sqft_mult, metro_mult):
        return ((self.price - node2.price) ** 2 + (sqft_mult*(self.sqft - node2.sqft)) ** 2 +
                (metro_mult*(self.distanceToMetro - node2.distanceToMetro)) ** 2) ** 0.5

    def setMetroDistsance(self, dist):
        self.distanceToMetro = dist

    def setNearGrocery(self, dist):
        if dist < grocery_distance_threshold:
            self.nearGrocery = True

    def setKidFriendly(self, dist_school, dist_park):
        if dist_school < dist_school_threshold and dist_park < dist_park_threshold:
            self.kidFriendly = True

    def matches_conditions(self, argv):
        # TODO - argv is a list of the conditions the search requires (including continuous variables)
        # return the number of conditions matched (so easier to do "nar"
        return 0


class AnchorNode(Node):
    def __init__(self, id_):
        super(AnchorNode, self).__init__(id_)
