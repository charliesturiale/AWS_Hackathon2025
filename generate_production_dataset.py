#!/usr/bin/env python3
"""
SafePath SF Production Dataset Generator
Follows exact DataSF API specifications for optimal performance
Outputs binary safety labels (0/1) only
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import random
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class OptimizedSafetyDatasetGenerator:
    def __init__(self):
        """Initialize with optimized API endpoints and filters"""
        self.sf_bounds = {
            'north': 37.812,
            'south': 37.708,
            'west': -122.520,
            'east': -122.357
        }
        
        # Optimized API queries based on specification
        self.api_queries = {
            'crime': self.build_crime_query(),
            'calls_911': self.build_911_query(),
            'hazards_311': self.build_311_query()
        }
        
        # Store fetched data
        self.crime_data = []
        self.calls_data = []
        self.hazards_data = []
        
    def build_crime_query(self):
        """Build optimized crime query per specification"""
        base = "https://data.sfgov.org/resource/wg3w-h783.json"
        
        # High-risk crime categories
        crime_types = [
            'Assault', 'Robbery', 'Homicide', 'Larceny Theft',
            'Weapons Offense', 'Sex Offense', 'Drug Offense',
            'Human Trafficking', 'Stolen Property', 'Traffic Collision',
            'Vandalism'
        ]
        
        # Last 2 years of data
        date_from = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        
        # Build WHERE clause
        crime_filter = ' OR '.join([f"incident_category='{c}'" for c in crime_types])
        where = f"incident_datetime>'{date_from}' AND ({crime_filter})"
        
        return f"{base}?$where={where}&$limit=50000&$select=incident_datetime,incident_category,latitude,longitude,analysis_neighborhood"
    
    def build_911_query(self):
        """Build optimized 911 dispatch query per specification"""
        base = "https://data.sfgov.org/resource/gnap-fj3t.json"
        
        # High-priority call types
        call_types = [
            'Assault', 'Robbery', 'Disturbance', 'Person Down',
            'Traffic Accident', 'Weapons Call', 'Auto Boost/Break-In',
            'Suspicious Occurrence', 'Mental Health Call', 'Prowler',
            'Shots Fired', 'Vandalism'
        ]
        
        # Last 48 hours for real-time
        date_from = (datetime.now() - timedelta(hours=48)).strftime('%Y-%m-%dT%H:%M:%S')
        
        call_filter = ' OR '.join([f"call_type_original='{c}'" for c in call_types])
        where = f"received_dt>'{date_from}' AND status_description='Open' AND ({call_filter})"
        
        return f"{base}?$where={where}&$limit=10000&$select=received_dt,call_type_original,latitude,longitude,priority_description"
    
    def build_311_query(self):
        """Build optimized 311 hazards query per specification"""
        base = "https://data.sfgov.org/resource/vw6y-z8j6.json"
        
        # Safety-critical case types
        case_types = [
            'Homeless Concerns', 'Street or Sidewalk Cleaning',
            'Public Health Hazard', 'Street Lights', 'Sidewalk or Curb',
            'Needles/Syringes', 'Blocked Sidewalk or Street', 'Encampment'
        ]
        
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        case_filter = ' OR '.join([f"case_type='{c}'" for c in case_types])
        where = f"requested_datetime>'{date_from}' AND status_description='Open' AND ({case_filter})"
        
        return f"{base}?$where={where}&$limit=10000&$select=requested_datetime,case_type,lat,long,analysis_neighborhood"
    
    def fetch_data_parallel(self):
        """Fetch all data sources in parallel for speed"""
        print("Fetching data from SF APIs (parallel)...")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.fetch_api_data, 'crime'): 'crime',
                executor.submit(self.fetch_api_data, 'calls_911'): 'calls',  
                executor.submit(self.fetch_api_data, 'hazards_311'): 'hazards'
            }
            
            for future in as_completed(futures):
                data_type = futures[future]
                try:
                    data = future.result()
                    if data_type == 'crime':
                        self.crime_data = data
                        print(f"✓ Fetched {len(data)} crime records")
                    elif data_type == 'calls':
                        self.calls_data = data
                        print(f"✓ Fetched {len(data)} 911 calls")
                    else:
                        self.hazards_data = data
                        print(f"✓ Fetched {len(data)} 311 hazards")
                except Exception as e:
                    print(f"✗ Error fetching {data_type}: {e}")
    
    def fetch_api_data(self, query_type):
        """Fetch data from a specific API"""
        try:
            response = requests.get(self.api_queries[query_type], timeout=30)
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def calculate_risk_for_location(self, lat, lng):
        """Calculate risk score for a specific location"""
        risk_score = 0
        
        # Weight factors per specification
        weights = {
            'violent_crime': 30,
            'property_crime': 15,
            'drug_crime': 20,
            'priority_911': 25,
            'encampment': 20,
            'needles': 15,
            'blocked': 10,
            'lighting': 15
        }
        
        # Count nearby incidents (optimized with early exit)
        violent = ['Assault', 'Robbery', 'Homicide', 'Sex Offense', 'Weapons Offense']
        property = ['Larceny Theft', 'Stolen Property', 'Vandalism']
        drugs = ['Drug Offense']
        
        # Crime analysis (200m radius)
        for crime in self.crime_data[:1000]:  # Sample for speed
            try:
                clat = float(crime.get('latitude', 0))
                clng = float(crime.get('longitude', 0))
                if abs(clat - lat) < 0.002 and abs(clng - lng) < 0.002:
                    category = crime.get('incident_category', '')
                    if category in violent:
                        risk_score += weights['violent_crime']
                    elif category in property:
                        risk_score += weights['property_crime']
                    elif category in drugs:
                        risk_score += weights['drug_crime']
                    
                    if risk_score > 100:  # Early exit
                        return 1
            except:
                continue
        
        # 911 calls analysis
        high_priority = 0
        for call in self.calls_data[:500]:  # Recent calls only
            try:
                clat = float(call.get('latitude', 0))
                clng = float(call.get('longitude', 0))
                if abs(clat - lat) < 0.001 and abs(clng - lng) < 0.001:
                    if call.get('priority_description') in ['High', 'Priority 1']:
                        high_priority += 1
            except:
                continue
        
        if high_priority > 2:
            risk_score += weights['priority_911']
        
        # 311 hazards analysis
        encampments = 0
        needles = 0
        blocked = 0
        lighting = 0
        
        for hazard in self.hazards_data[:500]:
            try:
                hlat = float(hazard.get('lat', 0))
                hlng = float(hazard.get('long', 0))
                if abs(hlat - lat) < 0.001 and abs(hlng - lng) < 0.001:
                    case_type = hazard.get('case_type', '')
                    if 'Encampment' in case_type or 'Homeless' in case_type:
                        encampments += 1
                    elif 'Needle' in case_type:
                        needles += 1
                    elif 'Blocked' in case_type:
                        blocked += 1
                    elif 'Light' in case_type:
                        lighting += 1
            except:
                continue
        
        if encampments > 1:
            risk_score += weights['encampment']
        if needles > 0:
            risk_score += weights['needles']
        if blocked > 0:
            risk_score += weights['blocked']
        if lighting > 1:
            risk_score += weights['lighting']
        
        # Time-based risk
        hour = datetime.now().hour
        if hour < 6 or hour > 22:
            risk_score += 15
        
        # Return 1 if unsafe (risk > 50), else 0
        return 1 if risk_score > 50 else 0
    
    def generate_binary_dataset(self, num_samples=10000):
        """Generate dataset with only 0/1 values"""
        print(f"\nGenerating {num_samples} binary safety labels...")
        
        labels = []
        
        # Use stratified sampling for better coverage
        samples_per_batch = 100
        num_batches = num_samples // samples_per_batch
        
        for batch in range(num_batches):
            if batch % 10 == 0:
                print(f"  Processing batch {batch}/{num_batches}...")
            
            for _ in range(samples_per_batch):
                # Random location in SF
                lat = random.uniform(self.sf_bounds['south'], self.sf_bounds['north'])
                lng = random.uniform(self.sf_bounds['west'], self.sf_bounds['east'])
                
                # Skip water areas
                if lat < 37.795 and lng > -122.390:  # Bay
                    labels.append(0)
                    continue
                
                # Calculate safety
                is_unsafe = self.calculate_risk_for_location(lat, lng)
                labels.append(is_unsafe)
        
        return labels
    
    def save_binary_csv(self, labels, filename="sf_safety_binary_production.csv"):
        """Save binary labels to CSV without header"""
        filepath = os.path.join('data', filename)
        os.makedirs('data', exist_ok=True)
        
        # Save as single column CSV without header
        with open(filepath, 'w') as f:
            for label in labels:
                f.write(f"{label}\n")
        
        print(f"\n✓ Saved to: {filepath}")
        print(f"  File size: {os.path.getsize(filepath) / 1024:.2f} KB")
        return filepath
    
    def run(self, num_samples=10000):
        """Main execution pipeline"""
        print("\n" + "="*60)
        print("SAFEPATH SF PRODUCTION DATASET GENERATOR")
        print("="*60)
        
        start_time = time.time()
        
        # Fetch data in parallel
        self.fetch_data_parallel()
        
        # Generate binary labels
        labels = self.generate_binary_dataset(num_samples)
        
        # Save to CSV
        filepath = self.save_binary_csv(labels)
        
        # Statistics
        safe = labels.count(0)
        unsafe = labels.count(1)
        
        print("\n" + "="*60)
        print("DATASET COMPLETE")
        print("="*60)
        print(f"Total rows: {len(labels)}")
        print(f"Safe (0): {safe} ({safe/len(labels)*100:.1f}%)")
        print(f"Unsafe (1): {unsafe} ({unsafe/len(labels)*100:.1f}%)")
        print(f"Generation time: {time.time() - start_time:.1f} seconds")
        
        # Show sample
        print("\nFirst 50 values:")
        print(''.join(str(x) for x in labels[:50]))
        
        return filepath

def main():
    """Main entry point"""
    generator = OptimizedSafetyDatasetGenerator()
    generator.run(num_samples=10000)

if __name__ == "__main__":
    main()