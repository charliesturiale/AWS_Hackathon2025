# -*- coding: utf-8 -*-
"""
Risk Scoring Algorithm Module
Implements the path risk calculation with time decay and distance weighting
"""
import numpy as np
from datetime import datetime
from geopy.distance import geodesic
from typing import List, Dict, Tuple, Any
import math

class RiskScorer:
    """Calculate risk scores for walking paths"""

    @staticmethod
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

    # Risk weight mapping based on incident type
    CRIME_RISK_WEIGHTS = {
        # High risk (w=3): 72-hour decay
        "EXPLOSIVE FOUND": 3,
        "EXPLOSION": 3,
        "ROBBERY": 3,
        "STRONGARM ROBBERY": 3,
        "ASSAULT": 3,
        "BATTERY": 3,

        # Medium risk (w=2): 24-hour decay
        "PURSE SNATCH": 2,
        "INDECENT EXPOSURE": 2,
        "FIGHT W/WEAPONS": 2,
        "FIGHT NO WEAPON": 2,
        "PERSON BREAKING IN": 2,
        "BURGLARY": 2,

        # Low risk (w=1): 24-hour decay
        "SUSPICIOUS PERSON": 1,
        "THREATS / HARASSMENT": 1,
        "THREATS": 1,
        "HARASSMENT": 1,
    }

    INCIDENT_311_RISK_WEIGHTS = {
        # Low risk (w=1): No time decay for open encampments
        "ENCAMPMENT": 1,
        "ENCAMPMENTS": 1,
        "AGGRESSIVE/THREATENING": 1,
        "AGGRESSIVE": 1,
        "THREATENING": 1,
    }

    # Encampment proximity threshold (0.001 degrees)
    ENCAMPMENT_MERGE_THRESHOLD = 0.001

    def __init__(self):
        self.current_time = datetime.now()

    def assign_risk(self, incident: Dict[str, Any], incident_type: str) -> int:
        """Assign risk weight to an incident"""
        if incident_type == "crime":
            description = incident.get("call_type_original_desc", "").upper()

            for crime_type, weight in self.CRIME_RISK_WEIGHTS.items():
                if crime_type in description:
                    return weight

            return 0

        else:  # 311 data
            service_name = incident.get("service_name", "").upper()

            for incident_name, weight in self.INCIDENT_311_RISK_WEIGHTS.items():
                if incident_name in service_name:
                    return weight

            return 0

    def min_distance_to_path(self, incident_coords: Tuple[float, float], path: List[Tuple[float, float]]) -> float:
        """Calculate minimum distance from incident to path"""
        if len(path) < 2:
            return float('inf')

        # Validate incident coordinates
        if not self.validate_coordinates(incident_coords[0], incident_coords[1]):
            return float('inf')

        min_dist = float('inf')

        for path_point in path:
            try:
                # Validate path point coordinates before calculating distance
                if not self.validate_coordinates(path_point[0], path_point[1]):
                    continue

                dist = geodesic(incident_coords, path_point).kilometers
                min_dist = min(min_dist, dist)
            except Exception as e:
                # Log the error but continue processing other points
                continue

        return min_dist

    def calculate_time_since_incident(self, incident_time_str: str, current_time: datetime = None) -> float:
        """Calculate hours since incident"""
        if current_time is None:
            current_time = self.current_time

        try:
            # Validate input
            if not incident_time_str or not isinstance(incident_time_str, str):
                return 0.0

            # Handle various ISO 8601 datetime formats
            time_str = incident_time_str.replace('Z', '+00:00').replace('.000', '')

            # Try parsing with fromisoformat
            try:
                incident_time = datetime.fromisoformat(time_str)
            except ValueError:
                # Fallback: try removing timezone info
                time_str = incident_time_str.replace('Z', '').replace('.000', '').split('+')[0].split('-')[0]
                incident_time = datetime.fromisoformat(time_str)

            time_diff = current_time - incident_time
            hours = time_diff.total_seconds() / 3600
            return max(0, hours)
        except Exception as e:
            return 0

    def filter_closed_encampments(self, incidents_311: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out closed encampments before merging"""
        filtered = []

        for incident in incidents_311:
            service_name = incident.get("service_name", "").upper()
            is_encampment = "ENCAMPMENT" in service_name

            if is_encampment:
                status = incident.get("status_description", "").upper()
                if status == "CLOSED":
                    continue  # Skip closed encampments

            filtered.append(incident)

        return filtered

    def merge_nearby_encampments(self, incidents_311: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge encampments within 0.001 degrees"""
        encampments = []
        other_incidents = []

        for incident in incidents_311:
            service_name = incident.get("service_name", "").upper()
            if "ENCAMPMENT" in service_name:
                point_geom = incident.get("point_geom", {})
                coords = point_geom.get("coordinates", [])

                if len(coords) >= 2:
                    incident["_lat"] = coords[1]
                    incident["_lng"] = coords[0]
                    encampments.append(incident)
            else:
                other_incidents.append(incident)

        merged = []
        used = set()

        for i, enc1 in enumerate(encampments):
            if i in used:
                continue

            cluster = [enc1]
            used.add(i)

            for j, enc2 in enumerate(encampments):
                if j in used:
                    continue

                lat_diff = abs(enc1["_lat"] - enc2["_lat"])
                lng_diff = abs(enc1["_lng"] - enc2["_lng"])

                if lat_diff <= self.ENCAMPMENT_MERGE_THRESHOLD and lng_diff <= self.ENCAMPMENT_MERGE_THRESHOLD:
                    cluster.append(enc2)
                    used.add(j)

            if len(cluster) > 1:
                cluster.sort(key=lambda x: x.get("requested_datetime", ""), reverse=True)
                merged_enc = cluster[0].copy()
                merged_enc["_merged_count"] = len(cluster)
                merged.append(merged_enc)
            else:
                merged.append(enc1)

        print(f"Merged {len(encampments)} encampments into {len(merged)}")

        return merged + other_incidents

    def calculate_risk_score(self, path: List[Tuple[float, float]], incidents: List[Dict[str, Any]], incident_type: str, current_time: datetime = None) -> float:
        """
        Calculate total risk score for a path using the mathematical formula:

        For high-risk incidents (w=3, 72-hour decay):
            f(d,t,w) = (ReLU(3 - 3t/72))^2 * e^(-d^2/0.02)

        For medium/low-risk incidents (w=1,2, 24-hour decay):
            f(d,t,w) = (ReLU(w - wt/24))^2 * e^(-d^2/0.02)

        For encampments (no time decay):
            f(d,w) = w^2 * e^(-d^2/0.02)

        Where:
            - w = risk weight (1=low, 2=medium, 3=high)
            - d = minimum distance from incident to route (km)
            - t = time since incident occurred (hours)
            - ReLU(x) = max(0, x)

        Total risk = sum of all incident risk contributions
        """
        if current_time is None:
            current_time = self.current_time

        total_risk = 0.0

        for incident in incidents:
            if incident_type == "crime":
                coords = incident.get("intersection_point", {}).get("coordinates", [])
                if len(coords) < 2:
                    continue
                incident_coords = (coords[1], coords[0])
                time_field = "entry_datetime"
            else:
                point_geom = incident.get("point_geom", {})
                if point_geom:
                    coords = point_geom.get("coordinates", [])
                    if len(coords) < 2:
                        continue
                    incident_coords = (coords[1], coords[0])
                else:
                    continue
                time_field = "requested_datetime"

            w = self.assign_risk(incident, incident_type)
            if w == 0:
                continue

            d = self.min_distance_to_path(incident_coords, path)

            if incident_type == "311":
                service_name = incident.get("service_name", "").upper()
                is_encampment = "ENCAMPMENT" in service_name
            else:
                description = incident.get("call_type_original_desc", "").upper()
                is_encampment = "ENCAMPMENT" in description

            incident_time_str = incident.get(time_field, "")
            t = self.calculate_time_since_incident(incident_time_str, current_time)

            if is_encampment:
                relu_term = w
            elif w == 3:
                relu_term = max(0, 3 - 3*t/72)
            else:
                relu_term = max(0, w - w*t/24)

            distance_factor = np.exp(-(d ** 2) / 0.02)
            risk_value = (relu_term ** 2) * distance_factor

            total_risk += risk_value

        return total_risk

    def analyze_route(self, path_coords: List[Dict[str, float]], crime_data: List[Dict[str, Any]], incidents_311: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a route and calculate risk score"""
        path = [(coord["lat"], coord["lng"]) for coord in path_coords]

        # Filter closed encampments BEFORE merging
        incidents_311_filtered = self.filter_closed_encampments(incidents_311)

        # Then merge nearby encampments
        incidents_311_merged = self.merge_nearby_encampments(incidents_311_filtered)

        crime_risk = self.calculate_risk_score(path, crime_data, "crime", self.current_time)
        incident_risk = self.calculate_risk_score(path, incidents_311_merged, "311", self.current_time)

        total_risk = crime_risk + incident_risk

        return {
            "total_risk": total_risk,
            "crime_risk": crime_risk,
            "incident_risk": incident_risk,
            "risk_breakdown": {
                "crime_count": len(crime_data),
                "incident_count": len(incidents_311),
                "filtered_incidents": len(incidents_311_filtered),
                "merged_incidents": len(incidents_311_merged)
            }
        }

    def calculate_path_length(self, path: List[Tuple[float, float]]) -> float:
        """Calculate total path length in kilometers"""
        if len(path) < 2:
            return 0.0

        total_length = 0.0
        for i in range(len(path) - 1):
            dist = geodesic(path[i], path[i+1]).kilometers
            total_length += dist

        return total_length

    def find_nearby_incidents(self, path: List[Tuple[float, float]], incidents: List[Dict[str, Any]],
                             incident_type: str, radius_km: float = 0.118) -> List[Dict[str, Any]]:
        """
        Find incidents within radius of path that contribute significant risk.
        Danger radius = 118m where distance decay = 50% (e^(-d^2/0.02) = 0.5)
        """
        nearby = []

        for incident in incidents:
            # Get incident coordinates
            if incident_type == "crime":
                coords = incident.get("intersection_point", {}).get("coordinates", [])
            else:  # 311
                point_geom = incident.get("point_geom", {})
                coords = point_geom.get("coordinates", []) if point_geom else []

            if not coords or len(coords) != 2:
                continue

            incident_coords = (float(coords[1]), float(coords[0]))  # (lat, lng)
            min_dist = self.min_distance_to_path(incident_coords, path)
            weight = self.assign_risk(incident, incident_type)

            if min_dist <= radius_km and weight > 0:
                # Calculate risk contribution from this incident
                if incident_type == "311":
                    service_name = incident.get("service_name", "").upper()
                    is_encampment = "ENCAMPMENT" in service_name
                else:
                    description = incident.get("call_type_original_desc", "").upper()
                    is_encampment = "ENCAMPMENT" in description

                incident_time_str = incident.get("requested_datetime" if incident_type == "311" else "entry_datetime", "")
                t = self.calculate_time_since_incident(incident_time_str, self.current_time)

                if is_encampment:
                    relu_term = weight
                elif weight == 3:
                    relu_term = max(0, 3 - 3*t/72)
                else:
                    relu_term = max(0, weight - weight*t/24)

                distance_factor = np.exp(-(min_dist ** 2) / 0.02)
                risk_contribution = (relu_term ** 2) * distance_factor

                nearby.append({
                    'incident': incident,
                    'coords': incident_coords,
                    'min_distance_km': min_dist,
                    'weight': weight,
                    'risk_contribution': risk_contribution,
                    'type': incident_type
                })

        return nearby

    def calculate_segment_risk(self, segment_path: List[Tuple[float, float]], crime_data: List[Dict[str, Any]],
                               incidents_311: List[Dict[str, Any]]) -> float:
        """Calculate total risk for a specific path segment"""
        crime_risk = self.calculate_risk_score(segment_path, crime_data, "crime", self.current_time)
        incident_risk = self.calculate_risk_score(segment_path, incidents_311, "311", self.current_time)
        return crime_risk + incident_risk

    def find_incidents_within_buffer(self, route_coords: List[Tuple[float, float]],
                                     crime_data: List[Dict[str, Any]], incidents_311: List[Dict[str, Any]],
                                     buffer_distance_km: float = 0.20) -> Tuple[List[Dict], float]:
        """
        Find all incidents within buffer distance of route segment.

        Args:
            route_coords: List of (lat, lng) tuples for segment
            crime_data: Crime incident data
            incidents_311: 311 incident data
            buffer_distance_km: Safety buffer distance (default 200m)

        Returns:
            Tuple of (list of incidents within buffer, minimum distance to closest incident)
        """
        incidents_within_buffer = []
        min_distance_overall = float('inf')

        # Check crime incidents
        for crime in crime_data:
            coords = crime.get("intersection_point", {}).get("coordinates", [])
            if len(coords) < 2:
                continue
            incident_coords = (coords[1], coords[0])

            min_dist = self.min_distance_to_path(incident_coords, route_coords)
            min_distance_overall = min(min_distance_overall, min_dist)

            if min_dist <= buffer_distance_km:
                weight = self.assign_risk(crime, "crime")
                if weight > 0:
                    incidents_within_buffer.append({
                        'incident': crime,
                        'coords': incident_coords,
                        'min_distance_km': min_dist,
                        'weight': weight,
                        'type': 'crime'
                    })

        # Check 311 incidents
        for incident in incidents_311:
            point_geom = incident.get("point_geom", {})
            coords = point_geom.get("coordinates", []) if point_geom else []
            if len(coords) < 2:
                continue
            incident_coords = (coords[1], coords[0])

            min_dist = self.min_distance_to_path(incident_coords, route_coords)
            min_distance_overall = min(min_distance_overall, min_dist)

            if min_dist <= buffer_distance_km:
                weight = self.assign_risk(incident, "311")
                if weight > 0:
                    incidents_within_buffer.append({
                        'incident': incident,
                        'coords': incident_coords,
                        'min_distance_km': min_dist,
                        'weight': weight,
                        'type': '311'
                    })

        return incidents_within_buffer, min_distance_overall

    def identify_problematic_segments(self, route_coords: List[Tuple[float, float]], crime_data: List[Dict[str, Any]],
                                     incidents_311: List[Dict[str, Any]], threshold_distance_km: float = 0.20,
                                     depth: int = 0, max_depth: int = 7) -> List[Dict[str, Any]]:
        """
        Recursively subdivide route to find segments passing too close to incidents.
        NOW USES DISTANCE-BASED DETECTION instead of risk-based.

        Args:
            route_coords: List of (lat, lng) tuples
            crime_data: Crime incident data
            incidents_311: 311 incident data
            threshold_distance_km: Minimum safe distance from incidents (default 200m)
            depth: Current recursion depth
            max_depth: Maximum recursion depth

        Returns:
            List of problematic segments that pass within threshold distance of incidents
        """
        # Calculate current segment metrics
        segment_length_km = self.calculate_path_length(route_coords)

        # Find incidents within buffer distance
        incidents_within_buffer, min_distance = self.find_incidents_within_buffer(
            route_coords, crime_data, incidents_311, threshold_distance_km
        )

        # Base case 1: Segment is safe (no incidents within buffer)
        if not incidents_within_buffer or min_distance >= threshold_distance_km:
            return []

        # Base case 2: Can't subdivide further (reached minimum segment size)
        # Minimum: 50m length OR less than 3 points OR max depth reached
        if depth >= max_depth or segment_length_km < 0.05 or len(route_coords) < 3:
            # This is a problematic leaf segment that needs detour
            segment_risk = self.calculate_segment_risk(route_coords, crime_data, incidents_311)

            print(f"    {'  ' * depth}[!] Problematic segment: {len(route_coords)} points, {segment_length_km*1000:.0f}m, "
                  f"{len(incidents_within_buffer)} incidents within {threshold_distance_km*1000:.0f}m (closest: {min_distance*1000:.0f}m)")

            return [{
                'coords': route_coords,
                'risk': segment_risk,
                'length_km': segment_length_km,
                'nearby_incidents': incidents_within_buffer,
                'min_distance_km': min_distance,
                'start': route_coords[0],
                'end': route_coords[-1]
            }]

        # Recursive case: Split and analyze both halves
        midpoint_idx = len(route_coords) // 2
        left_half = route_coords[:midpoint_idx+1]  # Include midpoint in both
        right_half = route_coords[midpoint_idx:]

        # Recurse on both halves
        left_problems = self.identify_problematic_segments(left_half, crime_data, incidents_311,
                                                          threshold_distance_km, depth+1, max_depth)
        right_problems = self.identify_problematic_segments(right_half, crime_data, incidents_311,
                                                            threshold_distance_km, depth+1, max_depth)

        return left_problems + right_problems
