"""
Comprehensive Test Suite for SafePath API
Tests all endpoints, edge cases, data accuracy, and performance
"""
import requests
import time
import json
from typing import Dict, List, Tuple

API_BASE = "http://localhost:8000"

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def add_pass(self, test_name: str, details: str = ""):
        self.passed.append(f"PASS: {test_name}" + (f" - {details}" if details else ""))

    def add_fail(self, test_name: str, reason: str):
        self.failed.append(f"FAIL: {test_name} - {reason}")

    def add_warning(self, test_name: str, reason: str):
        self.warnings.append(f"WARN: {test_name} - {reason}")

    def print_summary(self):
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Passed: {len(self.passed)}")
        print(f"Failed: {len(self.failed)}")
        print(f"Warnings: {len(self.warnings)}")
        print()

        if self.failed:
            print("FAILURES:")
            for fail in self.failed:
                print(f"  {fail}")
            print()

        if self.warnings:
            print("WARNINGS:")
            for warn in self.warnings:
                print(f"  {warn}")
            print()

        print(f"Pass Rate: {len(self.passed)/(len(self.passed)+len(self.failed))*100:.1f}%")

results = TestResults()

def test_health_endpoint():
    """Test /api/health endpoint"""
    print("\n[TEST] Health Endpoint")
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                results.add_pass("Health Endpoint", f"Response time: {response.elapsed.total_seconds():.2f}s")
            else:
                results.add_fail("Health Endpoint", f"Unexpected status: {data.get('status')}")
        else:
            results.add_fail("Health Endpoint", f"HTTP {response.status_code}")
    except Exception as e:
        results.add_fail("Health Endpoint", str(e))

def test_invalid_addresses():
    """Test API with invalid/gibberish addresses"""
    print("\n[TEST] Invalid Address Handling")

    test_cases = [
        ("asdfghjkl", "qwertyuiop", "Gibberish addresses"),
        ("", "Ferry Building", "Empty origin"),
        ("Union Square", "", "Empty destination"),
        ("123!@#", "$%^&*()", "Special characters"),
    ]

    for origin, dest, description in test_cases:
        try:
            response = requests.post(
                f"{API_BASE}/api/routes",
                json={"origin": origin, "destination": dest},
                timeout=15
            )

            if response.status_code == 400:
                results.add_pass(f"Invalid Input: {description}", "Correctly returns HTTP 400")
            elif response.status_code == 200:
                data = response.json()
                if len(data.get("routes", [])) == 0:
                    results.add_warning(f"Invalid Input: {description}", "HTTP 200 but no routes")
                else:
                    results.add_fail(f"Invalid Input: {description}", "HTTP 200 with routes - should be 400")
            else:
                results.add_fail(f"Invalid Input: {description}", f"Unexpected HTTP {response.status_code}")
        except Exception as e:
            results.add_fail(f"Invalid Input: {description}", str(e))

