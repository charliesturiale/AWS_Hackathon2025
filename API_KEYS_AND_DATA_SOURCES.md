# SafePath SF - API Keys and Data Sources

## Required APIs and Data Sources

### 1. SF Open Data APIs (Free, No Key Required)

#### Police Incidents (Past)
- **API Endpoint**: `https://data.sfgov.org/resource/wg3w-h783.json`
- **Documentation**: https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-2018-to-Present/wg3w-h783
- **Fields**: incident_datetime, incident_category, latitude, longitude
- **Rate Limit**: 1000 requests per hour
```bash
# Example query for recent crimes
curl "https://data.sfgov.org/resource/wg3w-h783.json?\$where=incident_datetime>'2024-10-01'"
```

#### 311 Cases (Hazards)
- **API Endpoint**: `https://data.sfgov.org/resource/vw6y-z8j6.json`
- **Documentation**: https://data.sfgov.org/City-Infrastructure/311-Cases/vw6y-z8j6
- **Use for**: Street hazards, lighting issues, sidewalk problems
```bash
# Get street light outages
curl "https://data.sfgov.org/resource/vw6y-z8j6.json?service_name=Streetlight"
```

### 2. INRIX APIs (Hackathon Access)

#### Sign Up for INRIX Developer Account
- **Website**: https://developer.inrix.com/
- **Hackathon Access**: Will be provided at https://github.com/SCUACM/inrix-access-25 (when hacking starts)
- **Documentation**: https://docs.inrix.com/

#### Required INRIX APIs:
```javascript
// INRIX Configuration
const INRIX_CONFIG = {
  APP_ID: "YOUR_INRIX_APP_ID",  // Get from hackathon organizers
  APP_KEY: "YOUR_INRIX_APP_KEY", // Get from hackathon organizers
  BASE_URL: "https://api.inrix.com/v1",
  
  // Endpoints we need:
  INCIDENTS: "/incidents",        // Real-time incidents
  TRAFFIC: "/segments",           // Traffic flow data
  PARKING: "/blocks/parking",     // Parking availability
  ROUTES: "/findRoute"           // Route calculation
};
```

### 3. Bay/Golden Gate Bridge Data

#### 511 SF Bay API
- **Sign Up**: https://511.org/open-data/developers
- **API Key Required**: Yes (free)
- **Documentation**: https://511.org/developers/list/apis/
```javascript
const BAY_511_API = {
  KEY: "YOUR_511_API_KEY",
  BASE_URL: "http://api.511.org",
  TRAFFIC_ENDPOINT: "/traffic/trafficconditions"
};
```

#### Caltrans Performance Measurement System (PeMS)
- **Website**: https://pems.dot.ca.gov/
- **Registration**: Required (free for research)
- **Use for**: Real-time bridge traffic data

### 4. Mission/SOMA Incidents (Events)

#### DataSF Events Calendar
- **API**: https://datasf.org/opendata/
- **No key required**
```bash
# Get upcoming events
curl "https://data.sfgov.org/resource/b2xn-6qcy.json"
```

#### EventBrite API (for nightlife/events)
- **Sign Up**: https://www.eventbrite.com/platform/api
- **API Key**: Required (free tier available)
```javascript
const EVENTBRITE_CONFIG = {
  TOKEN: "YOUR_EVENTBRITE_TOKEN",
  BASE_URL: "https://www.eventbriteapi.com/v3",
  SF_VENUE_ENDPOINT: "/events/search/?location.address=San+Francisco"
};
```

### 5. Real-Time Construction/Events

#### SF Public Works - Construction Permits
- **API**: `https://data.sfgov.org/resource/i98e-djp9.json`
- **No key required**
```bash
# Active construction permits
curl "https://data.sfgov.org/resource/i98e-djp9.json?status=ACTIVE"
```

### 6. SF Infrastructure Data

