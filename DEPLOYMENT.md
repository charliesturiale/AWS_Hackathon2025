# SafePath Deployment Guide

## Architecture Overview

SafePath is a full-stack application with two main components:

```
Frontend (React + TypeScript)  <---> Backend (FastAPI + Python)
    Port 3000                           Port 8000
         |                                  |
         |                                  |
         v                                  v
    User Interface              GraphHopper API (routing)
    - Route input               DataSF Crime API
    - Map display               DataSF 311 API
    - Safety visualization      Risk calculation engine
```

### Technology Stack

**Backend:**
- FastAPI (Python async web framework)
- Uvicorn (ASGI server)
- APScheduler (background data refresh)
- NumPy, geopy (risk calculations)

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS + shadcn/ui
- React Leaflet (interactive maps)
- Axios (API client)

### Data Flow

1. User enters origin and destination addresses
2. Frontend sends POST request to `/api/routes`
3. Backend geocodes addresses via GraphHopper API
4. Backend generates 3 route variations from GraphHopper
5. Backend applies offline optimization with binary tree recursion
6. Backend analyzes each route against incident data
7. Backend calculates risk scores using time-decay algorithm
8. Backend returns top 3 safest routes
9. Frontend displays routes on interactive map

### Rate Limiting

Backend implements comprehensive rate limiting:
- 3-second minimum wait between geocoding requests
- Exponential backoff on 429 errors (10s, 30s, 60s, 120s, 240s)
- Caching of geocoded addresses
- Semaphore-based concurrent request limiting (max 2)
- Up to 5 retries with automatic fallback

## Local Deployment (Windows)

### Prerequisites

- Windows 10/11
- Python 3.9 or later
- Node.js 16 or later
- Internet connection

### Step 1: Get API Keys

**DataSF API Token (FREE):**
1. Go to https://data.sfgov.org/
2. Click "Sign Up" and create account
3. Go to your profile settings
4. Copy your "App Token"

**GraphHopper API Key (FREE tier):**
1. Go to https://www.graphhopper.com/
2. Click "Get started for free"
3. Create account
4. Copy API key from dashboard
5. Note: Free tier has ~5 requests/minute limit

### Step 2: Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/safepath.git
cd safepath

# Run automated setup
SETUP.bat
```

The setup script will:
1. Check for Python and Node.js
2. Create Python virtual environment
3. Install backend dependencies
4. Install frontend dependencies
5. Guide you through .env configuration

### Step 3: Run Application

```bash
# Launch both servers
START_HERE.bat
```

This opens two windows:
- Backend server (http://localhost:8000)
- Frontend app (http://localhost:3000)

Browser automatically opens to http://localhost:3000

### Step 4: Test

Try these San Francisco addresses:
- "Union Square, SF" to "Ferry Building, SF"
- "Golden Gate Park" to "Fisherman's Wharf"
- "Mission District" to "Castro District"

## Cloud Deployment

### Option 1: Heroku (Easiest)

**Backend:**
```bash
# Install Heroku CLI
# Create Procfile
echo "web: cd backend/app && uvicorn main:app --host=0.0.0.0 --port=$PORT" > Procfile

# Deploy
heroku create safepath-backend
heroku config:set DATASF_API_TOKEN=your_token
heroku config:set GRAPHHOPPER_API_KEY=your_key
heroku config:set DATASF_CRIME_API=https://data.sfgov.org/resource/gnap-fj3t.json
heroku config:set DATASF_311_API=https://data.sfgov.org/resource/vw6y-z8j6.json
heroku config:set FRONTEND_URL=https://your-frontend.vercel.app
git push heroku main
```

**Frontend:**
```bash
cd frontend
# Update REACT_APP_BACKEND_URL in .env
vercel --prod
```

### Option 2: Railway.app

1. Connect GitHub repository
2. Create two services: backend and frontend
3. Add environment variables in Railway dashboard
4. Automatic deployment on git push

### Option 3: AWS/Azure/GCP

**Backend (EC2/VM instance):**
```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3.9 python3-pip

# Clone repo
git clone your-repo
cd safepath/backend

# Install dependencies
pip3 install -r requirements.txt

# Run with gunicorn
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker

