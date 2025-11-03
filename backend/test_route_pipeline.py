"""
Route Calculation Pipeline Testing
Tests each step of the route calculation process with benchmarking
"""
import time
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main import geocode_address, get_graphhopper_routes, GRAPHHOPPER_API_KEY
from app.data_fetcher import DataSFetcher
from app.risk_scorer import RiskScorer

def benchmark(func):
    """Decorator to benchmark function execution time"""
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"[PASS] {func.__name__}: {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            print(f"[FAIL] {func.__name__}: {elapsed:.2f}s - {str(e)}")
            raise

    def sync_wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"[PASS] {func.__name__}: {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            print(f"[FAIL] {func.__name__}: {elapsed:.2f}s - {str(e)}")
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


@benchmark
async def test_api_key():
    """Test 0: Verify GraphHopper API key is configured"""
    print("\n=== TEST 0: API Key Configuration ===")
    if not GRAPHHOPPER_API_KEY:
        raise Exception("GRAPHHOPPER_API_KEY not set")
    print(f"API Key: {GRAPHHOPPER_API_KEY[:10]}...{GRAPHHOPPER_API_KEY[-10:]}")
    return True


@benchmark
async def test_geocode_origin():
    """Test 1a: Geocode origin address"""
    print("\n=== TEST 1a: Geocode Origin ===")
    address = "Union Square, San Francisco"
    print(f"Geocoding: {address}")
    coords = await geocode_address(address)
    if not coords:
        raise Exception(f"Failed to geocode: {address}")
    print(f"Result: {coords}")
    return coords


@benchmark
async def test_geocode_destination():
    """Test 1b: Geocode destination address"""
    print("\n=== TEST 1b: Geocode Destination ===")
    address = "Ferry Building, San Francisco"
    print(f"Geocoding: {address}")
    coords = await geocode_address(address)
    if not coords:
        raise Exception(f"Failed to geocode: {address}")
    print(f"Result: {coords}")
    return coords


@benchmark
async def test_graphhopper_simple_route(origin, destination):
    """Test 2a: GraphHopper single route request"""
    print("\n=== TEST 2a: GraphHopper Single Route ===")
    print(f"Origin: {origin}")
    print(f"Destination: {destination}")

    import requests
    url = "https://graphhopper.com/api/1/route"
    params = {
        "point": [f"{origin['lat']},{origin['lng']}", f"{destination['lat']},{destination['lng']}"],
        "vehicle": "foot",
        "locale": "en",
        "points_encoded": "false",
        "key": GRAPHHOPPER_API_KEY
    }

    print(f"Making request to: {url}")
    response = requests.get(url, params=params, timeout=10)
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print(f"Response: {response.text}")
        raise Exception(f"GraphHopper API error: {response.status_code}")

    data = response.json()
    if not data.get("paths"):
        raise Exception("No paths returned")

    print(f"Paths returned: {len(data['paths'])}")
    path = data['paths'][0]
    print(f"Distance: {path['distance']}m")
    print(f"Time: {path['time']}ms")
    print(f"Points: {len(path['points']['coordinates'])}")
    return data


@benchmark
async def test_graphhopper_alternative_routes(origin, destination):
    """Test 2b: GraphHopper alternative routes request"""
    print("\n=== TEST 2b: GraphHopper Alternative Routes ===")
    print(f"Origin: {origin}")
    print(f"Destination: {destination}")

    import requests
    url = "https://graphhopper.com/api/1/route"
    params = {
        "point": [f"{origin['lat']},{origin['lng']}", f"{destination['lat']},{destination['lng']}"],
        "vehicle": "foot",
        "locale": "en",
        "points_encoded": "false",
        "algorithm": "alternative_route",
        "alternative_route.max_paths": "5",
        "key": GRAPHHOPPER_API_KEY
    }

    print(f"Making request to: {url}")
    response = requests.get(url, params=params, timeout=15)
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print(f"Response: {response.text}")
        raise Exception(f"GraphHopper API error: {response.status_code}")

    data = response.json()
    if not data.get("paths"):
        raise Exception("No alternative paths returned")

    print(f"Alternative paths returned: {len(data['paths'])}")
    for i, path in enumerate(data['paths']):
        print(f"  Route {i+1}: {path['distance']}m, {path['time']}ms, {len(path['points']['coordinates'])} points")
    return data


