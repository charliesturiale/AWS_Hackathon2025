"""
SafePath SF - Path Risk Analysis System
Direct implementation from Jupyter notebook Path_Risk_Analysis_Beginner.ipynb
"""

import boto3
import requests
import json
import numpy as np
import pandas as pd
from geopy.distance import geodesic
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

# AWS Configuration
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "my-path-risk-data"

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)

# SF Open Data API endpoints (no API key required!)
CRIME_API_URL = "https://data.sfgov.org/resource/gnap-fj3t.json"
API_311_URL = "https://data.sfgov.org/resource/vw6y-z8j6.json"


def fetch_crime_data(area_bounds, api_key=None):
    """
    Get crime data from SF Open Data API.
    
    This is like asking a website: "What crimes happened here?"
    
    Input:
    - area_bounds: Where we want to look (like GPS coordinates of an area)
    - api_key: Not needed for SF Open Data (they allow public access)
    
    Output:
    - A list of crimes that happened in that area
    """
    
    # SF Open Data API endpoint with specific crime types
    api_url = "https://data.sfgov.org/resource/gnap-fj3t.json"
    
    # Query for specific crime types
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
        "$limit": 5000  # Limit results
    }
    
    try:
        # Ask the website for data
        response = requests.get(api_url, params=query)
        
        # Check if we got good data back
        response.raise_for_status()
        
        # Convert the response to something we can use
        crimes = response.json()
        
        print(f"✅ Got {len(crimes)} crime incidents from SF Open Data!")
        return crimes
        
    except Exception as e:
        # If something went wrong, tell us
        print(f"❌ Error: {e}")
        return []


def fetch_311_data(area_bounds, api_key=None):
    """
    Get 311 data from SF Open Data API.
    
    This asks: "What street problems (Encampments, Aggressive/Threatening) were reported here?"
    
    Input:
    - area_bounds: Where to look (not used in this implementation, but kept for compatibility)
    - api_key: Not needed for SF Open Data
    
    Output:
    - List of 311 incidents
    """
    
    # SF Open Data 311 API endpoint
    api_url = "https://data.sfgov.org/resource/vw6y-z8j6.json"
    
    # Query for Aggressive/Threatening and Encampment incidents
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
        "$limit": 5000  # Limit results
    }
    
    try:
        # Ask for the data
        response = requests.get(api_url, params=query)
        response.raise_for_status()
        
        # Get the data
        incidents = response.json()
        
        print(f"✅ Got {len(incidents)} 311 incidents from SF Open Data!")
        return incidents
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def save_to_s3(data, bucket_name, key):
    """
    Save data to S3 (cloud storage).
    
    Think of it like saving a file to your phone's cloud storage.
    
    Input:
    - data: The information we want to save
    - bucket_name: Which "folder" to save it in
    - key: What to name the file
    
    Output:
    - True if saved successfully, False if it failed
    """
    
    try:
        # Convert our data to JSON (a common format for saving data)
        json_data = json.dumps(data)
        
        # Actually save it!
        s3_client.put_object(
            Bucket=bucket_name,      # Which "folder"
            Key=key,                 # Filename
            Body=json_data,          # The data itself
            ContentType='application/json'  # What type of file it is
        )
        
        print(f"✅ Saved '{key}' to S3!")
        return True
        
    except Exception as e:
        print(f"❌ Couldn't save: {e}")
        return False


def assign_risk(incident, incident_type):
    """
    Decide how dangerous an incident is.
    
    This is like judging: "How bad is this problem?"
    
    Input:
    - incident: Details about what happened
    - incident_type: Is this crime data or 311 data?
    
    Output:
    - A number (1, 2, or 3) saying how dangerous it is
    """
    
    if incident_type == "crime":
        # Get the crime description
        description = incident.get("call_type_original_desc", "").upper()
        
        # High risk crimes (w=3): Very dangerous
        high_risk_crimes = ["EXPLOSIVE FOUND", "EXPLOSION", "ROBBERY", "STRONGARM ROBBERY", "ASSAULT", "BATTERY"]
        if any(crime in description for crime in high_risk_crimes):
            return 3  # 🚨 Very dangerous!
        
        # Medium risk crimes (w=2): Somewhat dangerous
        medium_risk_crimes = ["PURSE SNATCH", "INDECENT EXPOSURE", "FIGHT W/ WEAPONS", "FIGHT W/O WEAPONS", "BREAKING IN"]
        if any(crime in description for crime in medium_risk_crimes):
            return 2  # ⚠️ Somewhat dangerous
        
        # Low risk crimes (w=1): Not very dangerous
        low_risk_crimes = ["SUSPICIOUS PERSON", "THREATS/HARASSMENT", "THREATS", "HARASSMENT", "AGGRESSIVE", "THREATENING", "ENCAMPMENT"]
        if any(crime in description for crime in low_risk_crimes):
            return 1  # ✅ Not very dangerous
        
        # Default for unknown crimes
        return 1  # ✅ Assume low risk for unknown
    
    else:  # It's 311 data (street problems)
        # SF 311 data uses service_name
        service_name = incident.get("service_name", "").upper()
        
        # Check for specific service types
        if "ENCAMPMENT" in service_name:
            return 1  # Low risk, but persistent
        elif "AGGRESSIVE" in service_name or "THREATENING" in service_name:
            return 3  # 🚨 Very dangerous!
        
        # Fallback for old format
        category = incident.get("Category", "").upper()
        if any(word in category for word in ["OBSTRUCTION", "HAZARD", "DEBRIS", "POTHOLES", "SIDEWALK"]):
            return 3  # 🚨 Trip hazard!
        elif any(word in category for word in ["MAINTENANCE", "REPAIR", "CLEANUP"]):
            return 2  # ⚠️ Annoying
        else:
            return 1  # ✅ No big deal


