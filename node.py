from location import *


class Node:
    def __init__(self, id_, address, price, sqft, centerX, centerY, hasParkingSpot=False,
                 vacant=False):
        # continuous variables
        self.price = price
        self.sqft = sqft
        self.distanceToMetro = self.getMetroDistance(self.location)

        # binary variables
        self.hasParkingSpot = hasParkingSpot
        self.nearGrocery = nearGrocery
        self.kidFriendly = kidFriendly
        self.vacant = vacant

        # position in graph:

        # TODO - delete these later possibly
        self.centerX = centerX
        self.centerY = centerY

        self.location = Location(centerX, centerY)
        self.zipCode = ""
        self.address = address

        # identifying info
        self.id = id_

    def __str__(self):
        return (self.address + '\n\tPrice: ' + str(self.price) + '\n\tsqft: ' + str(self.sqft)
                + '\n\tDistance to Metro: ' + str(self.distanceToMetro))

    def __hash__(self):
        return self.id

    def getDistance(self, node2):
        # TODO get the multipliers for the modified Euclidian space
        return ((self.price-node2.price)**2 + (self.sqft-node2.sqft)**2 +
                (self.distanceToMetro-node2.distanceToMetro)**2) ** 0.5

    def getMetroDistance(self, metro):
        return MetroStop.getDistance(metro)


