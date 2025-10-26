#!/usr/bin/env python3
"""
SafePath SF Simple Dataset Generator
Generates a location-agnostic CSV dataset for pedestrian safety classification
Each row represents safety features that could apply to any street segment
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleSafetyDatasetGenerator:
    def __init__(self):
        """Initialize the dataset generator"""
        # San Francisco city boundaries for data collection
        self.bounds = {
            'north': 37.812,
            'south': 37.708,
            'west': -122.520,
            'east': -122.357
        }
        
        # Grid size for street segments
        self.grid_size = 0.001
        
        # API endpoints
        self.api_endpoints = {
            'crime': os.getenv('REACT_APP_SF_CRIME_API', 'https://data.sfgov.org/resource/wg3w-h783.json'),
            'incidents_311': os.getenv('REACT_APP_SF_311_API', 'https://data.sfgov.org/resource/vw6y-z8j6.json'),
            'permits': os.getenv('REACT_APP_SF_PERMITS_API', 'https://data.sfgov.org/resource/i98e-djp9.json'),
        }
        
        # Optional DataSF app token
        self.datasf_token = os.getenv('DATASF_API_KEY', None)
        
        # Data storage
        self.crime_data = []
        self.hazard_data = []
        self.construction_data = []
        
    def fetch_all_data(self):
        """Fetch all data from APIs"""
        print("Fetching data from San Francisco APIs...")
        
        # Fetch crime data
        try:
            date_90_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            query = f"{self.api_endpoints['crime']}?$where=incident_datetime>'{date_90_days_ago}'&$limit=50000"
            if self.datasf_token:
                query += f"&$$app_token={self.datasf_token}"
            
            response = requests.get(query)
            if response.status_code == 200:
                self.crime_data = response.json()
                print(f"✓ Fetched {len(self.crime_data)} crime records")
        except Exception as e:
            print(f"✗ Error fetching crime data: {e}")
        
        # Fetch 311 data
        try:
            date_30_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
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
            if self.datasf_token:
                query += f"&$$app_token={self.datasf_token}"
                
            response = requests.get(query)
            if response.status_code == 200:
                self.hazard_data = response.json()
                print(f"✓ Fetched {len(self.hazard_data)} hazard reports")
        except Exception as e:
            print(f"✗ Error fetching 311 data: {e}")
    
    def generate_segments(self, num_samples=5000):
        """Generate random street segments across SF"""
        segments = []
        
        for _ in range(num_samples):
            lat = random.uniform(self.bounds['south'], self.bounds['north'])
            lng = random.uniform(self.bounds['west'], self.bounds['east'])
            
            # Skip water areas
            if self.is_walkable_area(lat, lng):
                segments.append({'lat': lat, 'lng': lng})
        
        return segments
    
    def is_walkable_area(self, lat, lng):
        """Check if coordinates are walkable"""
        if lat < 37.795 and lng > -122.390:  # Bay Bridge area
            return False
        if lng < -122.510:  # Ocean side
            return False
        if lat < 37.750 and lng > -122.380:  # SF Bay
            return False
        return True
    
    def calculate_features_for_segment(self, lat, lng):
        """Calculate safety features for a location"""
        features = {}
        
        # Crime features
        violent_crimes = 0
        property_crimes = 0
        drug_crimes = 0
        recent_crimes = 0
        
        violent_types = ['Assault', 'Robbery', 'Homicide', 'Rape', 'Human Trafficking']
        property_types = ['Burglary', 'Larceny Theft', 'Motor Vehicle Theft', 'Arson']
        drug_types = ['Drug Offense', 'Drug Violation']
        
        for crime in self.crime_data:
            try:
                crime_lat = float(crime.get('latitude', 0))
                crime_lng = float(crime.get('longitude', 0))
                
                # Check if within 200m
                if abs(crime_lat - lat) < 0.002 and abs(crime_lng - lng) < 0.002:
                    crime_type = crime.get('incident_category', '')
                    
                    if crime_type in violent_types:
                        violent_crimes += 1
                    elif crime_type in property_types:
                        property_crimes += 1
                    elif crime_type in drug_types:
                        drug_crimes += 1
                    
                    # Check if recent (last 7 days)
                    crime_date = datetime.strptime(crime.get('incident_datetime', '2024-01-01'), 
                                                  '%Y-%m-%dT%H:%M:%S.%f')
                    if (datetime.now() - crime_date).days <= 7:
                        recent_crimes += 1
                        
            except:
                continue
        
        features['violent_crimes'] = violent_crimes
        features['property_crimes'] = property_crimes
        features['drug_crimes'] = drug_crimes
        features['recent_crimes'] = recent_crimes
        
        # Hazard features
        street_hazards = 0
        encampments = 0
        needles = 0
        blocked_sidewalks = 0
        
        for hazard in self.hazard_data:
            try:
                hazard_lat = float(hazard.get('lat', 0))
                hazard_lng = float(hazard.get('long', 0))
                
                # Check if within 100m
                if abs(hazard_lat - lat) < 0.001 and abs(hazard_lng - lng) < 0.001:
                    service_type = hazard.get('service_name', '')
                    
                    if 'Street' in service_type or 'Sidewalk' in service_type:
                        street_hazards += 1
                    if 'Encampment' in service_type or 'Homeless' in service_type:
                        encampments += 1
                    if 'Needle' in service_type:
                        needles += 1
                    if 'Blocked' in service_type:
                        blocked_sidewalks += 1
                        
            except:
                continue
        
        features['street_hazards'] = street_hazards
        features['encampments'] = encampments
        features['needles_reported'] = needles
        features['blocked_sidewalks'] = blocked_sidewalks
        
        # Time features
        now = datetime.now()
        features['hour'] = now.hour
        features['is_night'] = 1 if (now.hour < 6 or now.hour > 20) else 0
        features['is_weekend'] = 1 if now.weekday() >= 5 else 0
        
        # Simulated infrastructure features (would come from real data)
        features['lighting_quality'] = random.uniform(0, 1)
        features['sidewalk_width'] = random.uniform(1.2, 3.5)
        features['pedestrian_traffic'] = random.uniform(0, 1)
        features['nearest_safe_haven_distance'] = random.uniform(50, 500)
        features['cctv_coverage'] = random.choice([0, 1])
        features['escape_routes'] = random.randint(1, 5)
        
        return features
    
    def calculate_safety_label(self, features):
        """Calculate if location is safe (0) or unsafe (1)"""
        risk_score = 0
        
        # Crime-based risk
        if features['violent_crimes'] > 5:
            risk_score += 30
        elif features['violent_crimes'] > 2:
            risk_score += 15
        
        if features['property_crimes'] > 10:
            risk_score += 15
        
        if features['recent_crimes'] > 3:
            risk_score += 20
        
        # Hazard-based risk
        if features['encampments'] > 2:
            risk_score += 15
        if features['needles_reported'] > 0:
            risk_score += 10
        if features['blocked_sidewalks'] > 1:
            risk_score += 5
        
        # Environmental risk
        if features['is_night']:
            risk_score += 15
        if features['lighting_quality'] < 0.3:
            risk_score += 15
        if features['pedestrian_traffic'] < 0.2:
            risk_score += 10
        if features['cctv_coverage'] == 0:
            risk_score += 5
        if features['escape_routes'] < 2:
            risk_score += 10
        
        # Return 1 if unsafe, 0 if safe
        return 1 if risk_score >= 50 else 0
    
    def generate_dataset(self, num_samples=5000):
        """Generate the complete dataset"""
        print("\n" + "="*60)
        print("SAFEPATH SF SIMPLE DATASET GENERATOR")
        print("="*60 + "\n")
        
        # Fetch data
        self.fetch_all_data()
        
        # Generate samples
        print(f"\nGenerating {num_samples} data points...")
        segments = self.generate_segments(num_samples)
        
        dataset = []
        for i, segment in enumerate(segments):
            if i % 500 == 0:
                print(f"  Processing {i}/{num_samples}...")
            
            features = self.calculate_features_for_segment(segment['lat'], segment['lng'])
            features['is_unsafe'] = self.calculate_safety_label(features)
            dataset.append(features)
        
        # Convert to DataFrame
        df = pd.DataFrame(dataset)
        
        # Reorder columns to put target at the end
        cols = [col for col in df.columns if col != 'is_unsafe'] + ['is_unsafe']
        df = df[cols]
        
        # Print statistics
        print("\n" + "="*60)
        print("DATASET STATISTICS")
        print("="*60)
        print(f"Total data points: {len(df)}")
        print(f"Safe locations (0): {len(df[df['is_unsafe'] == 0])} ({len(df[df['is_unsafe'] == 0])/len(df)*100:.1f}%)")
        print(f"Unsafe locations (1): {len(df[df['is_unsafe'] == 1])} ({len(df[df['is_unsafe'] == 1])/len(df)*100:.1f}%)")
        print(f"\nFeatures ({len(df.columns)-1}):")
        for col in df.columns:
            if col != 'is_unsafe':
                print(f"  - {col}")
        print(f"\nTarget variable: is_unsafe (0=safe, 1=unsafe)")
        
        return df
    
    def save_dataset(self, df, filename="sf_safety_simple.csv"):
        """Save dataset to CSV"""
        filepath = os.path.join('data', filename)
        os.makedirs('data', exist_ok=True)
        
        df.to_csv(filepath, index=False)
        print(f"\n✓ Dataset saved to: {filepath}")
        print(f"  File size: {os.path.getsize(filepath) / 1024:.2f} KB")
        
        return filepath


def main():
    """Main execution"""
    generator = SimpleSafetyDatasetGenerator()
    
    # Generate dataset
    df = generator.generate_dataset(num_samples=5000)
    
    # Save to CSV
    filepath = generator.save_dataset(df)
    
    # Display sample
    print("\n" + "="*60)
    print("SAMPLE DATA (First 5 rows)")
    print("="*60)
    print(df.head())
    
    print("\n✅ Dataset ready for ML training!")
    print("\nUsage example:")
    print("```python")
    print("import pandas as pd")
    print("from sklearn.model_selection import train_test_split")
    print("from sklearn.ensemble import RandomForestClassifier")
    print("")
    print("# Load data")
    print(f"df = pd.read_csv('{filepath}')")
    print("X = df.drop('is_unsafe', axis=1)")
    print("y = df['is_unsafe']")
    print("")
    print("# Train model")
    print("X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)")
    print("model = RandomForestClassifier()")
    print("model.fit(X_train, y_train)")
    print("```")


if __name__ == "__main__":
    main()