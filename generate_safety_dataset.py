#!/usr/bin/env python3
"""
SafePath SF Dataset Generator
Generates a CSV dataset for pedestrian safety classification with street segments
"""

import pandas as pd
import numpy as np
import json
import requests
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SFSafetyDatasetGenerator:
    def __init__(self):
        """Initialize the dataset generator with SF boundaries"""
        # San Francisco city boundaries
        self.bounds = {
            'north': 37.812,
            'south': 37.708,
            'west': -122.520,
            'east': -122.357
        }
        
        # Grid size for street segments (approximately 100m segments)
        self.grid_size = 0.001  # ~100 meters in SF latitude
        
        # API endpoints - using environment variables with fallbacks
        # DataSF APIs work without keys but have better rate limits with app token
        self.api_endpoints = {
            'crime': os.getenv('REACT_APP_SF_CRIME_API', 'https://data.sfgov.org/resource/wg3w-h783.json'),
            'incidents_311': os.getenv('REACT_APP_SF_311_API', 'https://data.sfgov.org/resource/vw6y-z8j6.json'),
            'streetlights': 'https://data.sfgov.org/resource/cbux-n2du.json',  # Correct streetlights endpoint
            'permits': os.getenv('REACT_APP_SF_PERMITS_API', 'https://data.sfgov.org/resource/i98e-djp9.json'),
        }
        
        # Optional DataSF app token for higher rate limits
        self.datasf_token = os.getenv('DATASF_API_KEY', None)
        
        # Initialize data storage
        self.crime_data = []
        self.hazard_data = []
        self.lighting_data = []
        self.construction_data = []
        
    def generate_street_segments(self) -> List[Dict]:
        """Generate street segments covering SF"""
        segments = []
        
        # Create grid of segments
        lat_steps = int((self.bounds['north'] - self.bounds['south']) / self.grid_size)
        lng_steps = int((self.bounds['east'] - self.bounds['west']) / self.grid_size)
        
        for i in range(lat_steps):
            for j in range(lng_steps):
                lat = self.bounds['south'] + (i * self.grid_size)
                lng = self.bounds['west'] + (j * self.grid_size)
                
                # Filter out water/non-walkable areas (simplified)
                if self.is_walkable_area(lat, lng):
                    segments.append({
                        'segment_id': f"seg_{i}_{j}",
                        'latitude': lat,
                        'longitude': lng,
                        'lat_end': lat + self.grid_size,
                        'lng_end': lng + self.grid_size
                    })
        
        return segments
    
    def is_walkable_area(self, lat: float, lng: float) -> bool:
        """Check if coordinates are in walkable area (not water)"""
        # Simplified check - exclude obvious water areas
        # Bay Bridge area
        if lat < 37.795 and lng > -122.390:
            return False
        # Ocean side
        if lng < -122.510:
            return False
        # SF Bay
        if lat < 37.750 and lng > -122.380:
            return False
        return True
    
    def fetch_crime_data(self):
        """Fetch crime data from DataSF"""
        print("Fetching crime data...")
        try:
            # Get crimes from last 90 days
            date_90_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            
            query = f"{self.api_endpoints['crime']}?$where=incident_datetime>'{date_90_days_ago}'&$limit=50000"
            
            # Add app token if available for better rate limits
            if self.datasf_token:
                query += f"&$$app_token={self.datasf_token}"
            
            response = requests.get(query)
            
            if response.status_code == 200:
                self.crime_data = response.json()
                print(f"✓ Fetched {len(self.crime_data)} crime records")
            else:
                print(f"✗ Error fetching crime data: {response.status_code}")
        except Exception as e:
            print(f"✗ Exception fetching crime data: {e}")
    
    def fetch_311_data(self):
        """Fetch 311 hazard reports"""
        print("Fetching 311 hazard data...")
        try:
            # Get recent 311 reports
            date_30_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Safety-related service types
            safety_categories = [
                'Street and Sidewalk Cleaning',
                'Streetlight',
                'Street Defects', 
                'Sidewalk or Curb',
                'Encampment',
                'Blocked Street or SideWalk',
                'Homeless Concerns',
                'Needles'
            ]
            
            category_filter = ' OR '.join([f"service_name='{cat}'" for cat in safety_categories])
            
            query = f"{self.api_endpoints['incidents_311']}?$where=({category_filter}) AND requested_datetime>'{date_30_days_ago}'&$limit=10000"
            
            # Add app token if available
            if self.datasf_token:
                query += f"&$$app_token={self.datasf_token}"
                
            response = requests.get(query)
            
            if response.status_code == 200:
                self.hazard_data = response.json()
                print(f"✓ Fetched {len(self.hazard_data)} hazard reports")
            else:
                print(f"✗ Error fetching 311 data: {response.status_code}")
        except Exception as e:
            print(f"✗ Exception fetching 311 data: {e}")
    
    def fetch_lighting_data(self):
        """Fetch street lighting issues"""
        print("Fetching street lighting data...")
        try:
            query = f"{self.api_endpoints['streetlights']}?$limit=5000"
            
            # Add app token if available
            if self.datasf_token:
                query += f"&$$app_token={self.datasf_token}"
                
            response = requests.get(query)
            
            if response.status_code == 200:
                self.lighting_data = response.json()
                print(f"✓ Fetched {len(self.lighting_data)} lighting issues")
            else:
                print(f"✗ Error fetching lighting data: {response.status_code}")
        except Exception as e:
            print(f"✗ Exception fetching lighting data: {e}")
    
    def fetch_construction_data(self):
        """Fetch active construction permits"""
        print("Fetching construction permit data...")
        try:
            query = f"{self.api_endpoints['permits']}?status=ISSUED&$limit=5000"
            
            # Add app token if available
            if self.datasf_token:
                query += f"&$$app_token={self.datasf_token}"
                
            response = requests.get(query)
            
            if response.status_code == 200:
                self.construction_data = response.json()
                print(f"✓ Fetched {len(self.construction_data)} construction permits")
            else:
                print(f"✗ Error fetching construction data: {response.status_code}")
        except Exception as e:
            print(f"✗ Exception fetching construction data: {e}")
    
    def calculate_segment_features(self, segment: Dict) -> Dict:
        """Calculate safety features for a street segment"""
        features = {
            'segment_id': segment['segment_id'],
            'latitude': segment['latitude'],
            'longitude': segment['longitude'],
            'lat_end': segment['lat_end'],
            'lng_end': segment['lng_end']
        }
        
        # Crime features
        crime_counts = self.count_nearby_crimes(segment)
        features.update(crime_counts)
        
        # 311 hazard features
        hazard_counts = self.count_nearby_hazards(segment)
        features.update(hazard_counts)
        
        # Lighting issues
        features['lighting_issues'] = self.count_nearby_issues(
            segment, self.lighting_data, 'lat', 'long', 200
        )
        
        # Construction zones
        features['active_construction'] = self.count_construction_nearby(segment)
        
        # Time-based features
        features.update(self.get_temporal_features())
        
        # Location-based features
        features.update(self.get_location_features(segment))
        
        # Infrastructure features (simulated for now)
        features.update(self.simulate_infrastructure_features(segment))
        
        return features
    
    def count_nearby_crimes(self, segment: Dict) -> Dict:
        """Count crimes by type near segment"""
        crime_counts = {
            'violent_crimes_90d': 0,
            'property_crimes_90d': 0,
            'drug_crimes_90d': 0,
            'total_crimes_90d': 0,
            'recent_crimes_7d': 0
        }
        
        violent_types = ['Assault', 'Robbery', 'Homicide', 'Rape', 'Human Trafficking']
        property_types = ['Burglary', 'Larceny Theft', 'Motor Vehicle Theft', 'Arson']
        drug_types = ['Drug Offense', 'Drug Violation']
        
        for crime in self.crime_data:
            try:
                crime_lat = float(crime.get('latitude', 0))
                crime_lng = float(crime.get('longitude', 0))
                
                # Check if crime is within segment bounds (with buffer)
                buffer = 0.002  # ~200m buffer
                if (segment['latitude'] - buffer <= crime_lat <= segment['lat_end'] + buffer and
                    segment['longitude'] - buffer <= crime_lng <= segment['lng_end'] + buffer):
                    
                    crime_type = crime.get('incident_category', '')
                    crime_counts['total_crimes_90d'] += 1
                    
                    if crime_type in violent_types:
                        crime_counts['violent_crimes_90d'] += 1
                    elif crime_type in property_types:
                        crime_counts['property_crimes_90d'] += 1
                    elif crime_type in drug_types:
                        crime_counts['drug_crimes_90d'] += 1
                    
                    # Check if recent (last 7 days)
                    crime_date = datetime.strptime(crime.get('incident_datetime', '2024-01-01'), 
                                                  '%Y-%m-%dT%H:%M:%S.%f')
                    if (datetime.now() - crime_date).days <= 7:
                        crime_counts['recent_crimes_7d'] += 1
                        
            except (ValueError, TypeError):
                continue
        
        return crime_counts
    
    def count_nearby_hazards(self, segment: Dict) -> Dict:
        """Count 311 hazards near segment"""
        hazard_counts = {
            'street_hazards': 0,
            'encampments': 0,
            'needles_reported': 0,
            'blocked_sidewalk': 0,
            'total_311_reports': 0
        }
        
        for hazard in self.hazard_data:
            try:
                hazard_lat = float(hazard.get('lat', 0))
                hazard_lng = float(hazard.get('long', 0))
                
                buffer = 0.001  # ~100m buffer
                if (segment['latitude'] - buffer <= hazard_lat <= segment['lat_end'] + buffer and
                    segment['longitude'] - buffer <= hazard_lng <= segment['lng_end'] + buffer):
                    
                    service_type = hazard.get('service_name', '')
                    hazard_counts['total_311_reports'] += 1
                    
                    if 'Street' in service_type or 'Sidewalk' in service_type:
                        hazard_counts['street_hazards'] += 1
                    if 'Encampment' in service_type or 'Homeless' in service_type:
                        hazard_counts['encampments'] += 1
                    if 'Needle' in service_type:
                        hazard_counts['needles_reported'] += 1
                    if 'Blocked' in service_type:
                        hazard_counts['blocked_sidewalk'] += 1
                        
            except (ValueError, TypeError):
                continue
        
        return hazard_counts
    
    def count_nearby_issues(self, segment: Dict, data: List, lat_field: str, 
                           lng_field: str, radius: float) -> int:
        """Generic function to count nearby issues"""
        count = 0
        buffer = radius / 111000  # Convert meters to degrees (approximate)
        
        for item in data:
            try:
                item_lat = float(item.get(lat_field, 0))
                item_lng = float(item.get(lng_field, 0))
                
                if (segment['latitude'] - buffer <= item_lat <= segment['lat_end'] + buffer and
                    segment['longitude'] - buffer <= item_lng <= segment['lng_end'] + buffer):
                    count += 1
            except (ValueError, TypeError):
                continue
        
        return count
    
    def count_construction_nearby(self, segment: Dict) -> int:
        """Count active construction permits nearby"""
        count = 0
        for permit in self.construction_data:
            # Construction data might have address instead of coords
            # For now, simulate based on segment location
            if random.random() < 0.1:  # 10% chance of construction
                count += 1
        return min(count, 3)  # Cap at 3
    
    def get_temporal_features(self) -> Dict:
        """Get time-based risk features"""
        now = datetime.now()
        return {
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'is_weekend': now.weekday() >= 5,
            'is_night': now.hour < 6 or now.hour > 20,
            'is_rush_hour': (7 <= now.hour <= 9) or (17 <= now.hour <= 19),
            'month': now.month
        }
    
    def get_location_features(self, segment: Dict) -> Dict:
        """Get location-based features"""
        lat, lng = segment['latitude'], segment['longitude']
        
        # High-risk neighborhoods (simplified)
        high_risk_areas = [
            {'name': 'Tenderloin', 'center': (37.784, -122.414), 'radius': 0.01},
            {'name': 'SOMA', 'center': (37.778, -122.405), 'radius': 0.015},
            {'name': 'Mission', 'center': (37.759, -122.415), 'radius': 0.02},
            {'name': 'Bayview', 'center': (37.735, -122.390), 'radius': 0.02}
        ]
        
        # Business districts (generally safer during day)
        business_areas = [
            {'name': 'Financial', 'center': (37.794, -122.400), 'radius': 0.01},
            {'name': 'Union Square', 'center': (37.788, -122.407), 'radius': 0.008}
        ]
        
        in_high_risk = 0
        in_business = 0
        
        for area in high_risk_areas:
            dist = np.sqrt((lat - area['center'][0])**2 + (lng - area['center'][1])**2)
            if dist <= area['radius']:
                in_high_risk = 1
                break
        
        for area in business_areas:
            dist = np.sqrt((lat - area['center'][0])**2 + (lng - area['center'][1])**2)
            if dist <= area['radius']:
                in_business = 1
                break
        
        return {
            'in_high_risk_area': in_high_risk,
            'in_business_district': in_business,
            'distance_to_downtown': np.sqrt((lat - 37.794)**2 + (lng + 122.400)**2)
        }
    
    def simulate_infrastructure_features(self, segment: Dict) -> Dict:
        """Simulate infrastructure features (would use real data in production)"""
        # These would come from real APIs in production
        return {
            'sidewalk_width': np.random.uniform(1.2, 3.5),  # meters
            'lighting_quality': np.random.uniform(0.2, 1.0),  # 0-1 scale
            'cctv_coverage': np.random.choice([0, 1], p=[0.7, 0.3]),  # 30% have CCTV
            'nearest_transit_stop': np.random.uniform(50, 500),  # meters
            'pedestrian_traffic': np.random.uniform(0.1, 1.0),  # 0-1 scale
            'business_density': np.random.poisson(5),  # number of businesses
            'escape_routes': np.random.randint(1, 5)  # number of escape paths
        }
    
    def calculate_safety_label(self, features: Dict) -> int:
        """Calculate if segment is safe (0) or unsafe (1) based on features"""
        risk_score = 0
        
        # Crime-based risk
        if features['violent_crimes_90d'] > 5:
            risk_score += 30
        elif features['violent_crimes_90d'] > 2:
            risk_score += 15
        
        if features['total_crimes_90d'] > 20:
            risk_score += 20
        elif features['total_crimes_90d'] > 10:
            risk_score += 10
        
        if features['recent_crimes_7d'] > 3:
            risk_score += 15
        
        # Hazard-based risk
        if features['encampments'] > 2:
            risk_score += 15
        if features['needles_reported'] > 0:
            risk_score += 10
        if features['blocked_sidewalk'] > 1:
            risk_score += 5
        
        # Infrastructure risk
        if features['lighting_issues'] > 2:
            risk_score += 10
        if features['lighting_quality'] < 0.3:
            risk_score += 15
        if features['cctv_coverage'] == 0:
            risk_score += 5
        if features['escape_routes'] < 2:
            risk_score += 10
        
        # Temporal risk
        if features['is_night']:
            risk_score += 10
        if features['hour'] >= 23 or features['hour'] <= 5:
            risk_score += 15
        
        # Location risk
        if features['in_high_risk_area']:
            risk_score += 20
        if features['pedestrian_traffic'] < 0.2:
            risk_score += 15
        
        # Threshold for unsafe classification
        return 1 if risk_score >= 50 else 0
    
    def generate_dataset(self, sample_size: int = None) -> pd.DataFrame:
        """Generate the complete dataset"""
        print("\n" + "="*60)
        print("SAFEPATH SF DATASET GENERATOR")
        print("="*60 + "\n")
        
        # Fetch all data from APIs
        print("Step 1: Fetching data from San Francisco APIs...")
        self.fetch_crime_data()
        self.fetch_311_data()
        self.fetch_lighting_data()
        self.fetch_construction_data()
        
        # Generate street segments
        print("\nStep 2: Generating street segments...")
        segments = self.generate_street_segments()
        print(f"✓ Generated {len(segments)} street segments")
        
        # Sample if requested
        if sample_size and sample_size < len(segments):
            segments = random.sample(segments, sample_size)
            print(f"✓ Sampled {sample_size} segments for dataset")
        
        # Calculate features for each segment
        print("\nStep 3: Calculating features for each segment...")
        dataset = []
        
        for i, segment in enumerate(segments):
            if i % 100 == 0:
                print(f"  Processing segment {i}/{len(segments)}...")
            
            features = self.calculate_segment_features(segment)
            features['is_unsafe'] = self.calculate_safety_label(features)
            dataset.append(features)
        
        # Convert to DataFrame
        df = pd.DataFrame(dataset)
        
        # Print dataset statistics
        print("\n" + "="*60)
        print("DATASET STATISTICS")
        print("="*60)
        print(f"Total segments: {len(df)}")
        print(f"Safe segments: {len(df[df['is_unsafe'] == 0])} ({len(df[df['is_unsafe'] == 0])/len(df)*100:.1f}%)")
        print(f"Unsafe segments: {len(df[df['is_unsafe'] == 1])} ({len(df[df['is_unsafe'] == 1])/len(df)*100:.1f}%)")
        print(f"Features per segment: {len(df.columns) - 1}")
        print("\nFeature columns:")
        for col in df.columns:
            if col != 'is_unsafe':
                print(f"  - {col}")
        
        return df
    
    def save_dataset(self, df: pd.DataFrame, filename: str = "sf_street_safety_dataset.csv"):
        """Save dataset to CSV file"""
        filepath = os.path.join(os.path.dirname(__file__), 'data', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df.to_csv(filepath, index=False)
        print(f"\n✓ Dataset saved to: {filepath}")
        print(f"  File size: {os.path.getsize(filepath) / 1024 / 1024:.2f} MB")
        
        return filepath


def main():
    """Main execution function"""
    generator = SFSafetyDatasetGenerator()
    
    # Generate dataset with 5000 samples (for testing)
    # Use None for full city coverage
    df = generator.generate_dataset(sample_size=5000)
    
    # Save to CSV
    filepath = generator.save_dataset(df)
    
    # Display sample
    print("\n" + "="*60)
    print("SAMPLE DATA (First 5 rows)")
    print("="*60)
    print(df.head())
    
    print("\n✅ Dataset generation complete!")
    print(f"📊 Use the CSV file at '{filepath}' for training your ML model")
    print("\nNext steps:")
    print("1. Load this CSV in your ML pipeline")
    print("2. Split into train/test sets")
    print("3. Train classifier (Random Forest, XGBoost, etc.)")
    print("4. Deploy model for real-time safety predictions")


if __name__ == "__main__":
    main()