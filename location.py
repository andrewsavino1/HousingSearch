# FILENAME: location.py

# location class to make objects for metro stops / grocery stores / etc
class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str(self.x) + ' , ' + str(self.y)

    def getDistance(self, loc2):
        multiplier = 0.261  # - distance multiplier for manhattan distance
        """return the Manhattan distance of 2 Locations"""
        return abs(loc2.x - self.x)*multiplier + abs(loc2.y - self.y)


class GroceryStore(Location):
    def __init__(self, x, y):
        super(GroceryStore, self).__init__(x, y)


class MetroStop(Location):
    def __init__(self, x, y, name):
        super(MetroStop, self).__init__(x, y)
        self.name = name

    def __str__(self):
        return self.name

class allSchools(Location):
    def __init__(self, x, y):
        super(allSchools, self).__init__(x, y)


class grounds(Location):
    def __init__(self, x, y):
        super(grounds, self).__init__(x, y)
