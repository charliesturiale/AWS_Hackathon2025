# DataSF Export Guide for SafePath
## Priority Datasets for Real-Time Route Safety Calculation

### 🚨 TIER 1: CRITICAL (Must Have)
These directly affect pedestrian safety decisions

#### 1. **Police Department Incident Reports** ⭐⭐⭐⭐⭐
- **Dataset**: `Police Department Incident Reports: 2018 to Present`
- **ID**: `wg3w-h783`
- **Size**: ~500MB
- **Update Frequency**: Daily
- **Key Fields**: incident_datetime, incident_category, latitude, longitude
- **Filter**: Last 90 days only
```sql
WHERE incident_datetime > '2024-07-01' 
  AND incident_category IN ('Assault', 'Robbery', 'Theft Person', 
                            'Sex Offense', 'Kidnapping', 'Human Trafficking')
```
**Why Critical**: Direct threat to pedestrian safety

#### 2. **311 Cases** ⭐⭐⭐⭐⭐
- **Dataset**: `311 Cases`
- **ID**: `vw6y-z8j6`
- **Size**: ~1GB (filtered)
- **Update Frequency**: Hourly
- **Key Fields**: service_name, lat, long, status_description
- **Filter**: Open cases only, safety-related
```sql
WHERE status_description = 'Open'
  AND service_name IN ('Streetlight', 'Encampment', 'Blocked Street or SideWalk',
                       'Street Defects', 'Sidewalk or Curb')
  AND requested_datetime > '2024-09-01'
```
**Why Critical**: Real-time hazards and lighting issues

#### 3. **SFPD Calls for Service** ⭐⭐⭐⭐⭐
- **Dataset**: `Police Department Calls for Service`
- **ID**: `hz9m-tj6z`
- **Size**: ~2GB (filtered)
- **Update Frequency**: Real-time
- **Key Fields**: call_datetime, call_type, latitude, longitude
- **Filter**: Last 24 hours only
```sql
WHERE call_datetime > NOW() - INTERVAL '24 hours'
  AND priority IN ('A', 'B')  -- High priority calls only
```
**Why Critical**: Active incidents happening NOW

### 🟡 TIER 2: IMPORTANT (Should Have)
Significantly improve route safety accuracy

#### 4. **Street Light Inventory**
- **Dataset**: `Street Light Poles`
- **ID**: `7kiu-46fz`
- **Size**: ~50MB
- **Update Frequency**: Monthly
- **Key Fields**: pole_id, latitude, longitude, wattage, install_date
- **Filter**: All active lights
**Why Important**: Calculate lighting quality along routes

#### 5. **Traffic Crashes**
- **Dataset**: `Traffic Crash Data from SWITRS`
- **ID**: `ubvf-ztfx`
- **Size**: ~200MB
- **Update Frequency**: Quarterly
- **Key Fields**: collision_date, latitude, longitude, pedestrian_involved
- **Filter**: Last 2 years, pedestrian-involved only
```sql
WHERE collision_date > '2022-10-01'
  AND pedestrian_involved = TRUE
```
**Why Important**: Historical danger zones

#### 6. **Registered Business Locations**
- **Dataset**: `Registered Business Locations - San Francisco`
- **ID**: `g8m3-pdis`
- **Size**: ~100MB
- **Update Frequency**: Weekly
- **Key Fields**: business_name, latitude, longitude, business_hours
- **Filter**: Active businesses only
```sql
WHERE business_end_date IS NULL
  AND location_end_date IS NULL
```
**Why Important**: Indicates foot traffic and "eyes on street"

#### 7. **SFMTA Parking Meters**
- **Dataset**: `SFMTA Parking Meter Operating Schedules`
- **ID**: `6cqg-dxku`
- **Size**: ~20MB
- **Update Frequency**: Weekly
- **Key Fields**: street_name, latitude, longitude, operating_hours
**Why Important**: Indicates active commercial areas

### 🟢 TIER 3: NICE TO HAVE
Enhance user experience but not critical

#### 8. **Public Works Permits**
- **Dataset**: `DPW Street Spatial Reference`
- **ID**: `i98e-djp9`
- **Size**: ~100MB
- **Update Frequency**: Daily
- **Filter**: Active permits only
```sql
WHERE permit_status = 'ACTIVE'
  AND permit_type IN ('Excavation', 'Street Construction')
```

#### 9. **SF Events**
- **Dataset**: `Events & Temporary Street Closures`
- **ID**: `jxvy-6tgf`
- **Size**: ~10MB
- **Update Frequency**: Daily
- **Filter**: Next 7 days only

#### 10. **Tree Inventory**
- **Dataset**: `Street Tree List`
- **ID**: `tkzw-k3nq`
- **Size**: ~50MB
- **Filter**: Trees > 20ft (provide shade/concealment)

### 📦 DATA EXPORT STRATEGY

#### Optimal Export Configuration:
```javascript
const EXPORT_CONFIG = {
  // TIER 1 - Real-time/Near real-time
  crime: {
    updateFrequency: '1 hour',
    retention: '90 days',
    format: 'JSON',
    compression: 'gzip',
    size: '~50MB compressed'
  },
  
  hazards311: {
    updateFrequency: '15 minutes',
    retention: '30 days',
    format: 'JSON',
    compression: 'gzip',
    size: '~20MB compressed'
  },
  
  activeCalls: {
    updateFrequency: '5 minutes',
    retention: '24 hours',
    format: 'JSON',
    compression: 'none',  // Need quick access
    size: '~5MB'
  },
  
  // TIER 2 - Daily updates
  staticInfrastructure: {
    updateFrequency: '24 hours',
    retention: 'permanent',
    format: 'JSON',
    compression: 'gzip',
    size: '~100MB compressed'
  }
};
```

