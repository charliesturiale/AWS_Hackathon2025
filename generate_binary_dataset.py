#!/usr/bin/env python3
"""
SafePath SF Binary Dataset Generator
Generates a CSV with only 0 (safe) or 1 (unsafe) values
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import random
import os

def generate_binary_safety_dataset():
    """Generate dataset with only 0/1 values based on SF data"""
    
    print("Fetching San Francisco crime and hazard data...")
    
    # Fetch crime data
    crime_data = []
    try:
        date_90_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        response = requests.get(
            f"https://data.sfgov.org/resource/wg3w-h783.json?$where=incident_datetime>'{date_90_days_ago}'&$limit=50000"
        )
        if response.status_code == 200:
            crime_data = response.json()
            print(f"✓ Fetched {len(crime_data)} crime records")
    except:
        print("✗ Could not fetch crime data")
    
    # Fetch 311 hazard data
    hazard_data = []
    try:
        date_30_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        response = requests.get(
            f"https://data.sfgov.org/resource/vw6y-z8j6.json?$where=requested_datetime>'{date_30_days_ago}'&$limit=10000"
        )
        if response.status_code == 200:
            hazard_data = response.json()
            print(f"✓ Fetched {len(hazard_data)} hazard reports")
    except:
        print("✗ Could not fetch hazard data")
    
    print("\nGenerating safety labels based on data density...")
    
    # Generate safety labels based on crime/hazard density
    labels = []
    
    # San Francisco bounds
    bounds = {
        'north': 37.812,
        'south': 37.708,
        'west': -122.520,
        'east': -122.357
    }
    
    # Generate 10000 data points
    num_samples = 10000
    
    for i in range(num_samples):
        # Random location in SF
        lat = random.uniform(bounds['south'], bounds['north'])
        lng = random.uniform(bounds['west'], bounds['east'])
        
        # Count nearby incidents
        crime_count = 0
        hazard_count = 0
        
        # Count crimes within ~200m
        for crime in crime_data:
            try:
                crime_lat = float(crime.get('latitude', 0))
                crime_lng = float(crime.get('longitude', 0))
                if abs(crime_lat - lat) < 0.002 and abs(crime_lng - lng) < 0.002:
                    crime_count += 1
            except:
                continue
        
        # Count hazards within ~100m
        for hazard in hazard_data:
            try:
                hazard_lat = float(hazard.get('lat', 0))
                hazard_lng = float(hazard.get('long', 0))
                if abs(hazard_lat - lat) < 0.001 and abs(hazard_lng - lng) < 0.001:
                    hazard_count += 1
            except:
                continue
        
        # Simple rule: unsafe if high crime/hazard density
        # Adjust thresholds based on data
        is_unsafe = 1 if (crime_count > 5 or hazard_count > 2) else 0
        
        # Add some time-based risk (night hours)
        hour = datetime.now().hour
        if hour < 6 or hour > 22:
            # Higher chance of unsafe at night
            if random.random() < 0.3:  # 30% chance
                is_unsafe = 1
        
        labels.append(is_unsafe)
        
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{num_samples} locations...")
    
    # Create DataFrame with single column
    df = pd.DataFrame({'is_unsafe': labels})
    
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    filepath = 'data/sf_safety_binary.csv'
    df.to_csv(filepath, index=False, header=False)  # No header, just values
    
    # Statistics
    safe_count = labels.count(0)
    unsafe_count = labels.count(1)
    
    print("\n" + "="*60)
    print("DATASET GENERATED")
    print("="*60)
    print(f"Total rows: {len(labels)}")
    print(f"Safe (0): {safe_count} ({safe_count/len(labels)*100:.1f}%)")
    print(f"Unsafe (1): {unsafe_count} ({unsafe_count/len(labels)*100:.1f}%)")
    print(f"\n✓ Saved to: {filepath}")
    print(f"File size: {os.path.getsize(filepath) / 1024:.2f} KB")
    
    # Show sample
    print("\nFirst 20 values:")
    print(labels[:20])
    
    return filepath

if __name__ == "__main__":
    generate_binary_safety_dataset()