@benchmark
async def test_get_routes_function(origin, destination):
    """Test 2c: get_graphhopper_routes function"""
    print("\n=== TEST 2c: get_graphhopper_routes Function ===")
    routes = await get_graphhopper_routes(origin, destination, num_routes=10)
    if not routes:
        raise Exception("get_graphhopper_routes returned empty list")
    print(f"Routes generated: {len(routes)}")
    for i, route in enumerate(routes):
        print(f"  Route {i+1}: {route['distance']}m, {route['time']}ms, {len(route['coordinates'])} coords")
    return routes


@benchmark
def test_data_fetcher():
    """Test 3: DataSFetcher incident data retrieval"""
    print("\n=== TEST 3: DataSFetcher ===")
    fetcher = DataSFetcher()
    data = fetcher.get_data()

    print(f"Crime incidents: {len(data['crime_data'])}")
    print(f"311 incidents: {len(data['incidents_311'])}")

    if len(data['crime_data']) > 0:
        sample = data['crime_data'][0]
        print(f"Sample crime incident: {sample.get('category', 'N/A')}")

    return data


@benchmark
def test_risk_scorer_initialization():
    """Test 4a: RiskScorer initialization"""
    print("\n=== TEST 4a: RiskScorer Initialization ===")
    scorer = RiskScorer()
    print(f"RiskScorer created successfully")
    return scorer


@benchmark
def test_risk_calculation(scorer, routes, incident_data):
    """Test 4b: Risk calculation for routes"""
    print("\n=== TEST 4b: Risk Calculation ===")

    if not routes:
        raise Exception("No routes to analyze")

    route = routes[0]
    path_coords = [{"lat": lat, "lng": lng} for lat, lng in route["coordinates"]]

    print(f"Analyzing route with {len(path_coords)} coordinates")
    print(f"Crime incidents: {len(incident_data['crime_data'])}")
    print(f"311 incidents: {len(incident_data['incidents_311'])}")

    analysis = scorer.analyze_route(
        path_coords,
        incident_data['crime_data'],
        incident_data['incidents_311']
    )

    print(f"Total risk: {analysis['total_risk']:.2f}")
    print(f"Crime risk: {analysis['crime_risk']:.2f}")
    print(f"Incident risk: {analysis['incident_risk']:.2f}")

    return analysis


@benchmark
def test_safety_score_calculation(total_risk):
    """Test 5: Safety score conversion"""
    print("\n=== TEST 5: Safety Score Calculation ===")
    import math

    if total_risk == 0:
        safety_score = 100
    else:
        safety_score = int(100 * math.exp(-total_risk / 10))
        safety_score = max(0, min(100, safety_score))

    print(f"Total risk: {total_risk:.2f}")
    print(f"Safety score: {safety_score}/100")

    return safety_score


async def run_all_tests():
    """Run all pipeline tests in sequence"""
    print("="*60)
    print("ROUTE CALCULATION PIPELINE TESTS")
    print("="*60)

    results = {}

    try:
        # Test 0: API Key
        await test_api_key()

        # Test 1: Geocoding
        origin = await test_geocode_origin()
        results['origin'] = origin

        destination = await test_geocode_destination()
        results['destination'] = destination

        # Test 2: GraphHopper routing
        await test_graphhopper_simple_route(origin, destination)
        await test_graphhopper_alternative_routes(origin, destination)
        routes = await test_get_routes_function(origin, destination)
        results['routes'] = routes

        # Test 3: Data fetching
        incident_data = test_data_fetcher()
        results['incident_data'] = incident_data

        # Test 4: Risk scoring
        scorer = test_risk_scorer_initialization()
        analysis = test_risk_calculation(scorer, routes, incident_data)
        results['analysis'] = analysis

        # Test 5: Safety score
        safety_score = test_safety_score_calculation(analysis['total_risk'])
        results['safety_score'] = safety_score

        print("\n" + "="*60)
        print("ALL TESTS PASSED")
        print("="*60)

        return results

    except Exception as e:
        print("\n" + "="*60)
        print(f"TEST SUITE FAILED: {str(e)}")
        print("="*60)
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(run_all_tests())
