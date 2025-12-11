import json
import pandas as pd
import h3
import osmnx as ox
from shapely import Polygon, MultiPolygon

#presets to define 
SaveFile = "Urban_Features_Scraper.json "
dres = 7 #Default hex resolution for hex grabbing throughout the program
out_json = [] #structured as [ City1{h3-, properties{}} City2{h3-, properties{}}]

osm_tags = {
    # Counting/point or area features
    'leisure': ['park', 'garden', 'playground'],
    'amenity': [
        'parking',
        'bus_stop',
        'casino',
        'school',
        'library',
        'bicycle_parking',
        'place_of_worship'
    ],
    'building': True,
    'tourism': ['museum', 'hotel', 'motel'],
    'military': True,
    'landuse': ['farm'],
    'place_of_worship': True,
    'religion': ['christian', 'muslim'],
    'footway': 'sidewalk',
    'highway': ['primary', 'secondary', 'tertiary', 'residential', 'cycleway', 'path', 'track'],
    'cycleway': ['lane', 'track'],
    'natural': ['water', 'tree', 'grass'],
    'water': ['lake', 'river'],
    'waterway': ['river', "lake"],
    'railway': True,
    'grass': True,
    'museum': True,
    'subway': True,
    'sidewalk': True
}

#list of cities to iterate through
cities = {"New York City, NY",
        "Boston, MA",
        "Chicago, IL",
        "San Francisco, CA",
        "Miami, FL",
        "Washington DC",
        "Baltimore, MD",
        "Dallas, TX",
        "Houston, TX",
        "Atlanta, GA",
        "Los Angeles, CA",
        "Las Vegas, NV",
        "Philadelphia, PA",
        "Seattle, WA",
        "Tulsa, OK",
        "Los Angeles, CA",
        "Las Vegas, NV",
        "Richmond, VA",
        "Phoenix, AZ",
        "Philadelphia, PA"
        }





#main functions in iteration
def h3_filler(city_name, hexres = dres):
    """
    returns list of h3's that fill city boundary
    """

    def boundary_maker(city_name):
        #returns list of coordinates creating city boundary as nodes in a polygon

        gdf = ox.geocode_to_gdf(city_name)
        #creates data frame of subset polys

        boundary_polygon = gdf.geometry.union_all()

        #merges sub polys into perimeter if necessary
        if isinstance(boundary_polygon, Polygon):
            coords = list(boundary_polygon.exterior.coords)
        elif isinstance(boundary_polygon, MultiPolygon):
            coords = []
            for poly in boundary_polygon.geoms:
                coords.extend(list(poly.exterior.coords))

        
        return coords

    coords = boundary_maker(city_name)
    poly_data = h3.LatLngPoly([(coordinate[1], coordinate[0]) for coordinate in coords])
    fill_list = h3.polygon_to_cells(poly_data, hexres)

    return fill_list

