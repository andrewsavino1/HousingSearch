from location import *
import geojson as geo
import os

metro_raw_coordinates = [(38.6530377, -90.3140165, 'East RiverfrontStation'),
                         (38.6530377, -90.3140165, 'Arch-Lachledes Landing'),
                         (38.6530377, -90.3140165, 'Convention Center'),

                            # TODO - add in the other metro coordinates

                         ]


def populateMetroList():
    metro_stops = []
    for (x, y, name) in metro_raw_coordinates:
        metro_stops.append(MetroStop(x, y, name))
    return metro_stops


def populateGroceryStoreList():
    grocery_stores = []
    callstr = os.getcwd() + '\\Data\\GroceryStores.geojson'
    print(callstr)
    stores_data = geo.load(open(callstr))
    for store in stores_data["features"]:
        grocery_stores.append(GroceryStore(store["properties"]["X"], store["properties"]["Y"]))
    return grocery_stores


def populateSchoolList():
    schools = []
    # TODO

    return schools


def populateParksandPlaygroundsList():
    p_and_p = []

    # TODO

    return p_and_p

#populateGroceryStoreList()
