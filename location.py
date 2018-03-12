class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str(self.x) + ' , ' + str(self.y)

    def getDistance(self, loc2):
        """return the Manhattan distance of 2 Locations"""
        return abs(loc2.x - self.x) + abs(loc2.y - self.y)


class GroceryStore(Location):
    def __init__(self, x, y):
        super(GroceryStore, self).__init__(x, y)


class MetroStop(Location):
    def __init__(self, x, y, name):
        super(MetroStop, self).__init__(x, y)
        self.name = name

