"""
SafePath SF - Path Risk Analysis API
Standalone implementation without AWS dependencies
Based on Jupyter notebook analysis
"""

import json
import requests
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from geopy.distance import geodesic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for Vercel frontend

# SF Open Data API endpoints (no API key required!)
CRIME_API_URL = "https://data.sfgov.org/resource/gnap-fj3t.json"
API_311_URL = "https://data.sfgov.org/resource/vw6y-z8j6.json"

# Cache for API data (simple in-memory cache)
data_cache = {
    'crime_data': {'data': [], 'timestamp': None},
    '311_data': {'data': [], 'timestamp': None}
}

CACHE_DURATION = timedelta(hours=1)  # Cache data for 1 hour

def fetch_crime_data():
    """
    Fetch crime data from SF Open Data API
    Specific crime types as defined in the notebook
    """
    # Check cache first
    if data_cache['crime_data']['timestamp']:
        if datetime.now() - data_cache['crime_data']['timestamp'] < CACHE_DURATION:
            logger.info("Using cached crime data")
            return data_cache['crime_data']['data']
    
    query = {
        "$query": """SELECT
  entry_datetime,
  call_type_original_desc,
  call_type_final_desc,
  intersection_name,
  intersection_point
WHERE
  caseless_one_of(
    call_type_original_desc,
    "EXPLOSIVE FOUND",
    "SUSPICIOUS PERSON",
    "FIGHT W/WEAPONS",
    "FIGHT NO WEAPON",
    "ASSAULT / BATTERY DV",
    "PURSE SNATCH",
    "EXPLOSION",
    "ROBBERY",
    "THREATS / HARASSMENT",
    "STRONGARM ROBBERY",
    "INDECENT EXPOSURE",
    "PERSON BREAKING IN",
    "BURGLARY"
  )
ORDER BY entry_datetime DESC NULL LAST""",
        "$limit": 5000
    }
    
    try:
        response = requests.get(CRIME_API_URL, params=query)
        response.raise_for_status()
        crimes = response.json()
        
        # Update cache
        data_cache['crime_data'] = {
            'data': crimes,
            'timestamp': datetime.now()
        }
        
        logger.info(f"Fetched {len(crimes)} crime incidents from SF Open Data")
        return crimes
        
    except Exception as e:
        logger.error(f"Error fetching crime data: {e}")
        return []

def fetch_311_data():
    """
    Fetch 311 data from SF Open Data API
    Focus on Encampment and Aggressive/Threatening reports
    """
    # Check cache first
    if data_cache['311_data']['timestamp']:
        if datetime.now() - data_cache['311_data']['timestamp'] < CACHE_DURATION:
            logger.info("Using cached 311 data")
            return data_cache['311_data']['data']
    
    query = {
        "$query": """SELECT
  requested_datetime,
  status_description,
  service_name,
  service_subtype,
  point_geom
WHERE
  caseless_one_of(
    service_name,
    "Aggressive/Threatening",
    "Encampment",
    "Encampments"
  )
ORDER BY requested_datetime DESC NULL LAST""",
        "$limit": 5000
    }
    
    try:
        response = requests.get(API_311_URL, params=query)
        response.raise_for_status()
        incidents = response.json()
        
        # Update cache
        data_cache['311_data'] = {
            'data': incidents,
            'timestamp': datetime.now()
        }
        
        logger.info(f"Fetched {len(incidents)} 311 incidents from SF Open Data")
        return incidents
        
    except Exception as e:
        logger.error(f"Error fetching 311 data: {e}")
        return []

