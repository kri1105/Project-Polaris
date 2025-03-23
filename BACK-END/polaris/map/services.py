import requests
from django.conf import settings
from math import radians, sin, cos, sqrt, atan2
import logging

# logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def haversine(lat1, lon1, lat2, lon2):
    """
    Distance between two points 
    """
    R = 6371  
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  

def geocode_location(location_name):
    """
    Convert location name to coordinates using Graphhopper's Geocoding API.
    """
    endpoint = "https://graphhopper.com/api/1/geocode"
    params = {
        "q": location_name, 
        "limit": 1,  
        "key": settings.GRAPH_HOPPER_API_KEY,  
    }
    
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('hits'):
            logger.error(f"No results found for location: {location_name}")
            return None  
            
        first_result = data['hits'][0]
        logger.debug(f"Geocoded location '{location_name}' to coordinates: {first_result['point']['lat']}, {first_result['point']['lng']}")
        return {
            "lat": first_result['point']['lat'],
            "lon": first_result['point']['lng'],
            "display_name": first_result.get('name', location_name),
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error geocoding location '{location_name}': {e}")
        return {"error": str(e)}

def get_car_route(start_lat, start_lng, end_lat, end_lng):
    """
    Fetch optimal car route from Graphhopper Directions API.
    """
    endpoint = "https://graphhopper.com/api/1/route"
    params = {
        "point": [f"{start_lat},{start_lng}", f"{end_lat},{end_lng}"],
        "vehicle": "car",  
        "locale": "en", 
        "key": settings.GRAPH_HOPPER_API_KEY,  
        "instructions": True,  
        "calc_points": True, 
        "points_encoded": False  
    }
    
    try:
        # Make the API request
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        # Check if the response contains valid route data
        if 'paths' not in data or not data['paths']:
            logger.error("No route found")
            return {"error": "No route found"}
        
        # Extract relevant route information
        route = data['paths'][0]
        logger.debug(f"Car route from ({start_lat}, {start_lng}) to ({end_lat}, {end_lng}) is {route['distance']} meters and will take {route['time']} milliseconds")
        return {
            "distance": route['distance'],  # Distance in meters
            "time": route['time'] / 1000,  # Time in seconds (Graphhopper returns time in milliseconds)
            "instructions": route['instructions'],  # Turn-by-turn instructions
            "points": route['points'],  # Geometry of the route
            "paths": [{
                "points": {
                    "coordinates": route['points']['coordinates']  # Latitude/longitude pairs
                }
            }]
        }
        
    except requests.exceptions.RequestException as e:
        # Handle request errors
        logger.error(f"Error fetching car route: {e}")
        return {"error": str(e)}

def get_train_stations():
    """
    Fetch a list of train stations with their names, codes, and coordinates.
    This can be replaced with an API call or a database query.
    """
    # Example static data (replace with actual API or database call)
    stations = [
        {"name": "Potheri", "code": "POI", "lat": 12.8236, "lon": 80.0444},
        {"name": "Guindy", "code": "GY", "lat": 13.0067, "lon": 80.2206},
        {"name": "Chennai Central", "code": "MAS", "lat": 13.0827, "lon": 80.2707},
        {"name": "Chennai Fort", "code": "MSF", "lat": 13.0832, "lon": 80.2826},
        {"name": "Chennai Park", "code": "MPK", "lat": 13.0795, "lon": 80.2700},
        {"name": "Chennai Egmore", "code": "MS", "lat": 13.0771, "lon": 80.2616},
        {"name": "Mambalam", "code": "MBM", "lat": 13.0346, "lon": 80.2209},
        {"name": "Tambaram", "code": "TBM", "lat": 12.9249, "lon": 80.1275},
        {"name": "Velachery", "code": "VLCY", "lat": 12.9763, "lon": 80.2182},
        {"name": "Perambur", "code": "PER", "lat": 13.1165, "lon": 80.2337},
        {"name": "St. Thomas Mount", "code": "STM", "lat": 13.0033, "lon": 80.2000},
        {"name": "Avadi", "code": "AVD", "lat": 13.1147, "lon": 80.1018},
        {"name": "Villivakkam", "code": "VLK", "lat": 13.1140, "lon": 80.2100},
        {"name": "Tiruvallur", "code": "TRL", "lat": 13.1439, "lon": 79.9086},
        {"name": "Tirusulam", "code": "TLM", "lat": 12.9695, "lon":  80.1704},
        {"name": "Kattangulathur", "code": "CTM", "lat": 12.8280, "lon": 80.0460},
        {"name": "Maraimalai Nagar", "code": "MMNK", "lat": 12.7480, "lon": 80.0280},
        {"name": "Singaperumal Koil", "code": "SK", "lat": 12.7460, "lon": 80.0280},
        {"name": "Paranur", "code": "PWU", "lat": 12.7100, "lon": 80.0150},
        {"name": "Chengalpattu Junction", "code": "CGL", "lat": 12.6870, "lon": 79.9820}
    ]
    return stations

def get_nearest_station(lat, lon, stations):
    """
    Find the nearest train station from a given latitude and longitude.
    """
    nearest_station = None
    min_distance = float('inf')
    
    for station in stations:
        station_lat = station['lat']
        station_lon = station['lon']
        distance = haversine(lat, lon, station_lat, station_lon)
        if distance < min_distance:
            min_distance = distance
            nearest_station = station
    
    return nearest_station

def get_multi_modal_route(start_lat, start_lng, end_lat, end_lng):
    """
    Get a multi-modal route combining car and train.
    Automatically calculates the nearest stations for start and destination.
    """
    # Fetch train stations
    stations = get_train_stations()
    if not stations:
        return {"error": "No train stations available"}
    
    # Find nearest stations
    start_station = get_nearest_station(start_lat, start_lng, stations)
    end_station = get_nearest_station(end_lat, end_lng, stations)
    
    if not start_station or not end_station:
        return {"error": "Could not find nearest stations"}
    
    # Get car routes
    car_route_start = get_car_route(start_lat, start_lng, start_station['lat'], start_station['lon'])
    car_route_end = get_car_route(end_station['lat'], end_station['lon'], end_lat, end_lng)
    if 'error' in car_route_start:
        return car_route_start
    if 'error' in car_route_end:
        return car_route_end
    
    # Get train route (NEWLY ADDED)
    train_route = get_train_route(start_station, end_station)
    if 'error' in train_route:
        return train_route
    
    # Combine all segments
    return {
        "start_address": f"Start: {start_lat}, {start_lng}",
        "end_address": f"End: {end_lat}, {end_lng}",
        "distance": car_route_start['distance'] + train_route['distance'] + car_route_end['distance'],
        "time": car_route_start['time'] + train_route['time'] + car_route_end['time'],
        "instructions": [
            *car_route_start['instructions'],
            {"text": f"Take train from {start_station['name']} to {end_station['name']} ({train_route['distance']/1000:.1f} km)"},
            *car_route_end['instructions']
        ],
        "paths": [
            *car_route_start['paths'],
            {"points": {"coordinates": train_route['points']['coordinates']}},
            *car_route_end['paths']
        ]
    }

# Add this function to calculate train distance/time (example)
def get_train_route(start_station, end_station):
    # Calculate straight-line distance using Haversine
    distance_km = haversine(
        start_station['lat'], start_station['lon'],
        end_station['lat'], end_station['lon']
    )
    # Estimate time at average 50 km/h (customize this)
    time_hr = distance_km / 60
    return {
        "distance": distance_km * 1000,  # meters
        "time": time_hr * 3600,  # seconds
        "points": {
            "coordinates": [
                [start_station['lon'], start_station['lat']],
                [end_station['lon'], end_station['lat']]
            ]
        }
    }