def scrape_features(h3x, city_name):

    point_sample = {
        "city_name": city_name,
        "h3_index": h3x
    }

    # coords = h3.cell_to_latlng(h3x)

    concentrations = {
    #counting concentration
    'parks': 0,
    'parking areas': 0,
    'bus stops': 0,
    'museums': 0,
    'gardens': 0,
    'playgrounds': 0,
    'hotels': 0,
    'motels': 0,
    'libraries': 0,
    'worship-house':0,
    'bicycle parking': 0,
    'rail stations': 0,
    'trees': 0,

    }

    binConcentrations = {
    #length/size based items so these tags use a binary check for presence instead
    'sidewalks': 0,
    'highways': 0,
    'bike lanes': 0,
    'lakes': 0,
    'rivers': 0,
    'rail/subways': 0,
    }

    remap = {
                "parking": "parking areas",
                "footway":"sidewalks",
                "sidewalk":"sidewalks",
                "cycleway":"bike lanes",
                "garden": "gardens",
                "playground": 'playgrounds',
                "park": 'parks' ,
                "river": 'rivers',
                "temple": 'worship-house' ,
                "hotel": 'hotels',
                "motel": 'motels',
                "place_of_worship": 'worship-house',
                "library": 'libraries' ,
                "synagogue":'worship-house',
                "bicycle_parking": 'bicycle parking',
                "train_station": 'rail stations',
                "church": 'worship-house',
                "christian": 'worship-house',
                "buddhist": 'worship-house',
                "bus_station": 'bus stops',
                "tree": "trees",
                "subway_entrance": 'rail stations',
                'religion':'worship-house' ,
                'highway': 'highways' ,
                'museum': 'museums',
                'lake': "lakes",
                'subway': "subway",
                'muslim': 'worship-house',
                'hindu': 'worship-house',

                #building;yes
                " inn ":"motel",
                "Hotel": 'hotels',
                "Motel": 'motels',
                " Inn ": 'motels',
                "Museum": "museums",
                "Library": "libraries",
                "Church": 'worship-house',
                "mosque": 'worship-house',
                "Mosque": 'worship-house',
                "synagogue": 'worship-house',
                "Synagogue": 'worship-house',
                "temple": 'worship-house',
                "Temple":'worship-house',


        }

    def make_hex_poly(subhex):

        bounds = h3.cell_to_boundary(subhex)
        bounds_corrected = [(lng, lat) for lat, lng in bounds]
        bounds_corrected.append(bounds_corrected[0])
        poly = Polygon(bounds_corrected)

        return poly

    gdf = ox.features.features_from_polygon(make_hex_poly(h3x), osm_tags)

    def update_dicts():

        for _, row in gdf.iterrows():
            for key in osm_tags:
                val = row.get(key)

                if not pd.notnull(val):
                    continue
                # out.add((val,key))

                v1, v2 = val,key

                if v1 in {"parking", "footway", "cycleway",
                          "garden", "playground", "park", "river",
                           "temple","hotel", "motel", "place_of_worship",
                           "library", "synagogue", "bicycle_parking",
                           "train_station", "church", "christian", "buddhist",
                           "bus_station", "tree", "subway_entrance", "museum",
                           "lake", "river", "muslim"}:

                    update_key = remap[v1]


                    if update_key in concentrations:
                        concentrations[update_key] += 1
                    elif update_key in binConcentrations:
                        binConcentrations[update_key] = 1


                    if v1 in {"subway_entrance", "train_station" }:
                        binConcentrations['rail/subways'] = 1

                #extra check since some features can be labeled under buildings
                elif v2 == "building" and v1 == "yes":
                    name = row.get("name")
                    for i in ["hotel", "motel", " inn ", "museum", "library",
                              "Hotel", "Motel", " Inn ", "Museum", "Library"
                              "church", "Church", "mosque", "Mosque",
                              "Synagogue" "synagogue", "temple", "Temple"]:
                        if i in str(name):
                            update_key = remap[i]
                            if update_key in concentrations:
                                concentrations[update_key] += 1
                            elif update_key in binConcentrations:
                                binConcentrations[update_key] = 1
                            break


                elif v2 in {'religion', 'highway', 'place_of_worship',
                            'museum', "subway", "sidewalk"}:
                    if v1 == "no":
                        continue

                    update_key = remap[v2]

                    if update_key in concentrations:
                        concentrations[update_key] += 1
                    elif update_key in binConcentrations:
                        binConcentrations[update_key] = 1
                else:
                    continue

    update_dicts()

    point_sample.update(concentrations)
    point_sample.update(binConcentrations)
    return point_sample




#iterating through cities and the hexes within them
for city in cities:
    print(f"Scraping hexes in {city}")

    for hex_point in h3_filler(city):
        try:
            data = scrape_features(hex_point, city)
            out_json.append(data)
        except ox._errors.InsufficientResponseError:
            # print("")
            continue





#file saving
with open(SaveFile, 'w') as json_file:
        json.dump(out_json, json_file, indent=4)
        print("Complete")

print("All Data Successfully Scraped")







































# osm_value_to_concentration_key = {
#         'park': 'parks',
#         'garden': 'garden',
#         'playground': 'playgrounds',
#         'golf_course': 'golf course',
#         'parking': 'parking spots',
#         'bus_stop': 'bus stops',
#         'casino': 'casinos',
#         'school': 'schools',
#         'museum': 'museums',
#         'subway_entrance': 'subways',
#         'hotel': 'hotels',
#         'motel': 'motels',
#         'military': 'military buildings',
#         'library': 'libraries',
#         'bicycle_parking': 'bicycle parking',
#         'airport': 'airports',
#         'christian': 'church',
#         'muslim': 'mosque',
#         'jewish': 'other-worship-house',
#         'buddhist': 'other-worship-house',
#         'hindu': 'other-worship-house',
#         'farm': 'farm',
#         'water': 'lakes',     # handle natural=water as lakes
#         'lake': 'lakes',
#         'river': 'rivers',
#         'sidewalk': 'sidewalks',
#         'primary': 'highways',
#         'secondary': 'highways',
#         'tertiary': 'highways',
#         'motorway': 'highways',
#         'cycleway': 'bike lanes',
#         'path': 'bike lanes',
#         'footway': 'sidewalks',
#         'pedestrian': 'sidewalks',
#     }

#     # Keys to check OSMnx results

# osm_key_to_tagsn_list = {
#         'natural': osm_tags['natural'],
#         'leisure': osm_tags['leisure'],
#         'amenity': osm_tags['amenity'],
#         'highway': osm_tags['highway'],
#         'building': osm_tags['building'],
#         'religion': osm_tags['religion'],
#         'water': [True],
#     }