### 🔄 INCREMENTAL UPDATE STRATEGY

Instead of downloading 2M files, use incremental updates:

```javascript
// Daily Full Sync (3 AM PST)
async function dailySync() {
  await syncDataset('wg3w-h783', { 
    since: '90 days ago',
    fields: ['incident_id', 'incident_datetime', 'incident_category', 
             'latitude', 'longitude']
  });
  
  await syncDataset('7kiu-46fz', { 
    full: true,  // Street lights don't change often
    fields: ['pole_id', 'latitude', 'longitude', 'wattage']
  });
}

// Hourly Updates (Critical Data)
async function hourlySync() {
  await syncDataset('wg3w-h783', { 
    since: '1 hour ago',
    fields: ['incident_id', 'incident_datetime', 'latitude', 'longitude']
  });
}

// Real-time Updates (Every 5 min)
async function realtimeSync() {
  await syncDataset('hz9m-tj6z', { 
    since: '5 minutes ago',
    priority: ['A', 'B'],
    fields: ['call_datetime', 'call_type', 'latitude', 'longitude']
  });
}
```

### 💾 STORAGE REQUIREMENTS

#### Estimated Storage Needs:
```
Initial Download:
- Tier 1 Data: ~200MB (compressed)
- Tier 2 Data: ~150MB (compressed)
- Tier 3 Data: ~50MB (compressed)
- TOTAL: ~400MB

Daily Updates:
- ~10-20MB/day

Monthly Total: ~1GB
```

### 🚀 QUICK START EXPORT COMMANDS

```bash
# 1. Export last 90 days of crime data
curl -X GET "https://data.sfgov.org/resource/wg3w-h783.json?\$where=incident_datetime>'2024-07-01'&\$limit=50000" \
  -o crime_data.json

# 2. Export open 311 hazards
curl -X GET "https://data.sfgov.org/resource/vw6y-z8j6.json?\$where=status_description='Open'&\$limit=10000" \
  -o hazards_311.json

# 3. Export street lights
curl -X GET "https://data.sfgov.org/resource/7kiu-46fz.json?\$limit=50000" \
  -o street_lights.json

# 4. Export active police calls (last 24h)
curl -X GET "https://data.sfgov.org/resource/hz9m-tj6z.json?\$where=call_datetime>'2024-10-24T00:00:00'&\$limit=5000" \
  -o active_calls.json
```

### 📈 PERFORMANCE OPTIMIZATION

#### Data Preprocessing:
```javascript
// Preprocess data into grid system for faster lookups
const GRID_SIZE = 100; // 100m x 100m grid

function preprocessData(rawData) {
  const grid = {};
  
  rawData.forEach(incident => {
    const gridKey = `${Math.floor(incident.lat * GRID_SIZE)}:${Math.floor(incident.lng * GRID_SIZE)}`;
    
    if (!grid[gridKey]) {
      grid[gridKey] = {
        crimes: [],
        hazards: [],
        lights: [],
        score: 100
      };
    }
    
    grid[gridKey].crimes.push(incident);
    grid[gridKey].score -= 5; // Adjust safety score
  });
  
  return grid;
}
```

### 🔐 API RATE LIMITS & BEST PRACTICES

```javascript
const RATE_LIMITS = {
  requestsPerHour: 1000,
  rowsPerRequest: 50000,
  maxConcurrent: 4
};

// Use batching and caching
async function fetchWithCache(dataset, query) {
  const cacheKey = `${dataset}:${JSON.stringify(query)}`;
  const cached = await cache.get(cacheKey);
  
  if (cached && cached.timestamp > Date.now() - 3600000) {
    return cached.data;
  }
  
  const data = await fetchFromDataSF(dataset, query);
  await cache.set(cacheKey, { data, timestamp: Date.now() });
  
  return data;
}
```

### ⚡ CRITICAL FIELDS ONLY

To minimize data size, only export essential fields:

```javascript
const ESSENTIAL_FIELDS = {
  crime: [
    'incident_id',
    'incident_datetime',
    'incident_category',
    'latitude',
    'longitude'
  ],
  
  hazards: [
    'service_request_id',
    'requested_datetime',
    'status_description',
    'service_name',
    'lat',
    'long'
  ],
  
  calls: [
    'cad_number',
    'call_datetime',
    'call_type',
    'priority',
    'latitude',
    'longitude'
  ],
  
  lights: [
    'pole_id',
    'latitude',
    'longitude',
    'wattage'
  ]
};
```

### 📊 FINAL RECOMMENDATION

**For Your Hackathon MVP, Focus On:**

1. **Crime Data** (last 30 days) - 50MB
2. **Open 311 Hazards** - 20MB  
3. **Street Lights** (full dataset) - 50MB
4. **Active Police Calls** (last 24h) - 5MB

**Total: ~125MB** - Manageable for demo

**Skip for MVP:**
- Historical data > 90 days
- Non-safety related datasets
- Redundant datasets

This focused approach gives you real-time safety data without overwhelming your system with 2M files.