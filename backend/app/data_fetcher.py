"""
DataSF API Integration Module
Fetches crime and 311 incident data from San Francisco Open Data
"""
import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

# API Configuration
DATASF_API_TOKEN = os.getenv("DATASF_API_TOKEN", "Mxc2vd1fRYxkD4S4Y22GO3dGJ")
CRIME_API_URL = "https://data.sfgov.org/resource/gnap-fj3t.json"
API_311_URL = "https://data.sfgov.org/resource/vw6y-z8j6.json"

# Cache directory
CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

class DataSFetcher:
    """Fetches and manages incident data from DataSF APIs"""
    
    def __init__(self):
        self.crime_data: List[Dict[str, Any]] = []
        self.incidents_311: List[Dict[str, Any]] = []
        self.last_fetch_time: datetime | None = None
        
    def fetch_crime_data(self) -> List[Dict[str, Any]]:
        """
        Fetch crime/dispatch data from DataSF API
        Returns list of crime incidents with specific types
        """
        print("[API] Fetching crime data from DataSF...")

        # Simplified query - fetch recent data and filter in Python
        query = {
            "$limit": 1000,
            "$order": "entry_datetime DESC",
            "$where": "entry_datetime > '2025-10-01T00:00:00.000'"
        }

        headers = {
            "X-App-Token": DATASF_API_TOKEN
        }

        # Crime types we're interested in
        target_crimes = {
            "EXPLOSIVE FOUND", "SUSPICIOUS PERSON", "FIGHT W/WEAPONS",
            "FIGHT NO WEAPON", "ASSAULT / BATTERY DV", "PURSE SNATCH",
            "EXPLOSION", "ROBBERY", "THREATS / HARASSMENT",
            "STRONGARM ROBBERY", "INDECENT EXPOSURE", "PERSON BREAKING IN",
            "BURGLARY"
        }

        try:
            response = requests.get(CRIME_API_URL, params=query, headers=headers, timeout=30)
            response.raise_for_status()

            all_crimes = response.json()
            # Filter for our target crime types
            crimes = [c for c in all_crimes
                     if c.get("call_type_original_desc", "").upper() in target_crimes
                     and c.get("intersection_point")]

            print(f"[OK] Fetched {len(crimes)} crime incidents (filtered from {len(all_crimes)} total)")
            
            # Save to cache
            self._save_to_cache(crimes, "crime_data.json")
            
            return crimes
            
        except Exception as e:
            print(f"[ERROR] Error fetching crime data: {e}")
            # Try to load from cache
            return self._load_from_cache("crime_data.json")
    
    def fetch_311_data(self) -> List[Dict[str, Any]]:
        """
        Fetch 311 incident data from DataSF API
        Returns list of 311 incidents (Encampments, Aggressive/Threatening)
        """
        print("[API] Fetching 311 data from DataSF...")

        # Simplified query - fetch recent data and filter in Python
        query = {
            "$limit": 50,
            "$order": "requested_datetime DESC",
            "$where": "requested_datetime > '2025-10-01T00:00:00.000'"
        }

        headers = {
            "X-App-Token": DATASF_API_TOKEN
        }

        # 311 service types we're interested in
        target_services = {"AGGRESSIVE/THREATENING", "ENCAMPMENT", "ENCAMPMENTS"}

        try:
            response = requests.get(API_311_URL, params=query, headers=headers, timeout=30)
            response.raise_for_status()

            all_incidents = response.json()
            # Filter for our target service types
            incidents = [i for i in all_incidents
                        if i.get("service_name", "").upper() in target_services
                        and i.get("point_geom")]

            print(f"[OK] Fetched {len(incidents)} 311 incidents (filtered from {len(all_incidents)} total)")
            
            # Save to cache
            self._save_to_cache(incidents, "311_data.json")
            
            return incidents
            
        except Exception as e:
            print(f"[ERROR] Error fetching 311 data: {e}")
            # Try to load from cache
            return self._load_from_cache("311_data.json")
    
    def fetch_all_data(self) -> Dict[str, Any]:
        """
        Fetch both crime and 311 data
        Returns dict with both datasets
        """
        self.crime_data = self.fetch_crime_data()
        self.incidents_311 = self.fetch_311_data()
        self.last_fetch_time = datetime.now()
        
        return {
            "crime_data": self.crime_data,
            "incidents_311": self.incidents_311,
            "fetch_time": self.last_fetch_time.isoformat()
        }
    
    def get_data(self) -> Dict[str, Any]:
        """Get current data (fetch if not available)"""
        if not self.crime_data or not self.incidents_311:
            return self.fetch_all_data()
        
        return {
            "crime_data": self.crime_data,
            "incidents_311": self.incidents_311,
            "fetch_time": self.last_fetch_time.isoformat() if self.last_fetch_time else None
        }
    
    def _save_to_cache(self, data: List[Dict[str, Any]], filename: str):
        """Save data to cache file"""
        try:
            cache_path = CACHE_DIR / filename
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[WARN] Failed to save cache: {e}")
    
    def _load_from_cache(self, filename: str) -> List[Dict[str, Any]]:
        """Load data from cache file"""
        try:
            cache_path = CACHE_DIR / filename
            if cache_path.exists():
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    print(f"[CACHE] Loaded {len(data)} items from cache")
                    return data
        except Exception as e:
            print(f"[WARN] Failed to load cache: {e}")
        
        return []