def min_distance_to_path(incident_coords, path):
    """
    Find the shortest distance from an incident to any point on the path.
    
    Think of it like this: 
    If an incident happened at point A, and your route goes through points B, C, D...
    What's the shortest distance from A to any of those points?
    
    Input:
    - incident_coords: Where the incident happened (latitude, longitude)
    - path: Your route (a list of GPS coordinates)
    
    Output:
    - The distance in kilometers
    """
    
    # Safety check: Make sure we have a real path
    if len(path) < 2:
        return float('inf')  # If no path, assume it's infinitely far away
    
    # Start with a really big number
    min_dist = float('inf')
    
    # Check distance to every point on the path
    for path_point in path:
        try:
            # Calculate distance (using geodesic = Earth's curve)
            dist = geodesic(incident_coords, path_point).meters / 1000
            # ^convert meters to kilometers
            
            # Keep track of the smallest distance we found
            min_dist = min(min_dist, dist)
        except:
            # If something goes wrong, just skip it
            continue
    
    return min_dist


def calculate_risk_score(path, incidents, incident_type, current_time=None):
    """
    Calculate the total danger score for a path.
    
    How it works:
    1. For each incident near the path
    2. Get its risk level (1, 2, or 3)
    3. Measure how far it is from the path
    4. Calculate time since incident
    5. Apply the magic formula with time decay
    6. Add it all up
    
    Special case: ENCAMPMENT
    - If status is CLOSED → skip (contributes 0 to risk)
    - If status is open → doesn't decay with time
    
    Input:
    - path: Your route (list of GPS points)
    - incidents: All the bad things that happened
    - incident_type: Is this crime or 311 data?
    - current_time: Current timestamp (for time calculation)
    
    Output:
    - Total danger score (lower is safer!)
    """
    
    total_risk = 0.0
    
    # Look at each incident
    for incident in incidents:
        
        # Step 1: Get the location of this incident
        if incident_type == "crime":
            # SF Crime data has location as [longitude, latitude] in intersection_point
            coords = incident.get("intersection_point", {}).get("coordinates", [])
            if len(coords) < 2:
                continue  # Skip if we don't have a location
            incident_coords = (coords[1], coords[0])  # Convert to (lat, lon)
        else:  # It's 311 data
            # SF 311 data has point_geom in GeoJSON format: {"type": "Point", "coordinates": [lon, lat]}
            point_geom = incident.get("point_geom")
            if point_geom:
                coords = point_geom.get("coordinates", [])
                if len(coords) >= 2:
                    incident_coords = (coords[1], coords[0])  # Convert to (lat, lon)
                else:
                    continue  # Skip if invalid
            else:
                # Fallback for old format
                lat = incident.get("Latitude")
                lon = incident.get("Longitude")
                if lat is None or lon is None:
                    continue  # Skip if missing
                incident_coords = (lat, lon)
        
        # Step 2: Get the risk level (1, 2, or 3)
        w = assign_risk(incident, incident_type)
        
        # Step 3: Find distance to path
        d = min_distance_to_path(incident_coords, path)
        
        # SPECIAL CASE: Check if this is ENCAMPMENT
        if incident_type == "crime":
            description = incident.get("call_type_original_desc", "").upper()
        else:
            description = incident.get("service_name", "").upper()
        is_encampment = "ENCAMPMENT" in description
        
        # If it's ENCAMPMENT and status is CLOSED, skip it (contributes 0)
        if is_encampment:
            # Check status (for 311 it's status_description, for crimes it's status)
            if incident_type == "crime":
                status = incident.get("status", "").upper()
            else:
                status = incident.get("status_description", "").upper()
            if status == "CLOSED":
                continue  # Skip this incident, don't contribute to risk
        
        # Step 4: Calculate time since incident
        # Get incident time from data
        if incident_type == "crime":
            incident_time_str = incident.get("entry_datetime")
        else:
            # For SF 311 data, it's requested_datetime
            incident_time_str = incident.get("requested_datetime") or incident.get("timestamp")
        
        # Calculate time difference in hours
        t = 0  # Default: assume recent incident (0 hours ago)
        if current_time and incident_time_str:
            try:
                from datetime import datetime
                # Parse the time string
                incident_time = datetime.fromisoformat(incident_time_str.replace('Z', '+00:00'))
                if isinstance(current_time, str):
                    current_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                # Calculate difference in hours
                time_diff = current_time - incident_time
                t = time_diff.total_seconds() / 3600  # Convert to hours
            except:
                t = 0  # If we can't parse, assume recent
        
        # Step 5: Apply the magic formula WITH TIME DECAY!
        # ReLU function: max(0, x)
        if is_encampment:
            # ENCAMPMENT doesn't decay with time - use full risk value
            relu_term = w
        elif w == 3:
            # High-risk incidents: decay over 72 hours
            relu_term = max(0, 3 - 3*t/72)
        else:
            # Lower-risk incidents: decay over 24 hours
            relu_term = max(0, w - w*t/24)
        
        risk_value = (relu_term ** 2) * np.exp(-(d ** 2) / 0.02)
        
        # Step 6: Add to total
        total_risk += risk_value
    
    return total_risk