#### Bart/Muni Stops
- **BART API**: http://api.bart.gov/docs/overview/index.aspx
- **Key Required**: Yes (free)
```javascript
const BART_API = {
  KEY: "YOUR_BART_API_KEY",  // Get from http://api.bart.gov/api/register.aspx
  BASE_URL: "http://api.bart.gov/api",
  STATIONS: "/stn.aspx",
  REAL_TIME: "/etd.aspx"
};
```

- **SFMTA/Muni**: https://www.sfmta.com/getting-around/transit/api
```javascript
const NEXTBUS_API = {
  // No key required for NextBus
  BASE_URL: "http://webservices.nextbus.com/service/publicJSONFeed",
  ROUTES: "?command=routeList&a=sf-muni",
  STOPS: "?command=routeConfig&a=sf-muni"
};
```

#### Street Lights/Cameras
- **Street Lights Database**: 
```bash
curl "https://data.sfgov.org/resource/vw6y-z8j6.json?service_subtype=Streetlight"
```

- **Public Cameras** (limited availability):
```bash
# Traffic cameras from 511
curl "http://api.511.org/traffic/cameras?api_key=YOUR_KEY&format=json"
```

### 7. Neighborhood-Specific Data

#### Tenderloin (High Crime)
```javascript
// Tenderloin boundary box for filtering
const TENDERLOIN_BOUNDS = {
  north: 37.7875,
  south: 37.7825,
  east: -122.4097,
  west: -122.4186
};

// Query crimes in Tenderloin
const query = `https://data.sfgov.org/resource/wg3w-h783.json?$where=latitude>${TENDERLOIN_BOUNDS.south} AND latitude<${TENDERLOIN_BOUNDS.north} AND longitude>${TENDERLOIN_BOUNDS.west} AND longitude<${TENDERLOIN_BOUNDS.east}`;
```

#### Financial District (Empty after 7pm)
```javascript
// Use business hours data
const FINANCIAL_DISTRICT_BOUNDS = {
  north: 37.7982,
  south: 37.7905,
  east: -122.3950,
  west: -122.4059
};
```

#### Castro/Mission (Nightlife)
- Use EventBrite API for nightlife events
- Cross-reference with crime data for time patterns

#### Golden Gate Park (Isolated Areas)
```javascript
const GG_PARK_BOUNDS = {
  north: 37.7736,
  south: 37.7661,
  east: -122.4534,
  west: -122.5116
};
```

### 8. 311 Report Integration
```javascript
// 311 Service Request API
const SF_311_API = {
  BASE_URL: "https://data.sfgov.org/resource/vw6y-z8j6.json",
  
  // Relevant service types for safety
  SAFETY_CATEGORIES: [
    "Streetlight",
    "Street Defects", 
    "Sidewalk or Curb",
    "Encampment",
    "Graffiti",
    "Blocked Street or SideWalk"
  ]
};

// Example: Get all safety-related 311 reports
async function get311SafetyReports(lat, lng, radius = 500) {
  const query = `${SF_311_API.BASE_URL}?$where=within_circle(location, ${lat}, ${lng}, ${radius})`;
  return fetch(query);
}
```

## Environment Variables Setup

Create a `.env` file in your project root:

```bash
# SF Open Data (no key needed but set URLs)
REACT_APP_SF_CRIME_API=https://data.sfgov.org/resource/wg3w-h783.json
REACT_APP_SF_311_API=https://data.sfgov.org/resource/vw6y-z8j6.json
REACT_APP_SF_PERMITS_API=https://data.sfgov.org/resource/i98e-djp9.json

# INRIX (get from hackathon)
REACT_APP_INRIX_APP_ID=pending_hackathon
REACT_APP_INRIX_APP_KEY=pending_hackathon

# Transit APIs
REACT_APP_BART_API_KEY=MW9S-E7SL-26DU-VV8V  # Example public key
REACT_APP_511_API_KEY=your_511_key_here

# Optional APIs
REACT_APP_EVENTBRITE_TOKEN=your_eventbrite_token
REACT_APP_GOOGLE_MAPS_KEY=your_google_maps_key  # For business hours
```

## Data Collection Script

Create a script to collect all needed data:

```javascript
// src/services/dataCollector.js