# Setup systemd service for auto-restart
# Configure nginx reverse proxy
# Setup SSL with Let's Encrypt
```

**Frontend (Static hosting):**
```bash
cd frontend
npm run build
# Deploy build/ folder to:
# - AWS S3 + CloudFront
# - Azure Static Web Apps
# - Google Cloud Storage
```

## Production Configuration

### Backend .env (Production)

```env
DATASF_API_TOKEN=your_production_token
GRAPHHOPPER_API_KEY=your_production_key
DATASF_CRIME_API=https://data.sfgov.org/resource/gnap-fj3t.json
DATASF_311_API=https://data.sfgov.org/resource/vw6y-z8j6.json
BACKEND_PORT=8000
FRONTEND_URL=https://your-frontend-domain.com
DATA_REFRESH_INTERVAL=10
```

### Frontend .env (Production)

```env
REACT_APP_BACKEND_URL=https://your-backend-domain.com
REACT_APP_GRAPHHOPPER_API_KEY=your_key
```

### CORS Configuration

Update `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
        "https://www.your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Or change port in .env
BACKEND_PORT=8001
```

**Module import errors:**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

**GraphHopper 429 errors:**
- Wait 60 seconds for rate limit reset
- Reduce concurrent requests
- Consider upgrading to paid plan ($99/month)

### Frontend Issues

**Port 3000 already in use:**
- Stop other React apps
- Or modify package.json to use different port

**API connection failed:**
- Verify backend is running (http://localhost:8000/api/health)
- Check REACT_APP_BACKEND_URL in frontend/.env
- Verify CORS settings in backend

**Build errors:**
```bash
cd frontend
rm -rf node_modules
npm install
npm run build
```

## Testing

### Quick Health Check
```bash
# Test backend
curl http://localhost:8000/api/health

# Should return:
# {"status":"healthy","data":{"crime_incidents":160,"311_incidents":50}}
```

### Comprehensive Test Suite
```bash
cd backend
python production_test_suite.py
```

Tests cover:
- API verification
- Data accuracy
- Route calculation
- Performance baselines
- Limited load testing (respects API limits)

### Manual Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts and loads
- [ ] Health endpoint returns 200
- [ ] Route calculation works
- [ ] Map displays routes correctly
- [ ] Safety scores are calculated
- [ ] Incident data is fresh (check timestamp)

## Monitoring

### Key Metrics to Track

1. **API Response Times:**
   - Health endpoint: <100ms
   - Stats endpoint: <500ms
   - Route calculation: 3-15 seconds (offline optimization)

2. **Error Rates:**
   - Target: <1% error rate
   - Monitor 429 rate limit errors

3. **Data Freshness:**
   - Crime/311 data updated every 10 minutes
   - Check `last_fetch` timestamp

4. **GraphHopper API Usage:**
   - 10 calls per route request (geocoding + route generation)
   - Free tier: ~5 requests/minute
   - Monitor daily quota

### Recommended Tools

- **Error Tracking:** Sentry
- **Uptime Monitoring:** UptimeRobot, Pingdom
- **Analytics:** Google Analytics, Plausible
- **Log Aggregation:** Papertrail, LogDNA

## Security Considerations

### API Keys
- Never commit .env to git
- Use environment variables in production
- Rotate keys regularly
- Use different keys for dev/prod

### CORS
- Restrict to specific frontend domains in production
- Don't use wildcard (*) in production

### Rate Limiting
- Backend implements rate limiting
- Consider adding request queuing for high traffic
- Monitor for abuse/DoS patterns

### Data Privacy
- No user data is stored
- All route calculations are ephemeral
- No tracking or analytics by default

## Performance Optimization

### Backend
- Geocoding results cached in memory
- 311 data cached locally (backend/cache/)
- Background data refresh (no request blocking)
- Async/await for concurrent operations

### Frontend
- Code splitting via React.lazy
- Map tiles cached by browser
- API response caching (future enhancement)
- Optimized bundle size (<500KB initial)

### Future Enhancements
- Redis for distributed caching
- WebSocket for real-time updates
- CDN for frontend assets
- Database for persistent caching

## Support and Resources

**Documentation:**
- README.md - Quick start guide
- CLAUDE.md - Development guide
- This file - Deployment guide

**Scripts:**
- SETUP.bat - First-time installation
- START_HERE.bat - Launch application
- test-backend.bat - Health check

**Testing:**
- production_test_suite.py - Comprehensive tests
- comprehensive_test.py - Basic API tests

**Need Help?**
- Check existing GitHub issues
- Review test suite output
- Verify API keys are valid
- Check API quotas haven't been exceeded