def find_lowest_risk_paths(polypaths, area_bounds=None, crime_api_key=None, api_311_key=None):
    """
    THE BIG ONE! This does everything!
    
    Input:
    - polypaths: List of possible routes
    - area_bounds: Not used for SF Open Data (optional)
    - crime_api_key: Not needed for SF Open Data (optional)
    - api_311_key: Not needed for SF Open Data (optional)
    
    Output:
    - Top 3 safest paths
    """
    
    print(f"🔍 Analyzing {len(polypaths)} paths...")
    print("=" * 60)
    
    # STEP 1: Get the data from SF Open Data
    print("\n📞 Fetching crime data from SF Open Data...")
    crime_data = fetch_crime_data(area_bounds, crime_api_key)
    
    print("\n📞 Fetching 311 data from SF Open Data...")
    incidents_311 = fetch_311_data(area_bounds, api_311_key)
    
    # STEP 2: Save to S3 (backup!)
    print("\n💾 Saving to cloud storage...")
    save_to_s3({"crimes": crime_data}, S3_BUCKET_NAME, "crime_data.json")
    save_to_s3({"incidents": incidents_311}, S3_BUCKET_NAME, "311_data.json")
    
    # STEP 3: Calculate risk for each path
    path_risks = []
    
    for i, path in enumerate(polypaths):
        print(f"\n📊 Analyzing Path {i+1}...")
        
        # Get current time for time-based calculations
        from datetime import datetime
        current_time = datetime.now()
        
        # Calculate risk from crimes (with time!)
        crime_risk = calculate_risk_score(path, crime_data, "crime", current_time)
        
        # Calculate risk from 311 incidents (with time!)
        incident_risk = calculate_risk_score(path, incidents_311, "311", current_time)
        
        # Total risk = crime risk + 311 risk
        total_risk = crime_risk + incident_risk
        
        path_risks.append((path, total_risk))
        print(f"   Total Risk Score: {total_risk:.4f}")
    
    # STEP 4: Sort by risk (lowest first = safest)
    path_risks.sort(key=lambda x: x[1])
    
    # STEP 5: Get top 3
    top_3_paths = [path for path, risk in path_risks[:3]]
    
    print("\n" + "=" * 60)
    print("🏆 RESULTS: Top 3 Safest Paths")
    print("=" * 60)
    for i, (path, risk) in enumerate(path_risks[:3]):
        print(f"\n{i+1}. Path {i+1} - Risk Score: {risk:.4f} (SAFEST!)" if i == 0 else f"\n{i+1}. Path {i+1} - Risk Score: {risk:.4f}")
    
    return top_3_paths


# Example usage - exactly as shown in the notebook
if __name__ == "__main__":
    # Example paths from the notebook
    example_polypaths = [
        # Path 1: Short route
        [(37.7849, -122.4094), (37.7855, -122.4086), (37.7861, -122.4078)],
        # Path 2: Different route
        [(37.7849, -122.4094), (37.7845, -122.4102), (37.7841, -122.4110)],
        # Path 3: Alternative route
        [(37.7849, -122.4094), (37.7852, -122.4090), (37.7855, -122.4086)],
    ]
    
    # Note: To actually run this, you need:
    # 1. AWS credentials configured
    # 2. S3 bucket created
    # 3. Install requirements: pip install boto3 requests numpy pandas geopy
    
    print("📝 Setup complete!")
    print("\n🎉 No API keys needed - SF Open Data is free and public!")
    print("\n⚠️  To actually run it:")
    print("   1. Set up AWS credentials")
    print("   2. Create S3 bucket")
    print("   3. Uncomment the line below and run!")
    
    # Uncomment to run:
    # lowest_risk_paths = find_lowest_risk_paths(example_polypaths)