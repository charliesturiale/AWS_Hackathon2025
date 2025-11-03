# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SafePath is a full-stack route safety analysis application for San Francisco that:
- Analyzes walking routes against real-time crime and 311 incident data
- Generates 3 route variations using GraphHopper API
- Uses offline optimization with in-memory waypoint injection (no additional API calls)
- Applies time-decay algorithms to weigh recent incidents more heavily
- Uses distance-based detection (200m safety buffer) for route optimization
- Merges nearby encampments for accurate risk assessment
- Provides real-time data updates every 10 minutes
- Processes routes in 3-15 seconds with 99.95% fewer API calls than previous implementation

**Tech Stack:**
- **Backend:** FastAPI (Python 3.9+) with uvicorn
- **Frontend:** React 18 + TypeScript + Tailwind CSS + shadcn/ui
- **APIs:** DataSF (crime/311 data), GraphHopper (routing)
- **Libraries:** geopy, numpy, pandas, react-leaflet

## Development Commands

### Backend Development

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server (from backend/app directory)
cd app
uvicorn main:app --reload --port 8000

# Run with production server
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000
```

**Backend runs on:** `http://localhost:8000`

### Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Run development server
npm start
# or
pnpm start

# Build for production
npm run build

# Run linter
npm run lint

# Run tests
npm test
```

**Frontend runs on:** `http://localhost:3000`

### Quick Start Scripts

```bash
# Windows batch files for convenience:
START_HERE.bat        # Interactive menu
start-backend.bat     # Start backend only
start-frontend.bat    # Start frontend only
test-backend.bat      # Test backend health
```

### Testing

```bash
# Test backend health
curl http://localhost:8000/api/health

# Test route calculation
curl -X POST http://localhost:8000/api/routes \
  -H "Content-Type: application/json" \
  -d '{"origin":"Union Square, SF","destination":"Ferry Building, SF"}'

# Get incident statistics
curl http://localhost:8000/api/data/stats
```

## Architecture

### Backend Architecture

**Main Application** (`backend/app/main.py`):
- FastAPI application with lifespan management
- Background scheduler (APScheduler) for periodic data fetching (every 10 min)
- CORS middleware for frontend communication
- GraphHopper integration for geocoding and routing

**Data Fetcher** (`backend/app/data_fetcher.py`):
- Fetches crime data from DataSF Police Dispatch API
- Fetches 311 incident data (encampments, aggressive/threatening behavior)
- Implements caching system in `backend/cache/` directory
- Filters for specific crime types and incident categories
- Automatic fallback to cached data on API failure

**Risk Scorer** (`backend/app/risk_scorer.py`):
- Implements sophisticated time-decay algorithm
- Risk weights: High (w=3, 72h decay), Medium (w=2, 24h decay), Low (w=1, 24h decay)
- Encampment merging within 0.001° threshold
- Distance-based risk weighting using exponential decay
- Filters closed encampments before analysis
- Binary tree recursion for identifying problematic segments (max depth: 5)
- Distance-based safety detection: 200m buffer from incidents

**Key Algorithms:**

*Risk Scoring:*
```
For high-risk (w=3): f(d,t,w) = (ReLU(3-3t/72))² × e^(-d²/0.02)
For med/low-risk: f(d,t,w) = (ReLU(w-wt/24))² × e^(-d²/0.02)
For encampments: No time decay, constant risk until closed
```

*Route Optimization (Offline):*
```
1. Recursively subdivide route to find segments within 200m of incidents
2. Calculate safe waypoint using perpendicular displacement (250m from threat)
3. Search for existing route points within 300m radius as anchors
4. Inject waypoint using anchor (maintains road validity) or interpolation
5. Validate using geodesic distance (no API calls)
```

### Frontend Architecture

**Main Component** (`frontend/src/components/safe-path-app.tsx`):
- Route input with location autocomplete
- Real-time route calculation with loading states
- Route selection UI with safety scores
- Error handling and API key validation

**Map Component** (`frontend/src/components/route-map.tsx`):
- React Leaflet for interactive map display
- Multiple route visualization with color coding
- Marker placement for origin/destination
- Route details overlay

**Services:**
- `graphhopper.ts`: Backend API client for route calculation
- `savedLocations.ts`: LocalStorage management for recent locations

**UI Components** (`frontend/src/components/ui/`):
- shadcn/ui component library
- Radix UI primitives for accessibility
- Tailwind CSS for styling

### Data Flow

1. **User Input** → Frontend captures origin/destination
2. **Geocoding** → Backend converts addresses to coordinates via GraphHopper (2 API calls)
3. **Route Generation** → Backend requests 3 route variations from GraphHopper (3-8 API calls depending on alternatives available)
4. **Data Retrieval** → Backend loads cached/fresh crime and 311 data
5. **Risk Analysis** → For each route:
   - Calculate minimum distance from each incident to route path
   - Apply time-decay formula based on incident age
   - Sum risk contributions across all incidents