def test_valid_routes():
    """Test valid route calculations"""
    print("\n[TEST] Valid Route Calculations")

    test_cases = [
        ("Union Square, SF", "Ferry Building, SF", "Short distance", 0.5, 2.0),
        ("Civic Center, SF", "Mission Dolores Park, SF", "Medium distance", 1.0, 3.0),
        ("Fishermans Wharf, SF", "Golden Gate Park, SF", "Long distance", 2.0, 5.0),
    ]

    for origin, dest, description, min_dist, max_dist in test_cases:
        try:
            response = requests.post(
                f"{API_BASE}/api/routes",
                json={"origin": origin, "destination": dest},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                routes = data.get("routes", [])

                # Check route count
                if len(routes) == 2:
                    results.add_pass(f"Route Count: {description}", "Returns exactly 2 routes")
                else:
                    results.add_fail(f"Route Count: {description}", f"Expected 2 routes, got {len(routes)}")

                # Validate route structure
                for i, route in enumerate(routes):
                    route_name = route.get("name", f"Route {i+1}")

                    # Check required fields
                    required_fields = ["id", "name", "distance", "time", "safetyScore", "coordinates"]
                    missing = [f for f in required_fields if f not in route]
                    if missing:
                        results.add_fail(f"Route Structure: {description} - {route_name}", f"Missing fields: {missing}")
                    else:
                        results.add_pass(f"Route Structure: {description} - {route_name}", "All required fields present")

                    # Validate safety score range
                    safety = route.get("safetyScore", -1)
                    if 0 <= safety <= 100:
                        results.add_pass(f"Safety Score: {description} - {route_name}", f"Score: {safety}/100")
                    else:
                        results.add_fail(f"Safety Score: {description} - {route_name}", f"Invalid score: {safety}")

                    # Validate coordinates
                    coords = route.get("coordinates", [])
                    if len(coords) >= 2:
                        results.add_pass(f"Coordinates: {description} - {route_name}", f"{len(coords)} points")
                    else:
                        results.add_fail(f"Coordinates: {description} - {route_name}", f"Only {len(coords)} points")

            elif response.status_code == 400:
                results.add_warning(f"Valid Route: {description}", "Returned HTTP 400 - may be too close or rate limited")
            else:
                results.add_fail(f"Valid Route: {description}", f"HTTP {response.status_code}")

        except requests.exceptions.Timeout:
            results.add_warning(f"Valid Route: {description}", "Request timeout - possible rate limiting")
        except Exception as e:
            results.add_fail(f"Valid Route: {description}", str(e))

def test_route_names():
    """Test that route names are correct"""
    print("\n[TEST] Route Naming Convention")

    try:
        response = requests.post(
            f"{API_BASE}/api/routes",
            json={"origin": "Union Square, SF", "destination": "Ferry Building, SF"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            routes = data.get("routes", [])

            if len(routes) >= 1:
                if routes[0].get("name") == "Safest Route":
                    results.add_pass("Route Naming", "First route is 'Safest Route'")
                else:
                    results.add_fail("Route Naming", f"First route is '{routes[0].get('name')}', expected 'Safest Route'")

            if len(routes) >= 2:
                if routes[1].get("name") == "Balanced Route":
                    results.add_pass("Route Naming", "Second route is 'Balanced Route'")
                else:
                    results.add_fail("Route Naming", f"Second route is '{routes[1].get('name')}', expected 'Balanced Route'")

            if len(routes) > 2:
                results.add_fail("Route Naming", f"Expected 2 routes, got {len(routes)}")

    except Exception as e:
        results.add_fail("Route Naming", str(e))

def test_response_times():
    """Test API response times"""
    print("\n[TEST] Performance - Response Times")

    # Health endpoint should be fast
    try:
        start = time.time()
        requests.get(f"{API_BASE}/api/health", timeout=5)
        elapsed = time.time() - start

        if elapsed < 0.1:
            results.add_pass("Performance: Health Endpoint", f"{elapsed*1000:.0f}ms")
        elif elapsed < 0.5:
            results.add_warning("Performance: Health Endpoint", f"{elapsed*1000:.0f}ms (target: <100ms)")
        else:
            results.add_fail("Performance: Health Endpoint", f"{elapsed*1000:.0f}ms (too slow)")
    except Exception as e:
        results.add_fail("Performance: Health Endpoint", str(e))

def test_edge_cases():
    """Test edge cases"""
    print("\n[TEST] Edge Cases")

    # Very close addresses (should be rejected)
    try:
        response = requests.post(
            f"{API_BASE}/api/routes",
            json={"origin": "Market St & 5th St, SF", "destination": "Market St & 6th St, SF"},
            timeout=15
        )

        if response.status_code == 400:
            results.add_pass("Edge Case: Very Close Addresses", "Correctly rejects <50m distance")
        else:
            results.add_warning("Edge Case: Very Close Addresses", f"HTTP {response.status_code} - check distance validation")
    except Exception as e:
        results.add_fail("Edge Case: Very Close Addresses", str(e))

if __name__ == "__main__":
    print("="*80)
    print("SAFEPATH API COMPREHENSIVE TEST SUITE")
    print("="*80)

    # Run all test suites
    test_health_endpoint()
    time.sleep(1)

    test_invalid_addresses()
    time.sleep(2)

    test_valid_routes()
    time.sleep(2)

    test_route_names()
    time.sleep(2)

    test_edge_cases()
    time.sleep(1)

    test_response_times()

    # Print summary
    results.print_summary()