class SafePathDataCollector {
  constructor() {
    this.baseUrls = {
      crime: process.env.REACT_APP_SF_CRIME_API,
      hazards: process.env.REACT_APP_SF_311_API,
      permits: process.env.REACT_APP_SF_PERMITS_API,
      bart: `http://api.bart.gov/api/stn.aspx?cmd=stns&key=${process.env.REACT_APP_BART_API_KEY}&json=y`,
      muni: 'http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=sf-muni'
    };
  }

  async collectAllData(bounds) {
    const data = await Promise.all([
      this.getCrimeData(bounds),
      this.get311Reports(bounds),
      this.getConstructionPermits(bounds),
      this.getTransitStops(),
      this.getStreetLights(bounds)
    ]);

    return {
      crimes: data[0],
      hazards: data[1],
      construction: data[2],
      transitStops: data[3],
      lighting: data[4]
    };
  }

  async getCrimeData(bounds) {
    const query = `${this.baseUrls.crime}?$where=latitude>${bounds.south} AND latitude<${bounds.north} AND longitude>${bounds.west} AND longitude<${bounds.east} AND incident_datetime>'2024-01-01'`;
    const response = await fetch(query);
    return response.json();
  }

  async get311Reports(bounds) {
    const query = `${this.baseUrls.hazards}?$where=within_circle(location, ${bounds.center.lat}, ${bounds.center.lng}, 1000)`;
    const response = await fetch(query);
    return response.json();
  }

  async getConstructionPermits(bounds) {
    const query = `${this.baseUrls.permits}?status=ACTIVE`;
    const response = await fetch(query);
    return response.json();
  }

  async getTransitStops() {
    const [bartStops, muniRoutes] = await Promise.all([
      fetch(this.baseUrls.bart).then(r => r.json()),
      fetch(this.baseUrls.muni).then(r => r.json())
    ]);
    return { bart: bartStops, muni: muniRoutes };
  }

  async getStreetLights(bounds) {
    const query = `${this.baseUrls.hazards}?service_subtype=Streetlight&status=Open`;
    const response = await fetch(query);
    return response.json();
  }
}

export default SafePathDataCollector;
```

## Quick Start Commands

```bash
# 1. Test SF Crime API
curl "https://data.sfgov.org/resource/wg3w-h783.json?\$limit=5" | json_pp

# 2. Test 311 API  
curl "https://data.sfgov.org/resource/vw6y-z8j6.json?\$limit=5" | json_pp

# 3. Get BART stations
curl "http://api.bart.gov/api/stn.aspx?cmd=stns&key=MW9S-E7SL-26DU-VV8V&json=y" | json_pp

# 4. Get Muni routes (no key needed)
curl "http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=sf-muni" | json_pp
```

## AWS Integration for Data Storage

```javascript
// Store collected data in AWS S3
const AWS = require('aws-sdk');
const s3 = new AWS.S3();

async function uploadToS3(data, filename) {
  const params = {
    Bucket: 'safepath-sf-data',
    Key: `raw-data/${filename}`,
    Body: JSON.stringify(data),
    ContentType: 'application/json'
  };
  
  return s3.upload(params).promise();
}
```

## Notes for Hackathon

1. **INRIX API**: Wait for hackathon to start to get credentials from https://github.com/SCUACM/inrix-access-25
2. **Rate Limits**: SF Open Data has generous limits (1000/hour), but implement caching
3. **Data Freshness**: Crime data updates daily, 311 updates hourly
4. **Free Tier**: All SF city data is free, BART/Muni APIs are free
5. **Backup Plan**: Download and cache data locally in case APIs fail during demo

## Priority Order for Implementation

1. **SF Crime Data** (Most important for safety)
2. **311 Hazards/Lighting** (Infrastructure safety)
3. **INRIX Real-time** (If available during hackathon)
4. **Transit Stops** (For safe havens)
5. **Construction/Events** (Route planning)
6. **Bridge/Traffic** (Nice to have)