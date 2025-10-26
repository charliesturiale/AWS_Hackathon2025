# DataSF Implementation Guide for SafePath

## ✅ What to Use from DataSF's 2M Files

### For Your MVP (Hackathon), Use ONLY:

| Dataset | Size | Update Rate | Why Essential |
|---------|------|-------------|---------------|
| **Crime Reports** | ~50MB | Hourly | Recent crimes = immediate danger |
| **311 Hazards** | ~20MB | 15 min | Broken lights, blocked sidewalks |
| **Street Lights** | ~50MB | Daily | Darkness = danger |
| **Police Calls** | ~5MB | 5 min | Active incidents NOW |
| **TOTAL** | **~125MB** | - | Manageable for demo |

### Skip These 1.9M+ Other Files:
- ❌ Historical data > 90 days old
- ❌ Parking meter data
- ❌ Budget reports
- ❌ Employee salaries  
- ❌ Building permits (except active construction)
- ❌ Census data
- ❌ Restaurant inspections
- ❌ Library usage
- ❌ Recreation program enrollment
- ❌ Everything else not safety-related

## 🎯 Implementation Strategy

### 1. Real-Time Data (Update every 5 min)
```javascript
// ONLY fetch active police calls
const REALTIME_ENDPOINT = 'https://data.sfgov.org/resource/hz9m-tj6z.json';
const REALTIME_QUERY = {
  where: "call_datetime > NOW() - INTERVAL '30 minutes'",
  limit: 100,
  fields: ['call_type', 'latitude', 'longitude', 'priority']
};
```

### 2. Near Real-Time (Update every hour)
```javascript
// Recent crimes only
const CRIME_ENDPOINT = 'https://data.sfgov.org/resource/wg3w-h783.json';
const CRIME_QUERY = {
  where: "incident_datetime > '30 days ago'",
  limit: 5000,
  fields: ['incident_category', 'latitude', 'longitude', 'incident_datetime']
};
```

### 3. Daily Cache (Update once per day)
```javascript
// Infrastructure that rarely changes
const STATIC_DATA = {
  streetLights: 'Download once, cache for 24h',
  businessHours: 'Download once, cache for 7 days',
  transitStops: 'Download once, cache forever'
};
```

## 📱 For Your App's Logistic Regression

### Input Features from DataSF:
```javascript
const routeFeatures = {
  // From Crime Data (wg3w-h783)
  crimeCount24h: 8,        // Count incidents in last 24h within 200m
  violentCrimeCount: 3,    // Filter for assault, robbery
  
  // From 311 Data (vw6y-z8j6)  
  brokenLights: 2,         // Count of streetlight issues
  hazardReports: 5,        // Encampments, blocked sidewalks
  
  // From Street Infrastructure
  lightDensity: 0.7,       // Lights per 100m of route
  
  // Calculated
  timeOfDay: 22,           // 10 PM
  dayOfWeek: 5,            // Friday
};
```

### Output:
```javascript
const safetyScore = logisticRegression(routeFeatures);
// Returns: 0.73 (73% safe)
```

## 🚀 Quick Implementation

### Step 1: Download Essential Data (5 min)
```bash
# Run the download script
./scripts/download-datasf.sh
```

### Step 2: Process for App (10 min)
```javascript
// Load and preprocess
const crimeData = require('./data/datasf/crime_data.json');
const hazards = require('./data/datasf/hazards_311.json');

// Create safety grid
const safetyGrid = createSafetyGrid(crimeData, hazards);
```

### Step 3: Calculate Routes (Runtime)
```javascript
function calculateSafeRoute(start, end) {
  // Get relevant grid squares
  const routeGrids = getRouteGrids(start, end);
  
  // Calculate safety score
  const safetyScore = routeGrids.reduce((score, grid) => {
    return score * grid.safetyScore;
  }, 1.0);
  
  return {
    path: routeCoordinates,
    safetyScore: safetyScore,
    warnings: getWarnings(routeGrids)
  };
}
```

## 💡 Pro Tips

### DO:
- ✅ Cache aggressively (data doesn't change that fast)
- ✅ Pre-calculate safety scores for common routes
- ✅ Use bounding boxes to limit data queries
- ✅ Have offline fallback data for demo

### DON'T:
- ❌ Try to download all 2M files
- ❌ Make API calls during route calculation
- ❌ Store historical data > 90 days
- ❌ Use non-safety related datasets

## 📊 Data Size Reality Check

```
What DataSF Has: 2,000,000+ files (100+ GB)
What You Need:   4 datasets (125 MB)
Percentage:      0.006% of available data
```

## 🎯 Focus = Success

Your app needs to know:
1. Where crimes happened recently
2. Where lights are broken
3. Where active police calls are
4. Where hazards exist

That's it. Everything else is noise for your use case.

## AWS Integration

Once data is downloaded:
```bash
# Upload to S3
aws s3 sync ./data/datasf s3://safepath-sf-data/datasf/

# Set up Lambda to refresh hourly
aws events put-rule --name refresh-crime-data \
  --schedule-expression "rate(1 hour)"
```

## Final Architecture

```
DataSF (2M files)
    ↓
Filter to 4 datasets (125MB)
    ↓
Download hourly
    ↓
Process into grid system
    ↓
Cache in DynamoDB
    ↓
Serve to app via API Gateway
    ↓
Calculate safe routes in real-time
```

Remember: **Less is more**. A working app with 4 datasets beats a broken app trying to process 2 million files.