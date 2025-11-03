"""
SafePath Production Readiness Test Suite
Comprehensive testing including data accuracy, performance, and load testing
"""
import requests
import time
import json
import statistics
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

API_BASE = "http://localhost:8000"

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.performance_metrics = {}

    def add_pass(self, test_name: str, details: str = ""):
        self.passed.append(f"PASS: {test_name}" + (f" - {details}" if details else ""))

    def add_fail(self, test_name: str, reason: str):
        self.failed.append(f"FAIL: {test_name} - {reason}")

    def add_warning(self, test_name: str, reason: str):
        self.warnings.append(f"WARN: {test_name} - {reason}")

    def add_metric(self, metric_name: str, value: float):
        self.performance_metrics[metric_name] = value

    def print_summary(self):
        print("\n" + "="*80)
        print("PRODUCTION READINESS TEST SUMMARY")
        print("="*80)
        print(f"Passed: {len(self.passed)}")
        print(f"Failed: {len(self.failed)}")
        print(f"Warnings: {len(self.warnings)}")

        total_tests = len(self.passed) + len(self.failed)
        if total_tests > 0:
            pass_rate = (len(self.passed) / total_tests) * 100
            print(f"Pass Rate: {pass_rate:.1f}%")
            print(f"Production Ready: {'YES' if pass_rate >= 90 and len(self.failed) == 0 else 'NO'}")
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

        if self.performance_metrics:
            print("PERFORMANCE METRICS:")
            for metric, value in self.performance_metrics.items():
                print(f"  {metric}: {value:.3f}s")
            print()

results = TestResults()

# ============================================================================
# TEST SUITE 1: BASIC API VERIFICATION
# ============================================================================

def test_health_endpoint():
    """Test /api/health endpoint"""
    print("\n[1] Testing Health Endpoint...")
    try:
        start = time.time()
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                results.add_pass("Health Endpoint", f"Response: {elapsed:.3f}s")
                results.add_metric("health_endpoint_time", elapsed)

                # Verify data counts
                crime_count = data.get("crime_incidents", 0)
                incident_count = data.get("311_incidents", 0)

                if crime_count > 0 and incident_count > 0:
                    results.add_pass("Data Availability", f"{crime_count} crimes, {incident_count} 311 incidents")
                else:
                    results.add_warning("Data Availability", "Some data sources may be empty")
            else:
                results.add_fail("Health Endpoint", f"Status: {data.get('status')}")
        else:
            results.add_fail("Health Endpoint", f"HTTP {response.status_code}")
    except Exception as e:
        results.add_fail("Health Endpoint", str(e))

def test_invalid_input_validation():
    """Test input validation for invalid addresses"""
    print("\n[2] Testing Input Validation...")

    test_cases = [
        ("asdfghjkl", "qwertyuiop", "Gibberish addresses"),
        ("", "Ferry Building, SF", "Empty origin"),
        ("Union Square, SF", "", "Empty destination"),
        ("123!@#$", "^&*()", "Special characters only"),
    ]

    for origin, dest, description in test_cases:
        try:
            response = requests.post(
                f"{API_BASE}/api/routes",
                json={"origin": origin, "destination": dest},
                timeout=10
            )

            if response.status_code == 400:
                results.add_pass(f"Invalid Input: {description}", "HTTP 400 returned")
            else:
                results.add_fail(f"Invalid Input: {description}", f"Expected 400, got {response.status_code}")
        except requests.Timeout:
            results.add_warning(f"Invalid Input: {description}", "Request timeout")
        except Exception as e:
            results.add_fail(f"Invalid Input: {description}", str(e))

# ============================================================================
# TEST SUITE 2: DATA ACCURACY & ROUTE CALCULATION
# ============================================================================