def assign_risk(incident: Dict, incident_type: str) -> int:
    """
    Assign risk level to an incident (1=low, 2=medium, 3=high)
    Based on the Jupyter notebook's risk assignment logic
    """
    if incident_type == "crime":
        description = incident.get("call_type_original_desc", "").upper()
        
        # High risk crimes (w=3)
        high_risk = ["EXPLOSIVE FOUND", "EXPLOSION", "ROBBERY", "STRONGARM ROBBERY", "ASSAULT", "BATTERY"]
        if any(crime in description for crime in high_risk):
            return 3
        
        # Medium risk crimes (w=2)
        medium_risk = ["PURSE SNATCH", "INDECENT EXPOSURE", "FIGHT W/ WEAPONS", "FIGHT W/O WEAPONS", "BREAKING IN"]
        if any(crime in description for crime in medium_risk):
            return 2
        
        # Low risk crimes (w=1)
        low_risk = ["SUSPICIOUS PERSON", "THREATS/HARASSMENT", "THREATS", "HARASSMENT", "AGGRESSIVE", "THREATENING", "ENCAMPMENT"]
        if any(crime in description for crime in low_risk):
            return 1
        
        return 1  # Default low risk
    
    else:  # 311 data
        service_name = incident.get("service_name", "").upper()
        
        if "ENCAMPMENT" in service_name:
            return 1  # Low risk but persistent
        elif "AGGRESSIVE" in service_name or "THREATENING" in service_name:
            return 3  # High risk
        
        # Fallback for category-based classification
        category = incident.get("Category", "").upper()
        if any(word in category for word in ["OBSTRUCTION", "HAZARD", "DEBRIS", "POTHOLES", "SIDEWALK"]):
            return 3
        elif any(word in category for word in ["MAINTENANCE", "REPAIR", "CLEANUP"]):
            return 2
        
        return 1

def min_distance_to_path(incident_coords: Tuple[float, float], path: List[Tuple[float, float]]) -> float:
    """
    Calculate minimum distance from incident to any point on the path
    Returns distance in kilometers
    """
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

def calculate_risk_score(path: List[Tuple[float, float]], incidents: List[Dict], 
                        incident_type: str, current_time: Optional[datetime] = None) -> float:
    """
    Calculate risk score for a path using the magic formula from the notebook
    
    Formula with time decay:
    - For w=3: f(d,t,w) = (ReLU(3-3t/72))² × e^(-d²/0.02)
    - For w=1,2: f(d,t,w) = (ReLU(w-wt/24))² × e^(-d²/0.02)
    
    Special case: ENCAMPMENT
    - If status is CLOSED → skip (contributes 0)
    - If open → doesn't decay with time
    """
    total_risk = 0.0
    
    if current_time is None:
        current_time = datetime.now()
    
    for incident in incidents:
        # Get incident location
        if incident_type == "crime":
            coords = incident.get("intersection_point", {}).get("coordinates", [])
            if len(coords) < 2:
                continue
            incident_coords = (coords[1], coords[0])  # (lat, lon)
        else:  # 311 data
            point_geom = incident.get("point_geom")
            if point_geom:
                coords = point_geom.get("coordinates", [])
                if len(coords) >= 2:
                    incident_coords = (coords[1], coords[0])
                else:
                    continue
            else:
                # Fallback for old format
                lat = incident.get("Latitude")
                lon = incident.get("Longitude")
                if lat is None or lon is None:
                    continue
                incident_coords = (lat, lon)
        
        # Get risk level
        w = assign_risk(incident, incident_type)
        
        # Calculate distance
        d = min_distance_to_path(incident_coords, path)
        
        # Check for ENCAMPMENT special case
        if incident_type == "crime":
            description = incident.get("call_type_original_desc", "").upper()
        else:
            description = incident.get("service_name", "").upper()
        
        is_encampment = "ENCAMPMENT" in description
        
        # Check if ENCAMPMENT is closed
        if is_encampment:
            if incident_type == "crime":
                status = incident.get("status", "").upper()
            else:
                status = incident.get("status_description", "").upper()
            if status == "CLOSED":
                continue  # Skip closed encampments
        
        # Calculate time since incident
        if incident_type == "crime":
            incident_time_str = incident.get("entry_datetime")
        else:
            incident_time_str = incident.get("requested_datetime") or incident.get("timestamp")
        
        t = 0  # Default: assume recent
        if incident_time_str:
            try:
                incident_time = datetime.fromisoformat(incident_time_str.replace('Z', '+00:00'))
                if isinstance(current_time, str):
                    current_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                time_diff = current_time - incident_time
                t = time_diff.total_seconds() / 3600  # Convert to hours
            except:
                t = 0
        
        # Apply magic formula with time decay
        if is_encampment:
            # Encampments don't decay with time
            relu_term = w
        elif w == 3:
            # High-risk: decay over 72 hours
            relu_term = max(0, 3 - 3*t/72)
        else:
            # Lower-risk: decay over 24 hours
            relu_term = max(0, w - w*t/24)
        
        risk_value = (relu_term ** 2) * np.exp(-(d ** 2) / 0.02)
        total_risk += risk_value
    
    return total_risk

