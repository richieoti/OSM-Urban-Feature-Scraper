Python file to scrape the concentration/presence of urban features in a city based on Uber's h3 hexagons using OpenStreetMap. 

Formats the data as a JSON that can be used for pattern recognition in city feature concentrations.

Example entry for an h3 hexagon in Baltimore:

[...
    {
        "city_name": "Baltimore, MD",
        "h3_index": "872aa8c0affffff",
        "parks": 4,
        "parking areas": 19,
        "bus stops": 0,
        "museums": 0,
        "gardens": 1,
        "playgrounds": 4,
        "hotels": 0,
        "motels": 0,
        "libraries": 0,
        "worship-house": 21,
        "bicycle parking": 0,
        "rail stations": 0,
        "trees": 0,
        "sidewalks": 1,
        "highways": 1,
        "bike lanes": 0,
        "lakes": 0,
        "rivers": 0,
        "rail/subways": 0
    },
    ...
    
