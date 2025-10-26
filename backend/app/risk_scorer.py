"""
Risk Scoring Algorithm Module
Implements the path risk calculation with time decay and distance weighting
"""
import numpy as np
from datetime import datetime
from geopy.distance import geodesic
from typing import List, Dict, Tuple, Any

class RiskScorer:
    """Calculate risk scores for walking paths"""

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

        min_dist = float('inf')

        for path_point in path:
            try:
                dist = geodesic(incident_coords, path_point).kilometers
                min_dist = min(min_dist, dist)
            except:
                continue

        return min_dist

    def calculate_time_since_incident(self, incident_time_str: str, current_time: datetime = None) -> float:
        """Calculate hours since incident"""
        if current_time is None:
            current_time = self.current_time

        try:
            incident_time = datetime.fromisoformat(incident_time_str.replace('Z', '+00:00').replace('.000', ''))
            time_diff = current_time - incident_time
            hours = time_diff.total_seconds() / 3600
            return max(0, hours)
        except:
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
        """Calculate total risk score for a path"""
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
