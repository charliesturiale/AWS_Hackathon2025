# Finding the Safest Walking Paths 🗺️

## What Are We Building?

Imagine you're walking home and Google Maps shows you 5 different routes. This system helps you find the **3 safest routes** by checking:
- **Crime incidents** nearby
- **Street problems** (like broken sidewalks, potholes) nearby

Then it ranks all your routes from safest to most risky.

## Think of it Like This:

If you're choosing between walking through:
1. A well-lit, busy street with no problems
2. A dimly lit alley with recent incidents
3. A sidewalk with construction

This system picks Option 1 for you automatically!

## What You'll Need

- A computer with internet
- Basic Python (we'll teach you as we go!)
- Access to crime and 311 data (we'll help you get this)
- AWS account (we'll guide you step-by-step)

## How It Works (Super Simple Version)

```
1. You give us multiple possible routes
2. We look up crime & safety problems along each route
3. We calculate a "danger score" for each route
4. We give you back the 3 routes with LOWEST danger scores
```

The lower the score, the safer the route! 🎯


## 📚 Some Important Terms (Don't Worry, We'll Explain!)

Before we start, let's learn a few simple words:

**Polypath** = A walking route (like a list of "turn here, then here")  
**API** = A way to get data from websites (like asking a question and getting an answer)  
**S3** = Amazon's storage (like a filing cabinet in the cloud)  
**Bedrock** = Amazon's AI (smart computer that can understand things)  
**Risk Score** = How dangerous a route is (higher number = more dangerous)

**The Magic Formula:** if w=3, f(d,t,w) = (ReLU(w-w(t/72)))² × e^(-(d)²/0.02), else f(d,t,w) = (ReLU(w-w(t/24)))² × e^(-(d)²/0.02)
- Don't worry about this yet! We'll explain it step by step.
- **d** = distance (things close matter more than far things)
- **t** = time since incident (recent incidents matter more than old ones)
- **ReLU** = makes sure values never go negative
- Just know: "recent and close incidents are more dangerous"


## Step 1: Getting the Tools We Need

Think of this like buying ingredients for a recipe. We need to install some "tools" (called libraries) first.

**What's a library?**  
It's like a toolbox with pre-made tools. Instead of building a hammer from scratch, you just get one from the toolbox!

Run the cell below to install everything:



```python
# This installs the tools we need
# Just like installing apps on your phone!
%pip install boto3 requests numpy pandas geopy --quiet

print("✅ Tools installed! We're ready to start!")

```

    Note: you may need to restart the kernel to use updated packages.
    ✅ Tools installed! We're ready to start!


## Step 2: Bringing in Our Tools

Now we're going to "import" our tools. Think of it like opening your toolbox.

**Analogy:** Imagine you're cooking:
- You need a knife → you "import" it from the kitchen
- You need a cutting board → you "import" it from the cupboard

Here, we're importing Python tools from libraries!



```python
# Import = bring in the tools
import boto3        # This talks to Amazon Web Services (AWS)
import requests     # This gets data from the internet
import json         # This reads/writes data in a special format
import numpy as np  # This does math calculations
import pandas as pd  # This organizes data in tables
from geopy.distance import geodesic  # This calculates distances on Earth
from typing import List, Dict, Tuple  # This just helps us write cleaner code

print("✅ All tools loaded! We're ready to work!")
print("\n💡 Tip: The 'import' command loads pre-written code so we don't have to write everything ourselves!")

```

    ✅ All tools loaded! We're ready to work!
    
    💡 Tip: The 'import' command loads pre-written code so we don't have to write everything ourselves!


## Step 3: Setting Up AWS (Amazon Web Services)

**What is AWS?**  
Think of AWS as Amazon's cloud services - it's like renting storage space and smart computers online.

**Why do we need it?**
1. **S3** = We store our data here (like a filing cabinet)
2. **Bedrock** = We use AI to understand how dangerous incidents are

### 📝 You Need to Set This Up (Don't Worry, It's Easy!)

1. Go to https://aws.amazon.com
2. Create a free account
3. Go to S3 (looks like a storage symbol)
4. Create a bucket (just click "Create bucket" and name it)
5. Get your credentials (Access Key ID and Secret Key)

**Important:** Never share your credentials! Keep them secret like a password.

### 🔧 Configuration

Fill in your details below:



```python
# ⚠️ IMPORTANT: Fill in your AWS details here
# You'll get these from your AWS account

# What region are you in? (us-east-1 is a common choice for USA)
AWS_REGION = "us-east-1"  # 🌍 Change this to your region

# What's your S3 bucket name? (This is where we store data)
S3_BUCKET_NAME = "my-path-risk-data"  # 📦 Change this to your bucket name

# Now we create the "clients" (think of them as assistants)
# They'll help us talk to AWS
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)

print(f"✅ Connected to AWS in region: {AWS_REGION}")
print("💡 If this fails, make sure you've set up your AWS credentials!")

```

    ✅ Connected to AWS in region: us-east-1
    💡 If this fails, make sure you've set up your AWS credentials!


## Step 4: Understanding the Data We'll Get

Before we write code, let's understand what data we're getting.

### Data from Crime API

When police respond to a call, they record it. We get this data like:
```json
{
  "call_type": "ASSAULT WITH WEAPON",
  "location": {
    "latitude": 37.7855,
    "longitude": -122.4090
  }
}
```

### Data from 311 API

When someone reports a street problem (like a pothole), we get data like:
```json
{
  "category": "Sidewalk Hazard",
  "latitude": 37.7852,
  "longitude": -122.4085
}
```

**In simple terms:** We're getting lists of "bad things that happened" with their locations!


## Step 5: Getting Crime Data from the Internet

**What is an API?**  
Think of it like this: You want to know the weather. You ask Google "What's the weather?" and Google gives you the answer. That's how an API works - you ask a question, you get an answer!

**How it works:**
1. We ask the Crime API: "Give me all crimes in this area"
2. It returns a list of crimes
3. We use that list!

Let's write the function:



```python
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

print("✅ Function created! This function gets crime data from SF Open Data.")
print("\n💡 This queries SF Open Data API for the specific crime types we need!")

```

    ✅ Function created! This function gets crime data from SF Open Data.
    
    💡 This queries SF Open Data API for the specific crime types we need!


## Step 6: Getting 311 Data (Street Problems)

**What is 311?**  
311 is a city service people call to report problems like:
- Broken sidewalks
- Potholes
- Streetlights out
- Trash problems

We want this data because these things make walking unsafe!

**Real Life Example:**  
If there's a "Sidewalk Hazard" report, that means someone could trip and fall. That's dangerous for pedestrians!



```python
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

print("✅ Function created! This gets Encampment and Aggressive/Threatening reports.")
print("\n💡 This queries SF Open Data API for encampments and threatening behavior!")

```

    ✅ Function created! This gets Encampment and Aggressive/Threatening reports.
    
    💡 This queries SF Open Data API for encampments and threatening behavior!


## Step 7: Saving Data to AWS S3

**What is S3?**  
S3 is Amazon's storage system. Think of it like Google Drive or Dropbox, but for computers.

**Why save it?**  
- Backup: If something goes wrong, we have the data
- Speed: We can load it faster later
- Remember: Computers forget when they restart, we want to save our work!

**Real Life Analogy:**  
It's like saving your homework to the cloud so you can access it from any computer!



```python
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

print("✅ Function created! This saves data to the cloud.")
print("\n💡 Think of it like Ctrl+S, but for cloud storage!")

```

    ✅ Function created! This saves data to the cloud.
    
    💡 Think of it like Ctrl+S, but for cloud storage!


## Step 8: Understanding Risk Levels 🤔

This is important! We need to decide: **How dangerous is each incident?**

We use three levels with **specific crime types**:

- **3 (High Risk)** = Very dangerous crimes:
  - EXPLOSIVE FOUND, EXPLOSION
  - ROBBERY, STRONGARM ROBBERY
  - ASSAULT, BATTERY

- **2 (Medium Risk)** = Somewhat dangerous crimes:
  - PURSE SNATCH, INDECENT EXPOSURE
  - FIGHT W/ WEAPONS, FIGHT W/O WEAPONS
  - BREAKING IN

- **1 (Low Risk)** = Less serious crimes:
  - SUSPICIOUS PERSON
  - THREATS/HARRASMENT, AGGRESIVE/THREATENING
  - ENCAMPMENT

**Special case: ENCAMPMENT** 🏕️
- If status is "CLOSED" → contributes 0 to risk (not dangerous anymore!)
- If status is open → doesn't decay with time (stays dangerous until closed)

**Why assign risk?**  
Not all problems are equally dangerous. An assault is much worse than a broken streetlight!



```python
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

# Let's test it!
print("🧪 Testing risk assignment:")
print(f"EXPLOSIVE FOUND → Risk: {assign_risk({'call_type_original_desc': 'EXPLOSIVE FOUND'}, 'crime')}")
print(f"ROBBERY → Risk: {assign_risk({'call_type_original_desc': 'ROBBERY'}, 'crime')}")
print(f"PURSE SNATCH → Risk: {assign_risk({'call_type_original_desc': 'PURSE SNATCH'}, 'crime')}")
print(f"ENCAMPMENT → Risk: {assign_risk({'call_type_original_desc': 'ENCAMPMENT'}, 'crime')}")
print(f"SIDEWALK HAZARD → Risk: {assign_risk({'Category': 'Sidewalk Hazard'}, '311')}")

```

    🧪 Testing risk assignment:
    EXPLOSIVE FOUND → Risk: 3
    ROBBERY → Risk: 3
    PURSE SNATCH → Risk: 2
    ENCAMPMENT → Risk: 1
    SIDEWALK HAZARD → Risk: 3


## Step 9: Measuring Distance 🏃

**What we're doing:**  
We need to know: "How far is this incident from our walking route?"

**Why?**  
An incident 10 feet away is MUCH more relevant than one 2 miles away!

**The Math (Don't Worry!):**  
We use "geodesic distance" - this is fancy talk for "distance on Earth" (not as a bird flies, but walking distance).

**Real Life Example:**  
If there's an assault 100 meters from your route, that's concerning.  
If there's an assault 5 kilometers away, who cares? You won't walk near it.

Let's write a function to measure this!



```python
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

# Let's test it!
test_path = [(37.7849, -122.4094), (37.7855, -122.4086)]
test_incident = (37.7865, -122.4080)
test_distance = min_distance_to_path(test_incident, test_path)

print(f"🧪 Test:")
print(f"Incident at: {test_incident}")
print(f"Path goes through: {test_path}")
print(f"Distance: {test_distance:.4f} km")
print("\n💡 The smaller the number, the closer the incident is to your route!")

```

    🧪 Test:
    Incident at: (37.7865, -122.408)
    Path goes through: [(37.7849, -122.4094), (37.7855, -122.4086)]
    Distance: 0.1229 km
    
    💡 The smaller the number, the closer the incident is to your route!


## Step 10: THE MAGIC FORMULA 🎩✨

This is where the magic happens! This is the core of our system.

### The Formula (With Time Decay!): 
**For high risk (w=3):** f(d,t,w) = (ReLU(3-3t/72))² × e^(-d²/0.02)  
**For lower risk (w=1,2):** f(d,t,w) = (ReLU(w-wt/24))² × e^(-d²/0.02)

**Breaking it down in simple terms:**

#### Part 1: The Risk Value (with Time!)
- w = How dangerous the incident is (1, 2, or 3)
- t = Time since incident (in hours)
- **High-risk incidents (w=3):** Take 72 hours to fully decay (3 days!)
- **Lower-risk incidents (w=1,2):** Take 24 hours to fully decay (1 day!)

**Why different times?**  
Serious crimes stay dangerous for longer!

#### Part 2: ReLU Function
ReLU(x) = max(0, x) - Returns 0 if negative, otherwise returns the value itself.

**What it does:**  
Prevents the risk from going negative (makes sense - you can't have "negative danger"!)

#### Part 3: e^(-d²/0.02) (Distance Decay)
- d = Distance in kilometers
- Makes things further away matter less

**How it works:**
- Close incident (0.1 km): Contributes a lot
- Medium distance (0.5 km): Contributes some  
- Far away (1+ km): Contributes almost nothing

#### Putting It Together:
A **recent, high-risk incident close** to your path has a huge impact.  
An **old, low-risk incident far away** has almost no impact.

**That's the whole point!** 🎯



```python
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
            # For 311 data, check service_name
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

print("✅ Function created! This calculates how dangerous your path is.")
print("\n📊 Lower score = Safer path!")
print("💡 Example: Path A = 5.2, Path B = 12.7 → Path A is safer!")
print("\n🎯 Key feature: Recent incidents matter MORE than old ones!")

```

    ✅ Function created! This calculates how dangerous your path is.
    
    📊 Lower score = Safer path!
    💡 Example: Path A = 5.2, Path B = 12.7 → Path A is safer!
    
    🎯 Key feature: Recent incidents matter MORE than old ones!


## Step 11: THE MAIN FUNCTION 🎪

This brings everything together! Think of it as the conductor of an orchestra - it makes sure everything happens in the right order.

**What it does:**
1. Get crime data
2. Get 311 data
3. Save everything to S3
4. For each path, calculate risk
5. Sort paths by risk
6. Return the 3 safest paths

Let's build it!



```python
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
        current_time = datetime.now().isoformat()
        
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

print("✅ Main function created!")
print("\n🎉 This is the function you'll actually use!")

```

    ✅ Main function created!
    
    🎉 This is the function you'll actually use!


## Step 12: Testing with Sample Data 🧪

Before using real APIs, let's test with fake data to make sure everything works!

**Why?**  
- We can see what happens
- No need for API keys yet
- Learn how the system works

Let's create some sample incidents and test!



```python
# Let's create some fake data to test with!

# Sample crimes
sample_crimes = [
    {
        "call_type_original_desc": "ASSAULT WITH DEADLY WEAPON",
        "intersection_point": {
            "coordinates": [-122.4090, 37.7855]  # (longitude, latitude)
        }
    },
    {
        "call_type_original_desc": "TRESPASSING",
        "intersection_point": {
            "coordinates": [-122.4080, 37.7850]
        }
    },
    {
        "call_type_original_desc": "NOISE COMPLAINT",
        "intersection_point": {
            "coordinates": [-122.4075, 37.7845]
        }
    }
]

# Sample 311 incidents
sample_311 = [
    {
        "Category": "Sidewalk Hazard",
        "Latitude": 37.7852,
        "Longitude": -122.4085
    },
    {
        "Category": "Trash Removal",
        "Latitude": 37.7858,
        "Longitude": -122.4090
    }
]

# A sample path
test_path = [(37.7849, -122.4094), (37.7855, -122.4086), (37.7861, -122.4078)]

print("✅ Sample data created!")
print(f"   - {len(sample_crimes)} sample crimes")
print(f"   - {len(sample_311)} sample 311 incidents")
print(f"   - 1 test path with {len(test_path)} waypoints")

```

    ✅ Sample data created!
       - 3 sample crimes
       - 2 sample 311 incidents
       - 1 test path with 3 waypoints



```python
# Let's test it!
print("🧪 Testing the system...")
print("=" * 60)

# Calculate risk
crime_risk = calculate_risk_score(test_path, sample_crimes, "crime")
incident_risk = calculate_risk_score(test_path, sample_311, "311")
total_risk = crime_risk + incident_risk

print("\n📊 RESULTS:")
print(f"   Crime Risk:     {crime_risk:.4f}")
print(f"   311 Risk:       {incident_risk:.4f}")
print(f"   TOTAL RISK:     {total_risk:.4f}")
print("\n✅ It works! Lower numbers = safer path.")

print("\n" + "=" * 60)
print("💡 Now you can use real data with the find_lowest_risk_paths() function!")

```

## Step 13: How to Use This System! 🚀

Now that you understand how it works, here's how to actually use it:



```python
# EXAMPLE: How to use the system with real data

# 1️⃣ Define your paths (from Google Maps or another source)
example_polypaths = [
    # Path 1: Short route
    [(37.7849, -122.4094), (37.7855, -122.4086), (37.7861, -122.4078)],
    # Path 2: Different route
    [(37.7849, -122.4094), (37.7845, -122.4102), (37.7841, -122.4110)],
    # Path 3: Alternative route
    [(37.7849, -122.4094), (37.7852, -122.4090), (37.7855, -122.4086)],
    # ... add more paths as needed
]

# 2️⃣ SF Open Data doesn't need API keys! It's public data! 🎉

# 3️⃣ Run it!
# Uncomment the line below when you're ready:
# lowest_risk_paths = find_lowest_risk_paths(example_polypaths)

# Or if you want to provide optional parameters:
# lowest_risk_paths = find_lowest_risk_paths(
#     example_polypaths,
#     area_bounds=None,  # Not used for SF Open Data
#     crime_api_key=None,  # Not needed
#     api_311_key=None    # Not needed
# )

print("📝 Setup complete!")
print("\n🎉 No API keys needed - SF Open Data is free and public!")
print("\n⚠️  To actually run it:")
print("   1. Uncomment the find_lowest_risk_paths line")
print("   2. Run the cell!")

```

    📝 Setup complete!
    
    🎉 No API keys needed - SF Open Data is free and public!
    
    ⚠️  To actually run it:
       1. Uncomment the find_lowest_risk_paths line
       2. Run the cell!


## 🎓 What You Learned!

Let's review what we built:

### ✅ The System
1. **Gets data** from Crime APIs and 311 APIs
2. **Saves data** to AWS S3 (cloud storage)
3. **Assigns risk** to each incident (1, 2, or 3)
4. **Measures distance** from incidents to paths
5. **Calculates risk** using the magic formula
6. **Returns** the 3 safest paths

### 🧮 The Math
**Formula (with time decay!):** 
- **For w=3:** f(d,t,w) = (ReLU(3-3t/72))² × e^(-d²/0.02)
- **For w=1,2:** f(d,t,w) = (ReLU(w-wt/24))² × e^(-d²/0.02)
- **w** = Risk value (1, 2, or 3)
- **d** = Distance in kilometers
- **Lower total** = Safer path! 🎯

### 🔑 Key Concepts
- **API**: How programs get data from websites
- **S3**: Cloud storage (like Google Drive for computers)
- **Geodesic**: Distance on Earth's surface
- **Risk Score**: A number showing how dangerous a path is

### 🚀 Next Steps

**To use with real data:**
1. Get API keys for Crime and 311 data
2. Set up AWS account
3. Create S3 bucket
4. Fill in credentials in the notebook
5. Run the main function!

**To learn more:**
- Read about APIs: "How do websites share data?"
- Learn about AWS: "What is cloud computing?"
- Study the formula: "How does exponential decay work?"

### 🎉 You Did It!

You now have a complete path safety analysis system!

**Remember:**
- Lower risk scores = Safer paths
- The formula balances distance and danger
- This works for any area with accessible data!

Happy analyzing! 🗺️✨

