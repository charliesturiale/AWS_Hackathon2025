# -*- coding: utf-8 -*-
"""
SafePath Backend - FastAPI Application
Provides route safety analysis using real-time SF crime and 311 data
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
from contextlib import asynccontextmanager
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import requests
import asyncio
import time

try:
    from .data_fetcher import DataSFetcher
    from .risk_scorer import RiskScorer
except ImportError:
    from data_fetcher import DataSFetcher
    from risk_scorer import RiskScorer
import math
from geopy.distance import geodesic
import numpy as np

# Load environment variables
load_dotenv()

# Initialize services (module-level)
data_fetcher = DataSFetcher()
risk_scorer = RiskScorer()
scheduler = BackgroundScheduler()

# Reverse geocoding cache to prevent repeated API calls for same coordinates
reverse_geocode_cache: Dict[str, str] = {}
# Forward geocoding cache to prevent repeated API calls for same addresses
geocode_cache: Dict[str, Optional[Dict[str, float]]] = {}
last_geocode_request_time = 0.0

# Rate limiting: Semaphore to limit concurrent geocoding requests (prevents API overload)
geocode_semaphore = asyncio.Semaphore(2)  # Max 2 concurrent geocoding requests


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 40)
    print("Starting SafePath Backend...")
    print("=" * 40)

    # Initial data fetch
    print("Fetching initial incident data...")
    data_fetcher.fetch_all_data()

    # Schedule periodic updates (every 10 minutes)
    interval_minutes = int(os.getenv("DATA_REFRESH_INTERVAL", 10))
    scheduler.add_job(
        periodic_data_fetch,
        'interval',
        minutes=interval_minutes,
        id='fetch_data',
        replace_existing=True
    )
    scheduler.start()
    print(f"Scheduled data updates every {interval_minutes} minutes")
    print(f"SafePath Backend ready!")

    yield

    # Shutdown
    scheduler.shutdown()
    print("SafePath Backend shutting down...")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="SafePath API",
    description="Real-time route safety analysis for San Francisco",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphHopper configuration
GRAPHHOPPER_API_KEY = os.getenv("GRAPHHOPPER_API_KEY", "72974d83-39d7-4a65-95eb-4440960fde46")
GEOCODING_URL = "https://graphhopper.com/api/1/geocode"
ROUTING_URL = "https://graphhopper.com/api/1/route"


# Pydantic Models
class RouteRequest(BaseModel):
    """Request model for route calculation"""
    origin: str
    destination: str


class CoordinatePair(BaseModel):
    """Lat/Lng coordinate pair"""
    lat: float
    lng: float


class RouteAnalysis(BaseModel):
    """Analysis result for a single route"""
    id: int
    name: str
    description: str
    distance: str
    time: str
    safetyScore: int
    total_risk: float
    crime_risk: float
    incident_risk: float
    coordinates: List[CoordinatePair]
    color: str


class RoutesResponse(BaseModel):
    """Response with analyzed routes"""
    routes: List[RouteAnalysis]
    originCoords: CoordinatePair
    destCoords: CoordinatePair
    data_timestamp: str


# Validation Helper Functions
def validate_coordinates(lat: float, lng: float) -> bool:
    """
    Validate latitude and longitude values
    Returns True if valid, False otherwise
    """
    try:
        # Check if values are numeric
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            return False

        # Check if values are within valid ranges
        # Latitude: -90 to 90
        # Longitude: -180 to 180
        if not (-90 <= lat <= 90):
            return False
        if not (-180 <= lng <= 180):
            return False

        # Check for NaN or infinity
        if math.isnan(lat) or math.isnan(lng):
            return False
        if math.isinf(lat) or math.isinf(lng):
            return False

        return True
    except:
        return False


def safe_print(message: str):
    """
    Safe print function that handles Windows console encoding issues
    Prevents [Errno 22] Invalid argument on Windows systems
    """
    try:
        print(message)
    except Exception as e:
        # Fallback: encode to ASCII, ignoring errors
        try:
            print(message.encode('ascii', 'ignore').decode('ascii'))
        except:
            pass  # Silently fail if all else fails


# Helper Functions
async def reverse_geocode(lat: float, lng: float) -> str:
    """
    Convert coordinates to street intersection or address using GraphHopper.
    Implements caching and rate limiting to prevent API overuse.
    """
    global last_geocode_request_time

    # Validate coordinates first to prevent errors
    if not validate_coordinates(lat, lng):
        safe_print(f"Invalid coordinates for reverse geocoding: lat={lat}, lng={lng}")
        return f"{lat:.4f}, {lng:.4f}"

    # Create cache key with rounded coordinates (to 4 decimal places = ~11m precision)
    cache_key = f"{lat:.4f},{lng:.4f}"

    # Check cache first
    if cache_key in reverse_geocode_cache:
        return reverse_geocode_cache[cache_key]

    try:
        # Rate limiting: ensure at least 1 second between requests (1 req/sec)
        current_time = time.time()
        time_since_last = current_time - last_geocode_request_time
        if time_since_last < 1.0:
            await asyncio.sleep(1.0 - time_since_last)

        last_geocode_request_time = time.time()

        # Make API request
        response = requests.get(
            f"{GEOCODING_URL}?point={lat},{lng}&key={GRAPHHOPPER_API_KEY}&reverse=true&locale=en",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        result = f"{lat:.4f}, {lng:.4f}"  # Default fallback

        if data.get("hits") and len(data["hits"]) > 0:
            hit = data["hits"][0]
            street = hit.get("street", "")
            house_number = hit.get("housenumber", "")

            if street:
                if house_number:
                    result = f"{house_number} {street}"
                else:
                    result = street
            elif hit.get("name"):
                result = hit["name"]

        # Cache the result
        reverse_geocode_cache[cache_key] = result
        return result

    except Exception as e:
        # On error, cache the coordinate string so we don't retry failed lookups
        result = f"{lat:.4f}, {lng:.4f}"
        reverse_geocode_cache[cache_key] = result
        if "429" not in str(e):  # Don't spam logs with rate limit errors
            print(f"Reverse geocoding error for {cache_key}: {e}")
        return result


#  Geometric Helper Functions for Route Optimization

def calculate_bearing(point1: tuple, point2: tuple) -> float:
    """Calculate bearing between two points in degrees"""
    lat1, lng1 = math.radians(point1[0]), math.radians(point1[1])
    lat2, lng2 = math.radians(point2[0]), math.radians(point2[1])

    d_lng = lng2 - lng1
    x = math.sin(d_lng) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lng)

    bearing = math.atan2(x, y)
    return (math.degrees(bearing) + 360) % 360


def destination_point(origin: tuple, bearing: float, distance_km: float) -> tuple:
    """Calculate destination point given origin, bearing, and distance"""
    R = 6371  # Earth radius in km
    lat1, lng1 = math.radians(origin[0]), math.radians(origin[1])
    bearing_rad = math.radians(bearing)

    lat2 = math.asin(math.sin(lat1) * math.cos(distance_km / R) +
                     math.cos(lat1) * math.sin(distance_km / R) * math.cos(bearing_rad))

    lng2 = lng1 + math.atan2(math.sin(bearing_rad) * math.sin(distance_km / R) * math.cos(lat1),
                             math.cos(distance_km / R) - math.sin(lat1) * math.sin(lat2))

    return (math.degrees(lat2), math.degrees(lng2))


def inject_waypoint_offline(route_coords: List[tuple], segment_start_idx: int,
                           segment_end_idx: int, safe_waypoint: tuple,
                           search_radius_km: float = 0.5) -> List[tuple]:
    """
    Inject waypoint into route by finding nearby existing route points (OFFLINE - no API calls).
    Uses existing coordinates as anchors to maintain road-like paths.
    IMPROVED: Better anchor search and path reconstruction to avoid straight lines.

    Args:
        route_coords: Full route coordinate list
        segment_start_idx: Index of problematic segment start
        segment_end_idx: Index of problematic segment end
        safe_waypoint: Calculated safe waypoint coordinate
        search_radius_km: Search radius for existing route points (default 500m)

    Returns:
        New route coordinates with waypoint injected
    """
    # Strategy 1: Find existing route points near the safe waypoint (EXPANDED RADIUS)
    candidates = []
    for idx in range(len(route_coords)):
        # Skip problematic segment and immediate neighbors
        if abs(idx - segment_start_idx) <= 2 or abs(idx - segment_end_idx) <= 2:
            continue

        coord = route_coords[idx]
        dist_to_waypoint = geodesic(coord, safe_waypoint).kilometers

        if dist_to_waypoint <= search_radius_km:
            # Calculate detour penalty (how far off the straight path)
            start_point = route_coords[segment_start_idx]
            end_point = route_coords[segment_end_idx]
            direct_dist = geodesic(start_point, end_point).kilometers
            detour_dist = geodesic(start_point, coord).kilometers + geodesic(coord, end_point).kilometers
            detour_penalty = detour_dist - direct_dist

            candidates.append({
                'idx': idx,
                'coord': coord,
                'dist_to_waypoint': dist_to_waypoint,
                'detour_penalty': detour_penalty
            })

    if candidates:
        # Sort by detour penalty (prefer routes that don't add too much distance)
        candidates.sort(key=lambda x: x['detour_penalty'])
        best = candidates[0]
        best_idx = best['idx']
        best_coord = best['coord']

        print(f"      Found anchor point at index {best_idx} ({best['detour_penalty']*1000:.0f}m detour)")

        # Create detour path through existing route point
        before = route_coords[:segment_start_idx]
        after = route_coords[segment_end_idx + 1:]

        # Use actual route segment as detour (maintains road structure)
        if best_idx < segment_start_idx:
            # Detour backwards through earlier part of route
            detour = route_coords[best_idx:segment_start_idx + 1]
        elif best_idx > segment_end_idx:
            # Detour forwards through later part of route
            detour = route_coords[segment_end_idx:best_idx + 1]
        else:
            # Should not happen due to skip logic, but handle safely
            detour = [best_coord]

        return before + detour + after
    else:
        # Strategy 2: No suitable anchor - keep original segment (safer than interpolation)
        print(f"      No anchor found within {search_radius_km*1000:.0f}m, keeping original segment")
        return route_coords  # Return unchanged to avoid creating invalid paths


def validate_offline_route(route_coords: List[tuple]) -> Dict[str, Any]:
    """
    Validate offline-optimized route for quality issues.

    Returns:
        Dict with 'valid' boolean, 'issues' list, and 'detour_ratio'
    """
    issues = []

    # Check for unrealistic segment lengths (>500m = possible straight-line shortcut)
    for i in range(len(route_coords) - 1):
        dist_m = geodesic(route_coords[i], route_coords[i+1]).meters
        if dist_m > 500:
            issues.append({
                'type': 'long_segment',
                'index': i,
                'distance_m': dist_m
            })

    # Check total detour ratio (>50% longer = excessive)
    total_distance = sum(
        geodesic(route_coords[i], route_coords[i+1]).kilometers
        for i in range(len(route_coords) - 1)
    )
    direct_distance = geodesic(route_coords[0], route_coords[-1]).kilometers
    detour_ratio = total_distance / direct_distance if direct_distance > 0 else 1

    if detour_ratio > 1.5:
        issues.append({
            'type': 'excessive_detour',
            'ratio': detour_ratio
        })

    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'detour_ratio': detour_ratio
    }


def calculate_perpendicular_safe_point(segment_start: tuple, segment_end: tuple,
                                       threat_point: tuple, safe_distance_km: float = 0.20) -> tuple:
    """
    Calculate a safe waypoint perpendicular to threat.

    Args:
        segment_start: (lat, lng) start of problematic segment
        segment_end: (lat, lng) end of problematic segment
        threat_point: (lat, lng) incident coordinates
        safe_distance_km: Safe distance from threat (default 200m)

    Returns:
        (lat, lng) of safe detour waypoint
    """
    # Calculate segment bearing
    bearing_segment = calculate_bearing(segment_start, segment_end)

    # Perpendicular bearings (+/-90 degrees)
    perp_bearing_1 = (bearing_segment + 90) % 360
    perp_bearing_2 = (bearing_segment - 90) % 360

    # Calculate midpoint of segment
    mid_lat = (segment_start[0] + segment_end[0]) / 2
    mid_lng = (segment_start[1] + segment_end[1]) / 2
    midpoint = (mid_lat, mid_lng)

    # Calculate candidate waypoints in both perpendicular directions
    candidate_1 = destination_point(midpoint, perp_bearing_1, safe_distance_km)
    candidate_2 = destination_point(midpoint, perp_bearing_2, safe_distance_km)

    # Choose the one farther from threat
    dist_1 = geodesic(candidate_1, threat_point).kilometers
    dist_2 = geodesic(candidate_2, threat_point).kilometers

    return candidate_1 if dist_1 > dist_2 else candidate_2


async def geocode_address(address: str, retry_count: int = 0, max_retries: int = 5) -> Optional[Dict[str, float]]:
    """Convert address to coordinates using GraphHopper, filtering for San Francisco

    Enhanced rate limiting:
    - Request queuing via semaphore (max 2 concurrent)
    - Longer exponential backoff: 10s, 30s, 60s, 120s, 240s
    - Min 3s wait between requests
    - Up to 5 retries for rate limit errors
    """
    global last_geocode_request_time

    # Use semaphore to limit concurrent geocoding requests
    async with geocode_semaphore:
        try:
            # Ensure San Francisco is in the query
            if "san francisco" not in address.lower():
                address = f"{address}, San Francisco, CA"

            # Normalize address for cache key (lowercase, strip whitespace)
            cache_key = address.lower().strip()

            # Check cache first (bypass rate limiting for cached results)
            if cache_key in geocode_cache:
                print(f"Cache hit for geocoding: {address}")
                return geocode_cache[cache_key]

            # Rate limiting: wait at least 3 seconds between requests (increased from 2s)
            current_time = time.time()
            time_since_last_request = current_time - last_geocode_request_time
            min_wait = 3.0  # Increased to 3 seconds to reduce API pressure
            if time_since_last_request < min_wait:
                wait_time = min_wait - time_since_last_request
                print(f"Rate limiting: waiting {wait_time:.2f}s before geocoding...")
                await asyncio.sleep(wait_time)  # Use async sleep

            last_geocode_request_time = time.time()

            response = requests.get(
                f"{GEOCODING_URL}?q={address}&key={GRAPHHOPPER_API_KEY}",
                timeout=10
            )

            # Check for 429 rate limit error specifically
            if response.status_code == 429:
                if retry_count < max_retries:
                    # Enhanced exponential backoff: 10s, 30s, 60s, 120s, 240s
                    backoff_time = 10 * (3 ** retry_count)
                    print(f"Rate limit hit (429). Waiting {backoff_time}s before retry {retry_count + 1}/{max_retries}...")
                    await asyncio.sleep(backoff_time)  # Use async sleep
                    last_geocode_request_time = time.time()
                    return await geocode_address(address, retry_count + 1, max_retries)
                else:
                    print(f"Rate limit exceeded after {max_retries} retries. Caching failure.")
                    geocode_cache[cache_key] = None
                    return None

            response.raise_for_status()
            data = response.json()

            if data.get("hits") and len(data["hits"]) > 0:
                # Filter hits to San Francisco only (bounding box: ~37.7-37.8 lat, ~-122.5--122.3 lng)
                for hit in data["hits"]:
                    point = hit["point"]
                    lat, lng = point["lat"], point["lng"]
                    # San Francisco bounding box
                    if 37.7 <= lat <= 37.85 and -122.52 <= lng <= -122.35:
                        # Cache successful result
                        geocode_cache[cache_key] = point
                        return point

                # If no SF hit found, this is likely an invalid or non-SF address
                print(f"ERROR: No San Francisco coordinates found for '{address}'. Address may be invalid or outside SF.")
                geocode_cache[cache_key] = None
                return None

            # No results - cache as None but don't retry
            geocode_cache[cache_key] = None
            return None
        except requests.exceptions.HTTPError as e:
            if "429" in str(e):
                # This shouldn't happen since we check status_code above, but just in case
                if retry_count < max_retries:
                    # Use enhanced exponential backoff
                    backoff_time = 10 * (3 ** retry_count)
                    print(f"Rate limit error (HTTP). Waiting {backoff_time}s before retry...")
                    await asyncio.sleep(backoff_time)
                    last_geocode_request_time = time.time()
                    return await geocode_address(address, retry_count + 1, max_retries)
            print(f"Geocoding HTTP error: {e}")
            geocode_cache[cache_key] = None
            return None
        except Exception as e:
            print(f"Geocoding error: {e}")
            # Only cache non-rate-limit errors
            if "429" not in str(e):
                geocode_cache[cache_key] = None
            return None


async def get_graphhopper_routes(origin_coords: Dict, dest_coords: Dict, num_routes: int = 3) -> List[Dict]:
    """
    Get multiple route alternatives from GraphHopper with enhanced variation strategies.

    Strategies to generate diverse routes:
    1. Alternative routes algorithm (3-5 routes)
    2. Different routing weightings (fastest, shortest)
    3. Small coordinate offsets to force different paths (+/-0.0005 degrees)
    4. Different avoid parameters

    Returns:
        List of distinct route dictionaries
    """
    safe_print(f"  GraphHopper: Requesting {num_routes} routes with enhanced variation...")

    # Validate coordinates before making API calls
    if not validate_coordinates(origin_coords['lat'], origin_coords['lng']):
        safe_print(f"ERROR: Invalid origin coordinates: {origin_coords}")
        raise ValueError(f"Invalid origin coordinates: lat={origin_coords['lat']}, lng={origin_coords['lng']}")

    if not validate_coordinates(dest_coords['lat'], dest_coords['lng']):
        safe_print(f"ERROR: Invalid destination coordinates: {dest_coords}")
        raise ValueError(f"Invalid destination coordinates: lat={dest_coords['lat']}, lng={dest_coords['lng']}")

    routes = []

    # Strategy 1: Alternative routes algorithm
    safe_print(f"  Strategy 1: Alternative routes algorithm...")
    params = {
        "vehicle": "foot",
        "locale": "en",
        "points_encoded": "false",
        "algorithm": "alternative_route",
        "alternative_route.max_paths": "5",
        "key": GRAPHHOPPER_API_KEY,
    }

    point_str = f"point={origin_coords['lat']},{origin_coords['lng']}&point={dest_coords['lat']},{dest_coords['lng']}"

    try:
        response = requests.get(
            f"{ROUTING_URL}?{point_str}&" + "&".join([f"{k}={v}" for k, v in params.items()]),
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        if data.get("paths"):
            print(f"  Strategy 1: Found {len(data['paths'])} alternative paths")
            for path in data["paths"]:
                routes.append({
                    "distance": path["distance"],
                    "time": path["time"],
                    "coordinates": [(coord[1], coord[0]) for coord in path["points"]["coordinates"]],
                    "strategy": "alternative"
                })
    except Exception as e:
        print(f"  Strategy 1 error: {e}")
        return []

    # Strategy 2: Different weighting profiles
    if len(routes) < num_routes:
        print(f"  Strategy 2: Different weighting profiles...")
        weightings = ["fastest", "shortest"]

        for weighting in weightings:
            try:
                params = {
                    "vehicle": "foot",
                    "locale": "en",
                    "points_encoded": "false",
                    "weighting": weighting,
                    "key": GRAPHHOPPER_API_KEY,
                }

                response = requests.get(
                    f"{ROUTING_URL}?{point_str}&" + "&".join([f"{k}={v}" for k, v in params.items()]),
                    timeout=15
                )

                if response.ok:
                    data = response.json()
                    if data.get("paths"):
                        path = data["paths"][0]
                        route = {
                            "distance": path["distance"],
                            "time": path["time"],
                            "coordinates": [(coord[1], coord[0]) for coord in path["points"]["coordinates"]],
                            "strategy": f"weighting_{weighting}"
                        }
                        # Check if different enough (>200m difference)
                        if not any(abs(r["distance"] - route["distance"]) < 200 for r in routes):
                            routes.append(route)
                            print(f"  Strategy 2: Added {weighting} route ({route['distance']:.0f}m)")
            except Exception as e:
                print(f"  Strategy 2 ({weighting}) error: {e}")
                continue

    # Strategy 3: Small coordinate offsets to force different paths
    if len(routes) < 3:  # Need at least 3 routes for good variation
        print(f"  Strategy 3: Coordinate offset variations...")
        offsets = [
            {"lat_offset": 0.0005, "lng_offset": 0},      # Slightly north
            {"lat_offset": -0.0005, "lng_offset": 0},     # Slightly south
            {"lat_offset": 0, "lng_offset": 0.0005},      # Slightly east
            {"lat_offset": 0, "lng_offset": -0.0005},     # Slightly west
        ]

        for i, offset in enumerate(offsets):
            if len(routes) >= num_routes:
                break

            try:
                # Apply offset to origin
                offset_origin_lat = origin_coords['lat'] + offset['lat_offset']
                offset_origin_lng = origin_coords['lng'] + offset['lng_offset']

                offset_point_str = f"point={offset_origin_lat},{offset_origin_lng}&point={dest_coords['lat']},{dest_coords['lng']}"

                params = {
                    "vehicle": "foot",
                    "locale": "en",
                    "points_encoded": "false",
                    "weighting": "fastest",
                    "key": GRAPHHOPPER_API_KEY,
                }

                response = requests.get(
                    f"{ROUTING_URL}?{offset_point_str}&" + "&".join([f"{k}={v}" for k, v in params.items()]),
                    timeout=15
                )

                if response.ok:
                    data = response.json()
                    if data.get("paths"):
                        path = data["paths"][0]
                        route = {
                            "distance": path["distance"],
                            "time": path["time"],
                            "coordinates": [(coord[1], coord[0]) for coord in path["points"]["coordinates"]],
                            "strategy": f"offset_{i}"
                        }
                        # Check if different enough
                        if not any(abs(r["distance"] - route["distance"]) < 200 for r in routes):
                            routes.append(route)
                            print(f"  Strategy 3: Added offset route {i+1} ({route['distance']:.0f}m)")
            except Exception as e:
                print(f"  Strategy 3 (offset {i}) error: {e}")
                continue

    # Filter duplicates based on coordinate similarity
    unique_routes = []
    for route in routes:
        is_duplicate = False
        for existing in unique_routes:
            # Check distance similarity (within 100m)
            if abs(route["distance"] - existing["distance"]) < 100:
                # Check coordinate overlap
                route_coords_set = set([f"{lat:.4f},{lng:.4f}" for lat, lng in route["coordinates"][:15]])
                existing_coords_set = set([f"{lat:.4f},{lng:.4f}" for lat, lng in existing["coordinates"][:15]])
                overlap = len(route_coords_set & existing_coords_set) / max(len(route_coords_set), 1)
                if overlap > 0.75:  # >75% overlap = duplicate
                    is_duplicate = True
                    break

        if not is_duplicate:
            unique_routes.append(route)

    print(f"  Final: {len(unique_routes)} unique routes (from {len(routes)} candidates)")
    return unique_routes


def periodic_data_fetch():
    """Fetch data periodically (called by scheduler)"""
    print(f"\n[{datetime.now()}] = Fetching updated incident data...")
    try:
        data_fetcher.fetch_all_data()
        print(f"Data fetch complete")
    except Exception as e:
        print(f"L Data fetch failed: {e}")


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "SafePath API",
        "version": "1.0.0",
        "last_data_fetch": data_fetcher.last_fetch_time.isoformat() if data_fetcher.last_fetch_time else None
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    data = data_fetcher.get_data()

    return {
        "status": "healthy",
        "data": {
            "crime_incidents": len(data["crime_data"]),
            "311_incidents": len(data["incidents_311"]),
            "last_fetch": data["fetch_time"]
        },
        "timestamp": datetime.now().isoformat()
    }


# Route Optimization Functions

def generate_detour_offline(segment: Dict[str, Any], route_coords: List[tuple],
                           crime_data: List[Dict], incidents_311: List[Dict]) -> List[tuple]:
    """
    Generate a safe detour using OFFLINE waypoint injection (no API calls).

    Strategy:
    1. Identify closest incident(s) to segment
    2. Calculate perpendicular waypoint 250m away from threats
    3. Inject waypoint into route using existing route points as anchors
    4. Validate detour maintains >200m from all incidents

    Args:
        segment: Dictionary with 'coords', 'start', 'end', 'nearby_incidents', 'min_distance_km'
        route_coords: Full route coordinate array for anchor searching
        crime_data: All crime incidents
        incidents_311: All 311 incidents

    Returns:
        List of (lat, lng) coordinates for safe detour (offline-generated)
    """
    segment_coords = segment['coords']
    start_coord = segment['start']
    end_coord = segment['end']
    nearby_incidents = segment['nearby_incidents']
    original_min_distance = segment.get('min_distance_km', 0)

    print(f"    Generating OFFLINE detour: {len(segment_coords)} points, {len(nearby_incidents)} incidents to avoid, "
          f"closest at {original_min_distance*1000:.0f}m")

    if not nearby_incidents:
        return segment_coords

    # Sort incidents by proximity (closest first)
    nearby_incidents.sort(key=lambda x: x['min_distance_km'])

    # Calculate safe waypoint perpendicular to closest threat
    closest_threat = nearby_incidents[0]
    safe_waypoint = calculate_perpendicular_safe_point(
        start_coord,
        end_coord,
        closest_threat['coords'],
        safe_distance_km=0.25  # 250m safe distance
    )

    # Find segment indices in full route
    segment_start_idx = None
    segment_end_idx = None
    for i in range(len(route_coords)):
        if route_coords[i] == start_coord:
            segment_start_idx = i
        if route_coords[i] == end_coord:
            segment_end_idx = i
            break

    if segment_start_idx is None or segment_end_idx is None:
        print(f"    WARNING: Could not locate segment in route, keeping original")
        return segment_coords

    # Inject waypoint offline using existing route points as anchors
    detour_coords = inject_waypoint_offline(
        route_coords,
        segment_start_idx,
        segment_end_idx,
        safe_waypoint,
        search_radius_km=0.3
    )

    # Validate detour maintains safe distance from ALL incidents
    incidents_in_detour, min_dist_detour = risk_scorer.find_incidents_within_buffer(
        detour_coords, crime_data, incidents_311, buffer_distance_km=0.20
    )

    print(f"      OFFLINE detour: {len(incidents_in_detour)} incidents within 200m (closest: {min_dist_detour*1000:.0f}m)")

    # Accept if ANY improvement in distance from incidents
    if min_dist_detour > original_min_distance:
        improvement_m = (min_dist_detour - original_min_distance) * 1000
        print(f"    SUCCESS: Offline detour improves safety by +{improvement_m:.0f}m")
        return detour_coords
    else:
        print(f"    WARNING: Offline detour did not improve safety, keeping original segment")
        return segment_coords


def repair_segment_offline(segment: Dict[str, Any], route_coords: List[tuple],
                          crime_data: List[Dict], incidents_311: List[Dict]) -> List[tuple]:
    """
    Generate a safe detour for a problematic segment using OFFLINE waypoint injection.
    MAXIMUM SAFETY MODE: Accept any detour that increases distance from incidents.

    Args:
        segment: Dictionary with 'start', 'end', 'nearby_incidents', 'min_distance_km'
        route_coords: Full route coordinate array for anchor searching
        crime_data: All crime incidents
        incidents_311: All 311 incidents

    Returns:
        List of (lat, lng) coordinates for repaired segment (offline-generated)
    """
    return generate_detour_offline(segment, route_coords, crime_data, incidents_311)


def reconstruct_optimized_route(original_coords: List[tuple], problematic_segments: List[Dict],
                                repaired_coords: List[List[tuple]]) -> List[tuple]:
    """
    Reconstruct complete route by replacing problematic segments with repairs.

    Args:
        original_coords: Original route coordinates
        problematic_segments: List of problematic segment dictionaries
        repaired_coords: List of repaired coordinate lists (same order as problematic_segments)

    Returns:
        Complete optimized route coordinates
    """
    if not problematic_segments:
        return original_coords

    optimized_route = []
    current_idx = 0

    for i, problem_segment in enumerate(problematic_segments):
        # Find where this problem starts in original route
        problem_start = problem_segment['start']

        try:
            problem_start_idx = original_coords.index(problem_start)
        except ValueError:
            # Segment not found in original, skip
            continue

        # Add safe portion before this problem
        optimized_route.extend(original_coords[current_idx:problem_start_idx])

        # Add repaired segment
        optimized_route.extend(repaired_coords[i])

        # Find where this problem ends
        problem_end = problem_segment['end']
        try:
            problem_end_idx = original_coords.index(problem_end)
            current_idx = problem_end_idx + 1
        except ValueError:
            current_idx = problem_start_idx + len(problem_segment['coords'])

    # Add remaining safe portion
    if current_idx < len(original_coords):
        optimized_route.extend(original_coords[current_idx:])

    return optimized_route


def iterative_route_optimization(original_route: Dict[str, Any], crime_data: List[Dict],
                                incidents_311: List[Dict], max_iterations: int = 1) -> Dict[str, Any]:
    """
    Multi-pass iterative optimization with waypoint injection.
    CONSERVATIVE MODE: Only optimize if safe detours can be found.

    Args:
        original_route: Route dictionary with 'coordinates', 'distance', 'time', 'total_risk'
        crime_data: Crime incident data
        incidents_311: 311 incident data
        max_iterations: Maximum optimization passes

    Returns:
        Optimized route if improvements found, otherwise original route
    """
    current_route = original_route
    iteration = 0

    print(f"\n  === ITERATIVE ROUTE OPTIMIZATION (Conservative Mode, Max {max_iterations} passes) ===")

    while iteration < max_iterations:
        iteration += 1
        route_coords = [(c['lat'], c['lng']) for c in current_route['coordinates']]

        print(f"\n  --- Iteration {iteration}/{max_iterations} ---")

        # Phase 1: Identify ONLY THE WORST segments (highest risk, closest incidents)
        problematic_segments = risk_scorer.identify_problematic_segments(
            route_coords=route_coords,
            crime_data=crime_data,
            incidents_311=incidents_311,
            threshold_distance_km=0.10,  # REDUCED: Only optimize segments within 100m (very close)
            depth=0,
            max_depth=3  # REDUCED: Less aggressive subdivision to avoid over-optimization
        )

        if not problematic_segments:
            print(f"  [SUCCESS] No segments within 100m of incidents!")
            break

        # LIMIT: Only optimize the 2 worst segments to avoid excessive path changes
        if len(problematic_segments) > 2:
            problematic_segments.sort(key=lambda x: x.get('min_distance_km', 999))
            problematic_segments = problematic_segments[:2]
            print(f"  Limiting optimization to 2 worst segments (out of {len(problematic_segments)} candidates)")

        print(f"  Found {len(problematic_segments)} segments within 100m of incidents")

        # Phase 2: Generate OFFLINE waypoint-based detours for each problematic segment
        repaired_segments = []
        improvements = 0
        for idx, segment in enumerate(problematic_segments):
            print(f"\n  Segment {idx+1}/{len(problematic_segments)}:")
            repaired = repair_segment_offline(segment, route_coords, crime_data, incidents_311)

            # Check if repair actually improved safety
            original_min_dist = segment.get('min_distance_km', 0)
            _, repaired_min_dist = risk_scorer.find_incidents_within_buffer(
                repaired, crime_data, incidents_311, buffer_distance_km=0.20
            )

            if repaired_min_dist > original_min_dist:
                improvements += 1

            repaired_segments.append(repaired)

        if improvements == 0:
            print(f"\n  [WARNING] No improvements possible in iteration {iteration}, stopping")
            break

        # Phase 3: Reconstruct complete route with repaired segments
        optimized_coords = reconstruct_optimized_route(route_coords, problematic_segments, repaired_segments)

        # Validate optimized route before accepting
        validation = validate_offline_route(optimized_coords)

        # Reject if route has quality issues (straight lines, excessive detours, loops)
        if not validation['valid']:
            print(f"\n  [REJECTED] Optimized route failed validation:")
            for issue in validation['issues']:
                if issue['type'] == 'long_segment':
                    print(f"    - Long segment at index {issue['index']}: {issue['distance_m']:.0f}m (possible straight line)")
                elif issue['type'] == 'excessive_detour':
                    print(f"    - Excessive detour: {issue['ratio']:.2f}x longer than direct path")
            print(f"  Keeping original route")
            break

        # Recalculate all metrics
        optimized_risk = risk_scorer.calculate_segment_risk(optimized_coords, crime_data, incidents_311)
        optimized_distance_km = risk_scorer.calculate_path_length(optimized_coords)
        _, optimized_min_distance = risk_scorer.find_incidents_within_buffer(
            optimized_coords, crime_data, incidents_311, buffer_distance_km=0.20
        )

        # SANITY CHECK: Reject if distance increased by more than 50%
        original_distance_km = current_route.get('distance_km', 0)
        if original_distance_km > 0:
            distance_increase_pct = (optimized_distance_km - original_distance_km) / original_distance_km * 100
            if distance_increase_pct > 50:
                print(f"\n  [REJECTED] Route distance increased by {distance_increase_pct:.1f}% (>50% limit)")
                print(f"  This likely indicates a loop or excessive detour")
                print(f"  Keeping original route")
                break

        print(f"\n  Iteration {iteration} Summary:")
        print(f"    Segments repaired: {improvements}/{len(problematic_segments)}")
        print(f"    Route risk: {current_route.get('total_risk', 0):.2f} -> {optimized_risk:.2f}")
        print(f"    Distance: {current_route.get('distance_km', 0):.2f}km -> {optimized_distance_km:.2f}km")
        print(f"    Closest incident: {current_route.get('min_distance_to_incidents', 0)*1000:.0f}m -> {optimized_min_distance*1000:.0f}m")
        print(f"    Validation: {validation['detour_ratio']:.2f}x detour ratio")

        # Recalculate estimated time based on walking speed (5 km/h)
        walking_speed_kmh = 5.0
        optimized_time_sec = (optimized_distance_km / walking_speed_kmh) * 3600
        optimized_time_min = int(optimized_time_sec / 60)

        # Update current route for next iteration
        current_route = {
            **current_route,
            'coordinates': [{'lat': c[0], 'lng': c[1]} for c in optimized_coords],
            'distance': f"{round(optimized_distance_km * 0.621371, 1)} mi",  # Update distance display
            'distance_km': optimized_distance_km,
            'time': f"{optimized_time_min} min",  # Update time display
            'total_risk': optimized_risk,
            'min_distance_to_incidents': optimized_min_distance,
            'optimized': True,
            'iterations': iteration,
            'segments_repaired': improvements
        }

    # Final result summary
    original_risk = original_route.get('total_risk', 0)
    final_risk = current_route.get('total_risk', 0)
    risk_reduction_pct = (1 - final_risk/original_risk) * 100 if original_risk > 0 else 0

    original_distance = original_route.get('distance_km', 0)
    final_distance = current_route.get('distance_km', 0)
    distance_increase_pct = (final_distance - original_distance) / original_distance * 100 if original_distance > 0 else 0

    print(f"\n  === OPTIMIZATION COMPLETE ===")
    print(f"  Iterations: {iteration}/{max_iterations}")
    print(f"  Risk reduction: -{risk_reduction_pct:.1f}%")
    print(f"  Distance increase: +{distance_increase_pct:.1f}%")
    print(f"  Optimized: {current_route.get('optimized', False)}")

    # MAXIMUM SAFETY MODE: Accept ANY improvement in safety
    if current_route.get('optimized') and final_risk < original_risk:
        print(f"  [ACCEPTED] Route safety improved")
        return current_route
    else:
        print(f"  [REJECTED] No safety improvement achieved")
        return original_route


def optimize_route_recursive(original_route: Dict[str, Any], crime_data: List[Dict],
                            incidents_311: List[Dict]) -> Dict[str, Any]:
    """
    Main optimization function with OFFLINE iterative waypoint injection.
    NOW USES DISTANCE-BASED DETECTION (200m buffer) instead of risk-based.
    NO API CALLS - All optimization done in-memory with coordinate manipulation.

    Args:
        original_route: Route dictionary with 'coordinates', 'distance', 'time'
        crime_data: Crime incident data
        incidents_311: 311 incident data

    Returns:
        Optimized route with all segments maintaining >200m from incidents (offline-optimized)
    """
    return iterative_route_optimization(original_route, crime_data, incidents_311, max_iterations=1)


@app.post("/api/routes", response_model=RoutesResponse)
async def calculate_routes(request: RouteRequest):
    """
    Calculate and analyze routes using real-time crime and 311 data

    Algorithm:
    1. Geocode origin and destination using GraphHopper API
    2. Generate 10 route variations using multiple strategies:
       - Alternative routes algorithm (3-5 routes)
       - Different routing profiles (fastest)
       - Slight variations (+/-5% distance/time)
    3. For each route, calculate risk score using mathematical formula:
       - For each incident near the route:
         * Calculate minimum distance d (km) from incident to route path
         * Calculate time t (hours) since incident occurred
         * Apply time-decay formula based on risk weight w:
           - High-risk (w=3, 72h decay): ReLU(3-3t/72)^2 * e^(-d^2/0.02)
           - Med/low-risk (w=1-2, 24h decay): ReLU(w-wt/24)^2 * e^(-d^2/0.02)
           - Encampments (no decay): w^2 * e^(-d^2/0.02)
       - Sum all risk contributions to total_risk
    4. Convert total_risk to safety_score (0-100): 100 * e^(-risk/10)
    5. Sort routes by risk (ascending) and select top 2 (Safest and Balanced)
    6. Generate specific descriptions based on actual threats avoided

    Returns:
        Top 2 routes (Safest, Balanced) with safety scores, risk breakdowns, and threat-specific descriptions

    Timeout: 60 seconds total (prevents stuck calculations)
    """
    try:
        # Wrap entire calculation in timeout to prevent stuck routes
        # Mathematical timeout formula: 60s total = 10s geocoding + 15s routing + 35s optimization
        return await asyncio.wait_for(
            _calculate_routes_internal(request),
            timeout=60.0
        )
    except asyncio.TimeoutError:
        print("ERROR: Route calculation exceeded 60s timeout")
        raise HTTPException(
            status_code=504,
            detail="Route calculation took too long. This address pair may be invalid or too complex. Please try different addresses."
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 for invalid addresses)
        raise
    except Exception as e:
        import traceback
        error_msg = f"An error occurred while calculating routes: {str(e)}"
        try:
            print(f"ERROR: Unexpected error in route calculation: {e}")
            print("".join(traceback.format_exc()))
        except:
            pass  # Ignore print errors on Windows
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


async def _calculate_routes_internal(request: RouteRequest):
    """
    Internal route calculation logic (separated for timeout wrapping)
    """
    try:
        print(f"\n=== ROUTE REQUEST START ===")
        print(f"Origin: {request.origin}")
        print(f"Destination: {request.destination}")
    except:
        pass  # Suppress print errors

    # Validation: Check for empty origin or destination fields
    if not request.origin or not request.origin.strip():
        print("ERROR: Empty origin field")
        raise HTTPException(status_code=400, detail="Origin address cannot be empty. Please enter a valid starting location.")

    if not request.destination or not request.destination.strip():
        print("ERROR: Empty destination field")
        raise HTTPException(status_code=400, detail="Destination address cannot be empty. Please enter a valid destination location.")

    print(f"Step 1: Geocoding addresses...")

    # Step 1: Geocode addresses
    origin_coords = await geocode_address(request.origin)
    print(f"Origin geocoded: {origin_coords}")
    dest_coords = await geocode_address(request.destination)
    print(f"Destination geocoded: {dest_coords}")

    if not origin_coords or not dest_coords:
        print("ERROR: Could not geocode addresses")
        raise HTTPException(status_code=400, detail="Could not geocode addresses. Please enter valid San Francisco addresses.")

    # Validation: Check if origin and destination are the same location (within 50m)
    distance_between = geodesic(
        (origin_coords["lat"], origin_coords["lng"]),
        (dest_coords["lat"], dest_coords["lng"])
    ).meters

    if distance_between < 50:
        print(f"ERROR: Origin and destination are the same location ({distance_between:.1f}m apart)")
        raise HTTPException(
            status_code=400,
            detail=f"Origin and destination are too close together ({distance_between:.0f}m apart). Please enter different locations that are at least 50 meters apart."
        )

    print(f"Distance between origin and destination: {distance_between:.0f}m")
    print(f"Step 2: Generating 10 route variations...")
    routes = await get_graphhopper_routes(origin_coords, dest_coords, num_routes=3)
    print(f"GraphHopper returned: {len(routes) if routes else 0} routes")

    if not routes:
        print("ERROR: Could not generate routes from GraphHopper")
        raise HTTPException(status_code=500, detail="Could not generate routes")

    # Step 3: Get current incident data
    print(f"Step 3: Getting incident data...")
    data = data_fetcher.get_data()
    crime_data = data["crime_data"]
    incidents_311 = data["incidents_311"]
    print(f"Using {len(crime_data)} crime incidents and {len(incidents_311)} 311 incidents")

    # Step 4: Analyze each route
    print(f"Step 4: Analyzing {len(routes)} routes...")
    analyzed_routes = []

    for i, route in enumerate(routes):
        print(f"Analyzing route {i+1}/{len(routes)}...")
        # Convert coordinates to the format expected by risk scorer
        path_coords = [{"lat": lat, "lng": lng} for lat, lng in route["coordinates"]]

        # Calculate risk
        analysis = risk_scorer.analyze_route(path_coords, crime_data, incidents_311)
        print(f"Route {i+1} risk: {analysis['total_risk']:.2f}")

        # Convert distance and time
        distance_mi = round(route["distance"] / 1609.34, 1)
        time_min = round(route["time"] / 1000 / 60)

        # Calculate safety score (0-100, inverted from risk)
        # Lower risk = higher safety score
        # We'll use a logarithmic scale to convert risk to safety score
        total_risk = analysis["total_risk"]
        if total_risk == 0:
            safety_score = 100
        else:
            # Map risk (0-inf) to safety (100-0)
            # Using exponential decay: safety = 100 * e^(-risk/10)
            import math
            safety_score = int(100 * math.exp(-total_risk / 10))
            safety_score = max(0, min(100, safety_score))  # Clamp to 0-100

        analyzed_routes.append({
            "id": i + 1,
            "name": f"Route {i + 1}",
            "distance": f"{distance_mi} mi",
            "distance_km": route["distance"] / 1000,
            "time": f"{time_min} min",
            "safetyScore": safety_score,
            "total_risk": analysis["total_risk"],
            "crime_risk": analysis["crime_risk"],
            "incident_risk": analysis["incident_risk"],
            "coordinates": [{"lat": lat, "lng": lng} for lat, lng in route["coordinates"]],
            "color": "#6b7280"  # Will be assigned by frontend
        })

    # Step 4.5: Optimize routes using OFFLINE recursive subdivision
    print(f"Step 4.5: Optimizing routes with OFFLINE recursive subdivision...")
    optimized_routes = []
    for i, route in enumerate(analyzed_routes):
        print(f"Optimizing route {i+1}/{len(analyzed_routes)}...")
        optimized = optimize_route_recursive(route, crime_data, incidents_311)

        # Recalculate safety score if route was optimized
        if optimized.get('optimized'):
            total_risk = optimized['total_risk']
            if total_risk == 0:
                safety_score = 100
            else:
                safety_score = int(100 * math.exp(-total_risk / 10))
                safety_score = max(0, min(100, safety_score))
            optimized['safetyScore'] = safety_score

            # Update distance display
            distance_mi = round(optimized['distance_km'] * 0.621371, 1)
            optimized['distance'] = f"{distance_mi} mi"

        optimized_routes.append(optimized)

    # Step 5: Select 2 routes - Safest and Balanced
    # DISTANCE-BASED Selection with Tiered Safety Criteria:
    #   1. Safest Route: Maximum minimum distance from incidents (200m > 150m > 100m > 50m)
    #   2. Balanced Route: Different path with acceptable safety profile

    print(f"Step 5: Selecting 2 routes using distance-based safety tiers...")

    if not optimized_routes:
        raise HTTPException(status_code=500, detail="No valid routes found after optimization")

    # Calculate minimum distance to nearest incident for each route
    for route in optimized_routes:
        route_coords = [(c['lat'], c['lng']) for c in route['coordinates']]
        _, min_distance = risk_scorer.find_incidents_within_buffer(
            route_coords, crime_data, incidents_311, buffer_distance_km=1.0  # Check within 1km
        )
        route['min_incident_distance_km'] = min_distance
        route['min_incident_distance_m'] = min_distance * 1000

    # Tiered safety classification
    safety_tiers = [
        ("Excellent", 0.200),   # 200m+
        ("Good", 0.150),        # 150m+
        ("Acceptable", 0.100),  # 100m+
        ("Minimum", 0.050),     # 50m+
        ("Unavoidable", 0.0)    # < 50m
    ]

    # Assign safety tier to each route
    for route in optimized_routes:
        min_dist = route['min_incident_distance_km']
        for tier_name, tier_threshold in safety_tiers:
            if min_dist >= tier_threshold:
                route['safety_tier'] = tier_name
                break

    # Sort by minimum incident distance (descending - farther is safer)
    # Secondary sort by total risk if distances are similar
    optimized_routes.sort(key=lambda x: (x['min_incident_distance_km'], -x["total_risk"]), reverse=True)

    # Route 1: Safest - Maximum distance from all incidents
    safest_route = optimized_routes[0]
    safest_time_min = int(safest_route["time"].replace(" min", ""))
    safest_dist_km = safest_route.get("distance_km", 0)
    safest_min_dist_m = safest_route['min_incident_distance_m']

    print(f"  Safest route: {safest_route['safety_tier']} safety tier, "
          f"closest incident {safest_min_dist_m:.0f}m away, "
          f"{safest_time_min} min, {safest_dist_km:.2f} km")

    # Route 2: Balanced - Must be visually distinct from safest
    remaining_routes = []
    for route in optimized_routes[1:]:
        route_dist_km = route.get("distance_km", 0)
        route_coords = route.get("coordinates", [])
        safest_coords = safest_route.get("coordinates", [])

        # Calculate path similarity
        route_coords_sample = set([f"{c['lat']:.4f},{c['lng']:.4f}" for c in route_coords[::5]])
        safest_coords_sample = set([f"{c['lat']:.4f},{c['lng']:.4f}" for c in safest_coords[::5]])
        overlap = len(route_coords_sample & safest_coords_sample) / max(len(route_coords_sample), 1)

        # Calculate differences
        dist_diff_km = abs(route_dist_km - safest_dist_km)
        min_dist_diff_m = abs(route['min_incident_distance_m'] - safest_min_dist_m)

        # DISTINCT CRITERIA: Different path (<70% overlap) OR different distance (>200m)
        is_distinct = overlap < 0.70 or dist_diff_km >= 0.20

        if is_distinct:
            remaining_routes.append({
                'route': route,
                'dist_diff': dist_diff_km,
                'overlap': overlap,
                'distinctness_score': dist_diff_km + (1 - overlap)
            })

    if remaining_routes:
        # Sort by distinctness (most different path first)
        remaining_routes.sort(key=lambda x: x['distinctness_score'], reverse=True)
        balanced_route = remaining_routes[0]['route']

        balanced_time_min = int(balanced_route["time"].replace(" min", ""))
        balanced_dist_km = balanced_route.get("distance_km", 0)
        balanced_min_dist_m = balanced_route['min_incident_distance_m']
        time_diff = balanced_time_min - safest_time_min

        print(f"  Balanced route: {balanced_route['safety_tier']} safety tier, "
              f"closest incident {balanced_min_dist_m:.0f}m away, "
              f"{balanced_time_min} min, {balanced_dist_km:.2f} km")
        print(f"  Difference: {time_diff:+d} min, "
              f"{(1 - remaining_routes[0]['overlap'])*100:.0f}% different path")

        selected_routes = [safest_route, balanced_route]
    else:
        # No distinct route available - use safest for both
        print(f"  INFO: No distinct alternative route found, displaying safest route only")
        balanced_route = safest_route.copy()
        balanced_route['id'] = 2
        selected_routes = [safest_route, balanced_route]

    # Step 6: Assign names, colors, and generate specific descriptions
    print(f"Step 6: Generating route-specific descriptions...")
    colors = ["#10b981", "#3b82f6"]  # Green for Safest, Blue for Balanced

    for i, route in enumerate(selected_routes):
        route["color"] = colors[i]
        route["id"] = i + 1

        # Analyze nearby incidents for this specific route
        route_path = [(c['lat'], c['lng']) for c in route['coordinates']]
        nearby_crimes = risk_scorer.find_nearby_incidents(route_path, crime_data, "crime", radius_km=0.118)
        nearby_311 = risk_scorer.find_nearby_incidents(route_path, incidents_311, "311", radius_km=0.118)

        # Calculate risk breakdown percentages
        crime_pct = (route["crime_risk"] / route["total_risk"] * 100) if route["total_risk"] > 0 else 0
        incident_pct = (route["incident_risk"] / route["total_risk"] * 100) if route["total_risk"] > 0 else 0

        if i == 0:
            # Safest Route - describe specific threats avoided
            route["name"] = "Safest Route"

            # Build specific description based on actual nearby incidents
            threat_details = []
            if nearby_crimes:
                high_risk_crimes = [c for c in nearby_crimes if c['weight'] >= 2]
                if high_risk_crimes:
                    crime_types = set([c['incident'].get('call_type_original_desc', 'incident')[:20] for c in high_risk_crimes[:3]])
                    threat_details.append(f"avoids {len(high_risk_crimes)} high-risk crime area(s)")

            if nearby_311:
                encampments = [i for i in nearby_311 if 'ENCAMPMENT' in i['incident'].get('service_name', '').upper()]
                aggressive = [i for i in nearby_311 if 'AGGRESSIVE' in i['incident'].get('service_name', '').upper()]
                if encampments:
                    threat_details.append(f"{len(encampments)} encampment(s)")
                if aggressive:
                    threat_details.append(f"{len(aggressive)} aggressive incident report(s)")

            if threat_details:
                route["description"] = f"Safest path - maintains maximum distance from {', '.join(threat_details)}. Total risk score: {route['total_risk']:.1f}"
            else:
                route["description"] = f"Safest path with minimal risk exposure (score: {route['total_risk']:.1f}). Optimal positioning away from all incident types."

        else:
            # Balanced Route - describe efficiency vs safety tradeoff
            route["name"] = "Balanced Route"

            route_time_min = int(route["time"].replace(" min", ""))
            time_saved = safest_time_min - route_time_min

            # Build description explaining the tradeoff
            threat_details = []
            if nearby_crimes:
                threat_details.append(f"{len(nearby_crimes)} crime area(s)")
            if nearby_311:
                threat_details.append(f"{len(nearby_311)} 311 incident(s)")

            if time_saved > 0:
                route["description"] = f"Faster option ({time_saved} min saved) with acceptable risk increase. Passes near {', '.join(threat_details) if threat_details else 'monitored areas'}, risk score: {route['total_risk']:.1f}"
            else:
                route["description"] = f"Alternative path with different risk profile. Navigates around {', '.join(threat_details) if threat_details else 'incident zones'}, risk score: {route['total_risk']:.1f}"

    print(f"Selected 2 routes:")
    for route in selected_routes:
        print(f"  {route['name']}: Risk={route['total_risk']:.2f}, Safety={route['safetyScore']}/100")
        print(f"    Description: {route['description']}")

    print(f"=== ROUTE REQUEST COMPLETE ===\n")
    return {
        "routes": selected_routes,
        "originCoords": {"lat": origin_coords["lat"], "lng": origin_coords["lng"]},
        "destCoords": {"lat": dest_coords["lat"], "lng": dest_coords["lng"]},
        "data_timestamp": data["fetch_time"]
    }


@app.get("/api/data/stats")
async def get_data_stats():
    """Get current incident data statistics"""
    data = data_fetcher.get_data()

    return {
        "crime_incidents": len(data["crime_data"]),
        "incidents_311": len(data["incidents_311"]),
        "last_fetch": data["fetch_time"],
        "next_fetch": "In 10 minutes"
    }


@app.get("/api/incidents")
async def get_all_incidents():
    """
    Get all incidents formatted for map markers
    Returns crime and 311 incidents with coordinates, type, and timestamp
    """
    data = data_fetcher.get_data()
    incidents = []

    # Process crime incidents
    for crime in data["crime_data"]:
        coords = None

        # Handle both WKT POINT format and GeoJSON format
        if crime.get("intersection_point"):
            point_data = crime["intersection_point"]

            # GeoJSON format: {"type": "Point", "coordinates": [lng, lat]}
            if isinstance(point_data, dict) and point_data.get("coordinates"):
                coords = point_data["coordinates"]
            # WKT POINT format: "POINT (-122.419 37.778)"
            elif isinstance(point_data, str) and "POINT" in point_data:
                coords_str = point_data.replace("POINT (", "").replace(")", "").split()
                if len(coords_str) == 2:
                    coords = [float(coords_str[0]), float(coords_str[1])]

        if coords and len(coords) == 2:
            incidents.append({
                "type": "crime",
                "title": crime.get("call_type_final_desc") or crime.get("call_type_original_desc", "Unknown Incident"),
                "date": crime.get("entry_datetime", ""),
                "location": crime.get("intersection_name", "Unknown Location"),
                "coordinates": {
                    "lat": float(coords[1]),
                    "lng": float(coords[0])
                }
            })

    # Process 311 incidents
    for incident in data["incidents_311"]:
        coords = None

        # Handle both WKT POINT format and GeoJSON format
        if incident.get("point_geom"):
            point_data = incident["point_geom"]

            # GeoJSON format: {"type": "Point", "coordinates": [lng, lat]}
            if isinstance(point_data, dict) and point_data.get("coordinates"):
                coords = point_data["coordinates"]
            # WKT POINT format: "POINT (-122.419 37.778)"
            elif isinstance(point_data, str) and "POINT" in point_data:
                coords_str = point_data.replace("POINT (", "").replace(")", "").split()
                if len(coords_str) == 2:
                    coords = [float(coords_str[0]), float(coords_str[1])]

        if coords and len(coords) == 2:
            lat, lng = float(coords[1]), float(coords[0])

            # Reverse geocode to get street address/intersection
            location = await reverse_geocode(lat, lng)

            incidents.append({
                "type": "311",
                "title": incident.get("service_name", "Unknown Service"),
                "subtype": incident.get("service_subtype", ""),
                "date": incident.get("requested_datetime", ""),
                "location": location,  # Added reverse geocoded location
                "status": incident.get("status_description", ""),
                "coordinates": {
                    "lat": lat,
                    "lng": lng
                }
            })

    return {
        "incidents": incidents,
        "total_count": len(incidents),
        "crime_count": len([i for i in incidents if i["type"] == "crime"]),
        "incident_311_count": len([i for i in incidents if i["type"] == "311"]),
        "last_fetch": data["fetch_time"]
    }

