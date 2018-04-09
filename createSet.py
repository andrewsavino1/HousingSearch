from location import *
import geojson as geo
import os

metro_raw_coordinates = [(38.6279026,-90.1925076,'8th & Pine'),
                         (38.5218998,-89.9744728,'Belleville'),
                         (38.6284464,-90.3379964,'Brentwood I-64'),
                         (38.6359936,-90.2624496,'Central West End'),
                         (38.624924,-90.2031208,'Civic Center'),
                         (38.6425518,-90.3237263,'Clayton'),
                         (38.7503222,-90.3754521,'College'),
                         (38.6303768,-90.1894267,'Convention Center'),
                         (38.6556873,-90.2944808,'Delmar Loop'),
                         (38.628508,-90.174753,'East Riverfront'),
                         (38.6288877,-90.1369647,'Emerson Park'),
                         (38.5936153,-90.0478052,'Fairview Heights'),
                         (38.6477913,-90.2846397,'Forest Park–DeBaliviere'),
                         (38.648927,-90.32814,'Forsyth'),
                         (38.6294781,-90.2352184,'Grand'),
                         (38.6233025,-90.1245416,'Jackie Joyner-Kersee Center'),
                         (38.6294675,-90.1840211,'Lacledes Landing'),
                         (38.7412264,-90.3646442,'Lambert Airport Terminal 1'),
                         (38.7363594,-90.3563864,'Lambert Airport Terminal 2'),
                         (38.6137789,-90.3312379,'Maplewood–Manchester'),
                         (38.557573,-90.015361,'Memorial Hospital'),
                         (38.7199726,-90.3156641,'North Hanley'),
                         (38.635142,-90.342339,'Richmond Heights'),
                         (38.6852819,-90.3014893,'Rock Road'),
                         (38.5388425,-89.8790235,'Shiloh–Scott'),
                         (38.593671,-90.3194855,'Shrewsbury–Lansdowne I-44'),
                         (38.6492024,-90.300566,'Skinker'),
                         (38.623407,-90.194543,'Stadium'),
                         (38.607588,-90.3302138,'Sunnen'),
                         (38.5361464,-89.9873452,'Swansea'),
                         (38.7130957,-90.3065649,'UMSL North'),
                         (38.7053325,-90.3052106,'UMSL South'),
                         (38.629174,-90.207592,'Union Station'),
                         (38.6517126,-90.31533,'University City–Big Bend'),
                         (38.6137168,-90.0952038,'Washington Park'),
                         (38.669179,-90.2983697,'Wellston')
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
    callstr = os.getcwd() + '\\Data\\PrivateSchool.geojson'
    private_school_data = geo.load(open(callstr))
    for school in private_school_data["features"]:
        schools.append(allSchools(school["properties"]["X"], school["properties"]["Y"]))

    callstr = os.getcwd() + '\\Data\\PublicCharterSchool.geojson'
    charter_school_data = geo.load(open(callstr))
    for school in charter_school_data["features"]:
        schools.append(allSchools(school["properties"]["X"], school["properties"]["Y"]))

    return schools


def populateParksandPlaygroundsList():
    p_and_p = []
    callstr = os.getcwd() + '\\Data\\Playgrounds.geojson'
    playgrounds_data = geo.load(open(callstr))
    for ground in playgrounds_data["features"]:
        p_and_p.append(grounds(ground["properties"]["x_coordina"], ground["properties"]["y_coordina"]))

    return p_and_p

