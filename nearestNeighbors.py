import json
import node


def convertToNode():
    # TODO getData

    # TODO
    price = 0
    sqft = 0
    distanceToMetro = 0
    id = 12345
    address = "25 Kings Court"
    centerX = 45
    centerY = 90
    n = node.Node(id, address, price, sqft, distanceToMetro, centerX, centerY)
    return n


def warmupFill(numInitialNodes=100):
    # TODO
    x = 1


def run():
    # TODO
    x = 1


print(convertToNode())