6. **Offline Optimization** → For each route (1 iteration, max depth 5):
   - Recursively identify segments within 200m of incidents
   - Calculate safe waypoints using perpendicular displacement
   - Inject waypoints using existing route anchors (no API calls)
   - Validate safety using geodesic distance calculations
7. **Route Selection** → Sort by total risk, select safest routes for display
8. **Response** → Return analyzed routes with safety scores (0-100) and descriptions
9. **Visualization** → Frontend displays routes on interactive map

### Background Data Refresh

The backend uses APScheduler to automatically fetch fresh data every 10 minutes:
- Scheduler starts on application startup (lifespan manager)
- Fetches both crime and 311 data in sequence
- Saves to cache directory for fallback
- Logs fetch status and incident counts

## Environment Configuration

### Backend Environment Variables (`.env` in root)

```env
# DataSF API Configuration
DATASF_API_TOKEN=your_token_here
DATASF_CRIME_API=https://data.sfgov.org/resource/gnap-fj3t.json
DATASF_311_API=https://data.sfgov.org/resource/vw6y-z8j6.json

# GraphHopper API
GRAPHHOPPER_API_KEY=your_key_here

# Server Configuration
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000

# Data refresh interval (minutes)
DATA_REFRESH_INTERVAL=10
```

### Frontend Environment Variables (`.env` in frontend/)

```env
REACT_APP_GRAPHHOPPER_API_KEY=your_key_here
REACT_APP_BACKEND_URL=http://localhost:8000
```

## API Endpoints

### `GET /`
Health check with service status and last data fetch time

### `GET /api/health`
Detailed health check with incident counts

### `POST /api/routes`
Calculate and analyze routes

**Request:**
```json
{
  "origin": "Union Square, San Francisco",
  "destination": "Ferry Building, San Francisco"
}
```

**Response:**
```json
{
  "routes": [
    {
      "id": 1,
      "name": "Safest Route",
      "distance": "1.2 mi",
      "time": "24 min",
      "safetyScore": 95,
      "total_risk": 2.34,
      "crime_risk": 1.12,
      "incident_risk": 1.22,
      "coordinates": [...],
      "color": "#10b981"
    }
  ],
  "originCoords": {"lat": 37.7879, "lng": -122.4075},
  "destCoords": {"lat": 37.7955, "lng": -122.3937},
  "data_timestamp": "2025-10-26T12:00:00"
}
```

### `GET /api/data/stats`
Current incident statistics

### `GET /api/incidents`
All incidents formatted for map markers (with mock data fallback)

## Important Implementation Details

### Risk Weight Assignment

The system categorizes incidents into three risk levels:

**High Risk (w=3, 72-hour decay):**
- Explosive Found, Explosion
- Robbery, Strongarm Robbery
- Assault, Battery

**Medium Risk (w=2, 24-hour decay):**
- Purse Snatch, Indecent Exposure
- Fight with/without Weapons
- Person Breaking In, Burglary

**Low Risk (w=1, 24-hour decay):**
- Suspicious Person
- Threats/Harassment
- Aggressive/Threatening Behavior

**Encampments:**
- No time decay for open encampments
- Automatically filtered if status is "Closed"
- Merged if within 0.001° (approximately 111 meters)

### Route Generation Strategy

GraphHopper typically returns 3-5 alternative routes. To generate 10 variations, the backend uses:
1. Alternative routes algorithm (primary strategy)
2. Different routing profiles (fastest route)
3. Slight variations of existing routes (±5% distance/time)

### Safety Score Calculation

Safety scores (0-100) are derived from total risk using exponential decay:
```python
safety_score = int(100 * exp(-total_risk / 10))
safety_score = max(0, min(100, safety_score))  # Clamp to 0-100
```

Lower risk → Higher safety score

### Caching System

- Cache directory: `backend/cache/`
- Files: `crime_data.json`, `311_data.json`
- Automatic fallback on API failure
- JSON format with 2-space indentation
- Updated every 10 minutes via background scheduler

## Common Issues

### Backend won't start
- Verify Python version: `python --version` (should be 3.9+)
- Check virtual environment is activated (look for `(venv)` in terminal)
- Reinstall dependencies: `pip install -r requirements.txt`
- Check port 8000 availability: `netstat -an | grep 8000` (Unix) or `netstat -an | findstr :8000` (Windows)

### Frontend can't connect to backend
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check CORS settings in `backend/app/main.py`
- Verify environment variables in both `.env` files

### No routes returned
- Validate GraphHopper API key
- Ensure addresses are in San Francisco
- Check backend logs for GraphHopper API errors

### Data not updating
- Verify DataSF API token is valid
- Check background scheduler is running (look for scheduled data fetch logs)
- Review cache directory for recent updates

## Notes for Development

- The frontend uses CRACO for custom webpack configuration
- TypeScript strict mode is enabled
- The map component requires Leaflet CSS to be properly imported
- Mock incident data is provided as fallback when APIs are unavailable
- All coordinates use (lat, lng) format internally
- GraphHopper API returns coordinates as [lng, lat] and must be reversed
- Time calculations assume ISO 8601 format timestamps