def test_route_calculation_accuracy():
    """Test route calculation with known San Francisco locations"""
    print("\n[3] Testing Route Calculation Accuracy...")

    test_routes = [
        ("Union Square, San Francisco", "Ferry Building, San Francisco", "Short route"),
        ("Civic Center, San Francisco", "Mission Dolores Park, San Francisco", "Medium route"),
    ]

    for origin, dest, description in test_routes:
        try:
            start = time.time()
            response = requests.post(
                f"{API_BASE}/api/routes",
                json={"origin": origin, "destination": dest},
                timeout=15
            )
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                routes = data.get("routes", [])

                # Verify exactly 2 routes
                if len(routes) == 2:
                    results.add_pass(f"Route Count: {description}", "Returns exactly 2 routes")
                else:
                    results.add_fail(f"Route Count: {description}", f"Expected 2 routes, got {len(routes)}")

                # Verify route names
                if len(routes) >= 2:
                    if routes[0]["name"] == "Safest Route" and routes[1]["name"] == "Balanced Route":
                        results.add_pass(f"Route Names: {description}", "Correct naming")
                    else:
                        results.add_fail(f"Route Names: {description}", f"Got: {routes[0]['name']}, {routes[1]['name']}")

                # Verify safety scores
                for route in routes:
                    score = route.get("safetyScore", -1)
                    if 0 <= score <= 100:
                        results.add_pass(f"Safety Score Range: {route['name']}", f"Score: {score}/100")
                    else:
                        results.add_fail(f"Safety Score Range: {route['name']}", f"Invalid score: {score}")

                # Verify risk components
                for route in routes:
                    total_risk = route.get("total_risk", -1)
                    crime_risk = route.get("crime_risk", -1)
                    incident_risk = route.get("incident_risk", -1)

                    if total_risk >= 0 and crime_risk >= 0 and incident_risk >= 0:
                        # Verify total_risk approximately equals crime_risk + incident_risk
                        calculated_total = crime_risk + incident_risk
                        if abs(total_risk - calculated_total) < 0.1:
                            results.add_pass(f"Risk Calculation: {route['name']}", f"Total: {total_risk:.2f}")
                        else:
                            results.add_fail(f"Risk Calculation: {route['name']}",
                                           f"Total {total_risk:.2f} != Crime {crime_risk:.2f} + Incident {incident_risk:.2f}")
                    else:
                        results.add_fail(f"Risk Values: {route['name']}", "Negative risk values")

                # Verify coordinates exist
                for route in routes:
                    coords = route.get("coordinates", [])
                    if len(coords) > 0:
                        results.add_pass(f"Route Coordinates: {route['name']}", f"{len(coords)} points")
                    else:
                        results.add_fail(f"Route Coordinates: {route['name']}", "No coordinates")

                results.add_metric(f"route_calculation_{description.replace(' ', '_')}", elapsed)

            elif response.status_code == 400:
                results.add_fail(f"Route Calculation: {description}", "HTTP 400 for valid addresses")
            else:
                results.add_fail(f"Route Calculation: {description}", f"HTTP {response.status_code}")

        except requests.Timeout:
            results.add_warning(f"Route Calculation: {description}", "Request timeout (>15s)")
        except Exception as e:
            results.add_fail(f"Route Calculation: {description}", str(e))

