from location import *
import geojson as geo
import os

metro_raw_coordinates = [(38.6530377, -90.3140165, 'East RiverfrontStation'),
                         (38.6530377, -90.3140165, 'Arch-Lachledes Landing'),
                         (38.6530377, -90.3140165, 'Convention Center'),

                            # TODO - add in the other metro coordinates

                         ]
metro_stops = []
grocery_stores = []
schools = []


def populateMetroList():
    for (x, y, name) in metro_raw_coordinates:
        metro_stops.append(MetroStop(x, y, name))


def populateGroceryStoreList():
    callstr = os.getcwd() + '\\Data\\GroceryStores.geojson'
    print(callstr)
    stores_data = geo.load(open(callstr))
    for store in stores_data["features"]:
        grocery_stores.append(GroceryStore(store["properties"]["X"], store["properties"]["Y"]))



populateGroceryStoreList()