def find_lowest_risk_paths(polypaths: List[List[Tuple[float, float]]]) -> Dict:
    """
    Main function to analyze multiple paths and return the 3 safest
    """
    logger.info(f"Analyzing {len(polypaths)} paths...")
    
    # Fetch data
    crime_data = fetch_crime_data()
    incidents_311 = fetch_311_data()
    
    # Calculate risk for each path
    path_risks = []
    current_time = datetime.now()
    
    for i, path in enumerate(polypaths):
        crime_risk = calculate_risk_score(path, crime_data, "crime", current_time)
        incident_risk = calculate_risk_score(path, incidents_311, "311", current_time)
        total_risk = crime_risk + incident_risk
        
        path_risks.append({
            'path_index': i,
            'path': path,
            'crime_risk': crime_risk,
            '311_risk': incident_risk,
            'total_risk': total_risk
        })
        
        logger.info(f"Path {i+1}: Total Risk = {total_risk:.4f}")
    
    # Sort by risk (lowest first)
    path_risks.sort(key=lambda x: x['total_risk'])
    
    # Return top 3 safest paths
    return {
        'safest_paths': path_risks[:3],
        'all_paths': path_risks,
        'analysis_timestamp': current_time.isoformat()
    }

# API Endpoints

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'SafePath SF Risk Analysis'})

@app.route('/analyze-paths', methods=['POST'])
def analyze_paths():
    """
    Analyze multiple paths and return risk scores
    
    Request body:
    {
        "paths": [
            [[lat1, lon1], [lat2, lon2], ...],
            [[lat3, lon3], [lat4, lon4], ...],
            ...
        ]
    }
    """
    try:
        data = request.json
        paths = data.get('paths', [])
        
        if not paths:
            return jsonify({'error': 'No paths provided'}), 400
        
        # Convert paths to tuples
        polypaths = []
        for path in paths:
            polypath = [(point[0], point[1]) for point in path]
            polypaths.append(polypath)
        
        # Analyze paths
        results = find_lowest_risk_paths(polypaths)
        
        # Format response
        response = {
            'success': True,
            'safest_paths': [
                {
                    'index': p['path_index'],
                    'risk_score': p['total_risk'],
                    'crime_risk': p['crime_risk'],
                    '311_risk': p['311_risk']
                }
                for p in results['safest_paths']
            ],
            'all_paths': [
                {
                    'index': p['path_index'],
                    'risk_score': p['total_risk'],
                    'crime_risk': p['crime_risk'],
                    '311_risk': p['311_risk']
                }
                for p in results['all_paths']
            ],
            'timestamp': results['analysis_timestamp']
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error analyzing paths: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/crime-data', methods=['GET'])
def get_crime_data():
    """Get cached crime data"""
    try:
        crimes = fetch_crime_data()
        return jsonify({
            'success': True,
            'count': len(crimes),
            'data': crimes[:100]  # Return first 100 for preview
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/311-data', methods=['GET'])
def get_311_data():
    """Get cached 311 data"""
    try:
        incidents = fetch_311_data()
        return jsonify({
            'success': True,
            'count': len(incidents),
            'data': incidents[:100]  # Return first 100 for preview
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run Flask app
    app.run(debug=True, port=5000, host='0.0.0.0')