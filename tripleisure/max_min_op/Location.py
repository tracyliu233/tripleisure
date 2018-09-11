"""
Location.py: Class representation of a location from database
Mark Lubin
"""

import os

import psycopg2

UNAME = "tracy"
PWD = ''
HOST = "localhost"
DBNAME = "tracy"

try:
    DB_CONNECT = os.environ["DATABASE_URL"]
    UNAME = DB_CONNECT.split(':')[1][2:]
    PWD, HOST = DB_CONNECT.split(':')[2].split("@")
    DBNAME = DB_CONNECT.split(':')[3].split("/")[1]
except KeyError:
    pass


class LocationError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Locations:
    def __init__(self):
        # a list of locations
        self.locations = {}
        cn = psycopg2.connect(user=UNAME, password=PWD, host=HOST, dbname=DBNAME)
        cr = cn.cursor()
        cr.execute("SELECT location_id, latitude, longitude, placename, importance, duration FROM YELP_SIGHTSEEING")

        for lid, lat, lng, name, imp, duration in cr.fetchall():
            self.locations[lid] = Location(lid, float(lat), float(lng), name, float(imp), float(duration))

    def __iter__(self):
        for lid in self._locations:
            yield self._locations[lid]

    def asIds(self):
        return self.locations.keys()

    def get_locations_attributes(self):
        loc_attributes = []
        for lid in self.locations:
            lat, long = self.locations[lid].getLatLong()
            importance = self.locations[lid].getImportance()
            duration = self.locations[lid].getDuration()
            loc_attributes.append((lid, lat, long, importance, duration))
        return loc_attributes

    def getLocations(self):
        locs = []#dictionary of location information
        for loc in self.locations:
            latlong = self.locations[loc].getLatLong()
            name = self.locations[loc].getPlacename()
            locs.append({"id"       : loc,
                         "latitude" : latlong[0],
                         "longitude": latlong[1],
                         "name"     : name})
        return locs

    def remove_location(self, lid):
        del self.locations[lid]

    def placenameForLocation(self, lid):
        if not lid in self.locations.keys():
            raise LocationError("No location for ID: %d" % lid)
        return self.locations[lid].getPlacename()

    def coordsForLocation(self, lid):
        if not lid in self.locations.keys():
            raise LocationError("No location for ID: %d" % lid)
        return self.locations[lid].getLatLong()

    def importanceForLocation(self, lid):
        if not lid in self.locations.keys():
            raise LocationError("No location for ID: %d" % lid)
        return self.locations[lid].getImportance()

    def durationForLocation(self, lid):
        return self.locations[lid].getDuration()
        # def gcdForLocations(self,lid1,lid2):#distance between two locations
        #     return greatCircleDistance(self.coordsForLocation(lid1),self.coordsForLocation(lid2))


class Location:
    def __init__(self, lid, lat, lng, placename, importance, duration):  # build a new location given this id num
        self._lat = lat
        self._lng = lng
        self._placename = placename
        self._lid = lid
        self._importance = importance
        self._duration = duration
        self._successors = []

    def getLatLong(self): return self._lat, self._lng

    def getPlacename(self): return self._placename

    def getImportance(self): return self._importance

    def getDuration(self): return self._duration

    def getSuccessors(self):
        if not self._successors:  # load up the list on the fly if we need it
            cn = psycopg2.connect(DB_CONNECT)
            cr = cn.cursor()
            cr.execute("SELECT dest_id FROM edges WHERE source_id = (%s) AND prob > 0.0", (self._lid,))
            [self._successors.append(row[0]) for row in cr.fetchall()]
        return self._successors