def test_route_selection_logic():
    """Verify safest route has lowest risk"""
    print("\n[4] Testing Route Selection Logic...")

    try:
        response = requests.post(
            f"{API_BASE}/api/routes",
            json={
                "origin": "Golden Gate Park, San Francisco",
                "destination": "Ocean Beach, San Francisco"
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            routes = data.get("routes", [])

            if len(routes) >= 2:
                safest = routes[0]
                balanced = routes[1]

                # Verify safest route has lowest risk
                if safest["total_risk"] <= balanced["total_risk"]:
                    results.add_pass("Route Selection", f"Safest: {safest['total_risk']:.2f}, Balanced: {balanced['total_risk']:.2f}")
                else:
                    results.add_fail("Route Selection",
                                   f"Safest ({safest['total_risk']:.2f}) has higher risk than Balanced ({balanced['total_risk']:.2f})")

                # Verify safest route has highest safety score
                if safest["safetyScore"] >= balanced["safetyScore"]:
                    results.add_pass("Safety Score Order", f"Safest: {safest['safetyScore']}, Balanced: {balanced['safetyScore']}")
                else:
                    results.add_fail("Safety Score Order", "Safest route has lower safety score")
        else:
            results.add_warning("Route Selection Logic", f"HTTP {response.status_code}")

    except requests.Timeout:
        results.add_warning("Route Selection Logic", "Request timeout")
    except Exception as e:
        results.add_fail("Route Selection Logic", str(e))

# ============================================================================
# TEST SUITE 3: PERFORMANCE TESTING
# ============================================================================

def test_response_time_baselines():
    """Test response time for different endpoints"""
    print("\n[5] Testing Response Time Baselines...")

    # Health endpoint
    try:
        times = []
        for i in range(5):
            start = time.time()
            response = requests.get(f"{API_BASE}/api/health", timeout=5)
            elapsed = time.time() - start
            if response.status_code == 200:
                times.append(elapsed)

        if times:
            avg_time = statistics.mean(times)
            if avg_time < 0.1:
                results.add_pass("Health Endpoint Performance", f"Avg: {avg_time:.3f}s (target: <0.1s)")
            else:
                results.add_warning("Health Endpoint Performance", f"Avg: {avg_time:.3f}s (target: <0.1s)")
            results.add_metric("health_avg_response", avg_time)
    except Exception as e:
        results.add_fail("Health Endpoint Performance", str(e))

    # Stats endpoint
    try:
        start = time.time()
        response = requests.get(f"{API_BASE}/api/data/stats", timeout=5)
        elapsed = time.time() - start

        if response.status_code == 200:
            if elapsed < 0.5:
                results.add_pass("Stats Endpoint Performance", f"{elapsed:.3f}s (target: <0.5s)")
            else:
                results.add_warning("Stats Endpoint Performance", f"{elapsed:.3f}s (target: <0.5s)")
            results.add_metric("stats_response", elapsed)
    except Exception as e:
        results.add_fail("Stats Endpoint Performance", str(e))

    # Route calculation (short distance)
    try:
        start = time.time()
        response = requests.post(
            f"{API_BASE}/api/routes",
            json={"origin": "Union Square, SF", "destination": "Ferry Building, SF"},
            timeout=20
        )
        elapsed = time.time() - start

        if response.status_code == 200:
            if elapsed < 10:
                results.add_pass("Short Route Performance", f"{elapsed:.3f}s (target: <10s)")
            else:
                results.add_warning("Short Route Performance", f"{elapsed:.3f}s (target: <10s)")
            results.add_metric("short_route_response", elapsed)
    except requests.Timeout:
        results.add_fail("Short Route Performance", "Timeout (>20s)")
    except Exception as e:
        results.add_fail("Short Route Performance", str(e))

# ============================================================================
# TEST SUITE 4: LOAD TESTING (CONCURRENT USERS)
# ============================================================================

def make_route_request(request_id: int) -> Tuple[int, float, int]:
    """Make a single route request and return (id, time, status_code)"""
    try:
        start = time.time()
        response = requests.post(
            f"{API_BASE}/api/routes",
            json={
                "origin": "Union Square, San Francisco",
                "destination": "Ferry Building, San Francisco"
            },
            timeout=30
        )
        elapsed = time.time() - start
        return (request_id, elapsed, response.status_code)
    except requests.Timeout:
        return (request_id, 30.0, 408)  # Request Timeout
    except Exception as e:
        return (request_id, -1, 500)

def test_concurrent_load(num_users: int):
    """Test concurrent user load"""
    print(f"\n[6] Testing Load: {num_users} Concurrent Users...")

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(make_route_request, i) for i in range(num_users)]
        results_list = []

        for future in as_completed(futures):
            results_list.append(future.result())

    total_time = time.time() - start_time

    # Analyze results
    successful = [r for r in results_list if r[2] == 200]
    failed = [r for r in results_list if r[2] != 200]
    timeouts = [r for r in results_list if r[2] == 408]

    success_rate = (len(successful) / num_users) * 100

    if len(successful) > 0:
        response_times = [r[1] for r in successful]
        avg_response = statistics.mean(response_times)
        p95_response = sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 1 else response_times[0]

        print(f"  Success Rate: {success_rate:.1f}% ({len(successful)}/{num_users})")
        print(f"  Avg Response: {avg_response:.2f}s")
        print(f"  P95 Response: {p95_response:.2f}s")
        print(f"  Total Time: {total_time:.2f}s")

        if success_rate >= 80:
            results.add_pass(f"Load Test: {num_users} users",
                           f"Success: {success_rate:.1f}%, Avg: {avg_response:.2f}s, P95: {p95_response:.2f}s")
        else:
            results.add_fail(f"Load Test: {num_users} users",
                           f"Success rate {success_rate:.1f}% (target: ≥80%)")

        results.add_metric(f"load_{num_users}_users_avg", avg_response)
        results.add_metric(f"load_{num_users}_users_p95", p95_response)
    else:
        results.add_fail(f"Load Test: {num_users} users", "All requests failed")

    if len(timeouts) > 0:
        results.add_warning(f"Load Test: {num_users} users", f"{len(timeouts)} timeouts")

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def run_all_tests():
    """Execute all test suites"""
    print("="*80)
    print("SAFEPATH PRODUCTION READINESS TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Suite 1: Basic API Verification
    print("\n" + "="*80)
    print("SUITE 1: API VERIFICATION")
    print("="*80)
    test_health_endpoint()
    test_invalid_input_validation()

    # Suite 2: Data Accuracy
    print("\n" + "="*80)
    print("SUITE 2: DATA ACCURACY & ROUTE CALCULATION")
    print("="*80)
    test_route_calculation_accuracy()
    test_route_selection_logic()

    # Suite 3: Performance
    print("\n" + "="*80)
    print("SUITE 3: PERFORMANCE TESTING")
    print("="*80)
    test_response_time_baselines()

    # Suite 4: Load Testing
    print("\n" + "="*80)
    print("SUITE 4: LOAD TESTING")
    print("="*80)
    test_concurrent_load(5)   # 5 concurrent users
    test_concurrent_load(10)  # 10 concurrent users
    test_concurrent_load(20)  # 20 concurrent users

    # Print final summary
    results.print_summary()

    # Save results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f"test_results_{timestamp}.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "passed": len(results.passed),
            "failed": len(results.failed),
            "warnings": len(results.warnings),
            "pass_rate": len(results.passed)/(len(results.passed)+len(results.failed))*100 if (len(results.passed)+len(results.failed)) > 0 else 0,
            "metrics": results.performance_metrics,
            "details": {
                "passed": results.passed,
                "failed": results.failed,
                "warnings": results.warnings
            }
        }, f, indent=2)

    print(f"\nDetailed results saved to: test_results_{timestamp}.json")

if __name__ == "__main__":
    run_all_tests()
