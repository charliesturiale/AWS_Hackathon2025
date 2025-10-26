#!/usr/bin/env python3
"""
SafePath SF Final Dataset Generator
Uses exact API URLs provided for police reports and 311 cases
Outputs binary (0/1) CSV for ML model training
"""

import requests
import random
import os
from urllib.parse import unquote
import json

class FinalSafetyDataset:
    def __init__(self):
        """Initialize with exact API URLs"""
        
        # Police incidents - v2 API (no auth required)
        self.police_api_url = "https://data.sfgov.org/resource/wg3w-h783.json"
        
        # 311 cases
        self.cases_311_api_url = "https://data.sfgov.org/resource/vw6y-z8j6.json"
        
        # SF boundaries
        self.sf_bounds = {
            'north': 37.812,
            'south': 37.708,
            'west': -122.520,
            'east': -122.357
        }
        
        # Sample size for statistical validity (95% confidence, ±5% margin)
        self.sample_size = 385  # Standard sample size for unknown population
        
        # Data storage
        self.police_data = []
        self.cases_311_data = []
    
    def fetch_police_data(self):
        """Fetch police incident data with exact filters"""
        print("\nFetching Police Department Incident Reports...")
        print("  Filtering for serious crimes: Assault, Robbery, Burglary, etc.")
        
        # Crime categories from user specification
        crime_categories = [
            "Assault", "Burglary", "Disorderly Conduct", "Homicide",
            "Robbery", "Weapons Offense", "Larceny Theft", "Fire Report"
        ]
        
        all_incidents = []
        
        # Fetch data for each category (API doesn't handle OR conditions well)
        for category in crime_categories:
            params = {
                '$limit': '5000',
                'incident_year': '2024',  # Recent data
                'incident_category': category,
                '$order': 'incident_datetime DESC'
            }
            
            try:
                response = requests.get(self.police_api_url, params=params, timeout=30)
                if response.status_code == 200:
                    incidents = response.json()
                    # Filter out non-criminal subcategories
                    filtered = [i for i in incidents 
                               if i.get('incident_subcategory', '') not in 
                               ['Non-Criminal', 'Courtesy Report', 'Lost Property']]
                    all_incidents.extend(filtered)
                    print(f"  ✓ {category}: {len(filtered)} incidents")
            except Exception as e:
                print(f"  ✗ Error fetching {category}: {e}")
        
        # Also fetch 2023 data for more comprehensive dataset
        for category in crime_categories[:4]:  # Top categories for 2023
            params = {
                '$limit': '2000',
                'incident_year': '2023',
                'incident_category': category,
                '$order': 'incident_datetime DESC'
            }
            
            try:
                response = requests.get(self.police_api_url, params=params, timeout=30)
                if response.status_code == 200:
                    incidents = response.json()
                    filtered = [i for i in incidents 
                               if i.get('incident_subcategory', '') not in 
                               ['Non-Criminal', 'Courtesy Report', 'Lost Property']]
                    all_incidents.extend(filtered)
            except:
                pass  # Silent fail for 2023 data
        
        self.police_data = all_incidents
        print(f"\n✓ Total police incidents retrieved: {len(self.police_data)}")
        
        # Show sample of data
        if self.police_data:
            print("  Sample recent incidents:")
            for incident in self.police_data[:5]:
                cat = incident.get('incident_category', 'N/A')
                desc = incident.get('incident_description', 'N/A')[:30]
                intersection = incident.get('intersection', 'N/A')[:25]
                print(f"    - {cat}: {desc}... @ {intersection}")
    
    def fetch_311_data(self):
        """Fetch 311 cases data"""
        print("\nFetching 311 Cases...")
        
        # Get recent 311 cases
        from datetime import datetime, timedelta
        date_30_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        params = {
            '$where': f"requested_datetime > '{date_30_days_ago}' AND status_description='Open'",
            '$limit': '10000',
            '$select': 'service_request_id,service_name,lat,long'
        }
        
        try:
            response = requests.get(self.cases_311_api_url, params=params, timeout=30)
            if response.status_code == 200:
                self.cases_311_data = response.json()
                print(f"✓ Retrieved {len(self.cases_311_data)} 311 cases")
                
                # Show sample of data
                if self.cases_311_data:
                    print("  Sample service types:")
                    service_counts = {}
                    for case in self.cases_311_data[:100]:
                        service = case.get('service_name', 'Unknown')
                        service_counts[service] = service_counts.get(service, 0) + 1
                    
                    for service, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                        print(f"    - {service}: {count}")
            else:
                print(f"✗ Error: API returned status {response.status_code}")
        except Exception as e:
            print(f"✗ Error fetching 311 data: {e}")
    
    def generate_sample_points(self):
        """Generate stratified sample points across SF"""
        points = []
        
        # Create grid for stratified sampling
        grid_size = 0.004  # ~400m grid
        lat_steps = int((self.sf_bounds['north'] - self.sf_bounds['south']) / grid_size)
        lng_steps = int((self.sf_bounds['east'] - self.sf_bounds['west']) / grid_size)
        
        grid_points = []
        for i in range(lat_steps):
            for j in range(lng_steps):
                lat = self.sf_bounds['south'] + (i + 0.5) * grid_size
                lng = self.sf_bounds['west'] + (j + 0.5) * grid_size
                
                # Skip water areas
                if self.is_land(lat, lng):
                    grid_points.append((lat, lng))
        
        # Sample required number of points
        sample_count = min(self.sample_size, len(grid_points))
        points = random.sample(grid_points, sample_count)
        
        print(f"\n✓ Generated {len(points)} sample points from {len(grid_points)} grid cells")
        return points
    
    def is_land(self, lat, lng):
        """Check if point is on land"""
        # Simplified water exclusion
        if lat < 37.795 and lng > -122.390:  # Bay
            return False
        if lng < -122.510:  # Ocean
            return False
        if lat < 37.750 and lng > -122.380:  # South Bay
            return False
        return True
    
    def calculate_safety_label(self, lat, lng):
        """Calculate binary safety label based on incident density"""
        
        crime_count = 0
        hazard_count = 0
        radius = 0.003  # ~300m radius
        
        # Count nearby police incidents
        for incident in self.police_data:
            try:
                inc_lat = float(incident.get('latitude', 0))
                inc_lng = float(incident.get('longitude', 0))
                
                if inc_lat and inc_lng:
                    if abs(inc_lat - lat) <= radius and abs(inc_lng - lng) <= radius:
                        crime_count += 1
            except:
                continue
        
        # Count nearby 311 cases
        for case in self.cases_311_data:
            try:
                case_lat = float(case.get('lat', 0))
                case_lng = float(case.get('long', 0))
                
                if case_lat and case_lng:
                    if abs(case_lat - lat) <= radius and abs(case_lng - lng) <= radius:
                        hazard_count += 1
            except:
                continue
        
        # Risk scoring - both data sources must influence decision
        # Crime incidents have higher weight (violent/property crimes)
        # 311 cases have medium weight (quality of life issues)
        risk_score = (crime_count * 10) + (hazard_count * 2)
        
        # Recalibrated thresholds for realistic SF safety distribution
        # Target: ~30-40% unsafe areas (matches actual high-crime neighborhoods)
        # >8 serious crimes in 300m = definitely unsafe
        # >20 quality-of-life issues = potentially unsafe
        # Combined risk score >80 = unsafe
        return 1 if (crime_count > 8 or (crime_count > 5 and hazard_count > 15) or risk_score > 80) else 0
    
    def generate_dataset(self):
        """Generate the complete binary dataset"""
        print("\n" + "="*60)
        print("GENERATING ML-READY DATASET")
        print("="*60)
        
        # Fetch data from APIs
        self.fetch_police_data()
        self.fetch_311_data()
        
        if not self.police_data and not self.cases_311_data:
            print("\n✗ No data retrieved from APIs")
            return []
        
        # Generate sample points
        sample_points = self.generate_sample_points()
        
        # First pass: calculate risk scores for all points
        print("\nCalculating risk scores...")
        risk_scores = []
        
        for lat, lng in sample_points:
            crime_count = 0
            hazard_count = 0
            radius = 0.003  # ~300m radius
            
            # Count nearby police incidents
            for incident in self.police_data:
                try:
                    inc_lat = float(incident.get('latitude', 0))
                    inc_lng = float(incident.get('longitude', 0))
                    
                    if inc_lat and inc_lng:
                        if abs(inc_lat - lat) <= radius and abs(inc_lng - lng) <= radius:
                            crime_count += 1
                except:
                    continue
            
            # Count nearby 311 cases  
            for case in self.cases_311_data:
                try:
                    case_lat = float(case.get('lat', 0))
                    case_lng = float(case.get('long', 0))
                    
                    if case_lat and case_lng:
                        if abs(case_lat - lat) <= radius and abs(case_lng - lng) <= radius:
                            hazard_count += 1
                except:
                    continue
            
            # Calculate risk score
            risk_score = (crime_count * 10) + (hazard_count * 2)
            risk_scores.append(risk_score)
        
        # Calculate percentile threshold for ~35% unsafe
        sorted_scores = sorted(risk_scores)
        percentile_65 = sorted_scores[int(len(sorted_scores) * 0.65)]  # Top 35% are unsafe
        
        print(f"\nRisk score distribution:")
        print(f"  Min: {min(risk_scores)}")
        print(f"  65th percentile (threshold): {percentile_65}")
        print(f"  Max: {max(risk_scores)}")
        
        # Second pass: assign labels based on percentile
        print("\nAssigning safety labels...")
        labels = []
        
        for i, score in enumerate(risk_scores):
            if i % 50 == 0 and i > 0:
                print(f"  Processed {i}/{len(risk_scores)} points...")
            
            # Label as unsafe if in top 35% of risk scores
            label = 1 if score > percentile_65 else 0
            labels.append(label)
        
        return labels
    
    def save_csv(self, labels):
        """Save binary labels to CSV for ML"""
        filepath = 'data/sf_safety_ml_dataset.csv'
        os.makedirs('data', exist_ok=True)
        
        # Save as single column CSV without header (just 0s and 1s)
        with open(filepath, 'w') as f:
            for label in labels:
                f.write(f"{label}\n")
        
        # Calculate statistics
        safe = labels.count(0)
        unsafe = labels.count(1)
        
        print("\n" + "="*60)
        print("DATASET COMPLETE")
        print("="*60)
        print(f"Total samples: {len(labels)}")
        print(f"Safe (0): {safe} ({safe/len(labels)*100:.1f}%)")
        print(f"Unsafe (1): {unsafe} ({unsafe/len(labels)*100:.1f}%)")
        
        print(f"\n✓ CSV saved to: {filepath}")
        print(f"  File size: {os.path.getsize(filepath) / 1024:.2f} KB")
        
        # Show sample
        print(f"\nFirst 100 values:")
        print(''.join(str(x) for x in labels[:100]))
        
        print("\n📊 Ready for ML:")
        print(f"  - Binary classification dataset (0=safe, 1=unsafe)")
        print(f"  - {len(labels)} samples for city-wide extrapolation")
        print(f"  - Based on real police incidents and 311 cases")
        print(f"  - CSV format ready for scikit-learn, TensorFlow, etc.")
        
        return filepath

def main():
    """Main execution"""
    generator = FinalSafetyDataset()
    labels = generator.generate_dataset()
    
    if labels:
        generator.save_csv(labels)
    else:
        print("✗ Failed to generate dataset")

if __name__ == "__main__":
    main()