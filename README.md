# SafePath - Intelligent Route Safety Analysis

**Find the safest walking paths in San Francisco using real-time crime and incident data**

SafePath analyzes walking routes against real-time San Francisco crime statistics and 311 incident reports to recommend the safest paths to your destination.

![SafePath Demo](https://img.shields.io/badge/Status-Active-success) ![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue) ![Node 16+](https://img.shields.io/badge/Node-16%2B-green)

---

## 🚀 Quick Start (3 Steps)

### 1. Clone Repository
```bash
git clone https://github.com/charliesturiale/AWS_Hackathon2025.git
cd AWS_Hackathon2025
```

### 2. Run Setup (First Time Only)
```bash
SETUP.bat
```
This will:
- Check for Python 3.9+ and Node.js 16+
- Install all dependencies automatically
- Guide you through API key configuration

### 3. Launch Application
```bash
START_HERE.bat
```
- Opens backend (http://localhost:8000)
- Opens frontend (http://localhost:3000)
- Browser opens automatically!

**That's it!** 🎉

---

## 📋 Prerequisites

### Software (Auto-Checked by SETUP.bat)
- **Python 3.9+** - [Download here](https://www.python.org/downloads/)
  - ⚠️ During installation, CHECK "Add Python to PATH"
- **Node.js 16+** - [Download here](https://nodejs.org/)
  - Use LTS version (default settings are fine)

### API Keys (FREE)

#### DataSF API Token (Required)
1. Go to [data.sfgov.org](https://data.sfgov.org/)
2. Click **"Sign Up"** (free account)
3. Go to Profile → Copy **"App Token"**

#### GraphHopper API Key (Required)
1. Go to [graphhopper.com](https://www.graphhopper.com/)
2. Click **"Get started for free"**
3. Copy API key from dashboard
4. **Note:** Free tier = ~5 requests/minute (perfect for testing)

---

## 🎯 Features

- **Real-Time Data**: Crime & 311 incidents updated every 10 minutes
- **Smart Routing**: Generates 3 optimized route variations
- **Offline Optimization**: Fast safety improvements (no extra API calls)
- **Time-Decay Algorithm**: Recent incidents weighted more heavily
- **Distance-Based Detection**: 200m safety buffer for incidents
- **Interactive Map**: Visual routes with safety scores
- **Mobile Responsive**: Works on all devices

---

## 🧪 Try It Out

Test these San Francisco routes:
- **Short**: "Union Square, SF" → "Ferry Building, SF"
- **Long**: "Golden Gate Park" → "Fisherman's Wharf"
- **Neighborhood**: "Mission District" → "Castro District"

---

## 📖 Manual Setup (Mac/Linux or Advanced Users)

<details>
<summary>Click to expand manual installation steps</summary>

### 1. Clone Repository
```bash
git clone https://github.com/charliesturiale/AWS_Hackathon2025.git
cd AWS_Hackathon2025
```

### 2. Create `.env` File
Create a file named `.env` in the project root with:
```env
# DataSF API Configuration
DATASF_API_TOKEN=your_datasf_token_here
DATASF_CRIME_API=https://data.sfgov.org/resource/gnap-fj3t.json
DATASF_311_API=https://data.sfgov.org/resource/vw6y-z8j6.json

# GraphHopper API Configuration
GRAPHHOPPER_API_KEY=your_graphhopper_key_here

# Server Configuration
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
DATA_REFRESH_INTERVAL=10
```

### 3. Setup Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 4. Setup Frontend
```bash
cd frontend
npm install
```

### 5. Run Backend (Terminal 1)
```bash
cd backend/app
source ../venv/bin/activate  # Mac/Linux
python -m uvicorn main:app --reload --port 8000
```

### 6. Run Frontend (Terminal 2)
```bash
cd frontend
npm start
```

### 7. Open Browser
Navigate to http://localhost:3000

</details>

---

## 🔧 Troubleshooting

### ❌ "Python not found"
**Solution:** Install Python 3.9+ and make sure to **check "Add to PATH"** during installation.

### ❌ "Node not found"
**Solution:** Install Node.js 16+ from [nodejs.org](https://nodejs.org/)

### ❌ "Port 8000 already in use"
**Solution (Windows):**
```bash
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

### ❌ "Port 3000 already in use"
**Solution:** Stop other React apps or close terminals running on port 3000.

### ❌ GraphHopper "429 Too Many Requests"
**Solution:**
- Wait 60 seconds (rate limit resets)
- Free tier = ~5 requests/minute
- Consider upgrading for production

### ❌ Frontend can't connect to backend
**Checklist:**
1. Is backend running? Test: `curl http://localhost:8000/api/health`
2. Check CORS settings in `backend/app/main.py`
3. Verify `.env` file exists in project root

### ❌ Module import errors
**Solution:**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📡 API Endpoints

### Health Check
```http
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "data": {
    "crime_incidents": 160,
    "311_incidents": 50,
    "last_fetch": "2025-10-29T20:08:09.061345"
  }
}
```

### Calculate Routes
```http
POST /api/routes
Content-Type: application/json

{
  "origin": "Union Square, San Francisco",
  "destination": "Pier 39, San Francisco"
}
```

**Response:**
```json
{
  "routes": [
    {
      "id": 1,
      "name": "Safest Route",
      "description": "Safest path with minimal risk exposure",
      "distance": "2.5 mi",
      "time": "52 min",
      "safetyScore": 85,
      "total_risk": 1.51,
      "coordinates": [{"lat": 37.7830, "lng": -122.4060}, ...],
      "color": "#10b981"
    }
  ],
  "originCoords": {"lat": 37.7829, "lng": -122.4060},
  "destCoords": {"lat": 37.8098, "lng": -122.4103}
}
```

### Get Statistics
```http
GET /api/data/stats
```

---

## 🧮 How It Works

### Risk Scoring Algorithm

**High-risk incidents (72-hour decay):**
```
risk = (max(0, 3-3t/72))² × exp(-d²/0.02)
```

**Medium/low-risk incidents (24-hour decay):**
```
risk = (max(0, w-wt/24))² × exp(-d²/0.02)
```

Where:
- `t` = hours since incident
- `d` = distance from route (km)
- `w` = risk weight (1=low, 2=medium, 3=high)

### Risk Categories

| Risk Level | Weight | Decay | Examples |
|------------|--------|-------|----------|
| **High** | 3 | 72hr | Robbery, Assault, Battery, Explosives |
| **Medium** | 2 | 24hr | Purse Snatch, Fights, Burglary |
| **Low** | 1 | 24hr | Suspicious Person, Threats, Harassment |
| **Encampments** | 2 | None | Open encampments (until closed) |

### Route Optimization Process

1. **Generate Routes**: Request 3 variations from GraphHopper
2. **Analyze Segments**: Find areas within 200m of incidents
3. **Calculate Waypoints**: Create safe alternatives (250m from threats)
4. **Offline Injection**: Add waypoints using existing route anchors
5. **Validate**: Verify improved safety with geodesic distance
6. **Rank**: Sort by safety score and return top 3

---

## 🏗️ Project Structure

```
AWS_Hackathon2025/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── data_fetcher.py      # DataSF integration
│   │   └── risk_scorer.py       # Risk calculation engine
│   ├── cache/                   # Cached incident data
│   ├── requirements.txt         # Python dependencies
│   └── production_test_suite.py # Test suite
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   └── services/            # API clients
│   ├── package.json             # Node dependencies
│   └── public/                  # Static assets
├── .env                         # API keys (DO NOT COMMIT)
├── .gitignore                   # Git ignore rules
├── SETUP.bat                    # First-time setup
├── START_HERE.bat               # Launch application
└── README.md                    # This file
```

---

## 🧪 Testing

### Quick Backend Test
```bash
curl http://localhost:8000/api/health
```

### Comprehensive Test Suite
```bash
cd backend
python production_test_suite.py
```

**Tests include:**
- API verification
- Route calculation accuracy
- Risk scoring validation
- Performance baselines
- Load testing (respects API limits)

---

## 🌐 Production Deployment

<details>
<summary>Click to expand production deployment guide</summary>

### Environment Variables

**Backend `.env` (Production):**
```env
DATASF_API_TOKEN=your_production_token
GRAPHHOPPER_API_KEY=your_production_key
DATASF_CRIME_API=https://data.sfgov.org/resource/gnap-fj3t.json
DATASF_311_API=https://data.sfgov.org/resource/vw6y-z8j6.json
BACKEND_PORT=8000
FRONTEND_URL=https://your-domain.com
DATA_REFRESH_INTERVAL=10
```

### CORS Configuration

Update `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Production Server

**Using Gunicorn (recommended):**
```bash
cd backend
gunicorn app.main:app \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --worker-class uvicorn.workers.UvicornWorker
```

### Frontend Build

```bash
cd frontend
npm run build
# Deploy build/ folder to static hosting (Vercel, Netlify, S3, etc.)
```

### Hosting Options

| Service | Backend | Frontend | Difficulty |
|---------|---------|----------|------------|
| **Heroku** | ✅ Free tier | ❌ | Easy |
| **Railway** | ✅ Free tier | ✅ Free tier | Easy |
| **Vercel** | ❌ | ✅ Free tier | Easy |
| **AWS** | EC2 | S3+CloudFront | Medium |
| **DigitalOcean** | Droplet | Spaces | Medium |

</details>

---

## 💻 Tech Stack

**Backend:**
- FastAPI (Python 3.9+)
- Uvicorn ASGI server
- APScheduler (background tasks)
- geopy, numpy, pandas

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS + shadcn/ui
- React Leaflet (maps)
- Axios

**APIs:**
- GraphHopper (routing/geocoding)
- DataSF Crime Data
- DataSF 311 Incidents

---

## 📝 Development

### Backend Development
```bash
cd backend/app
source ../venv/bin/activate  # Mac/Linux
uvicorn main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm start
```

### Code Style
- Backend: PEP 8 (Python)
- Frontend: ESLint + Prettier (TypeScript/React)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Crime data from [DataSF](https://datasf.org/)
- Routing powered by [GraphHopper](https://www.graphhopper.com/)
- Map tiles from [OpenStreetMap](https://www.openstreetmap.org/)

---

## 📞 Support

**Having issues?**
1. Check [Troubleshooting](#-troubleshooting) section above
2. Search [existing GitHub issues](https://github.com/charliesturiale/AWS_Hackathon2025/issues)
3. Open a new issue with:
   - Error message
   - Steps to reproduce
   - OS and Python/Node versions

---

## 🎉 Quick Command Reference

```bash
# First time setup
SETUP.bat

# Launch application
START_HERE.bat

# Individual backend
start-backend.bat

# Individual frontend
start-frontend.bat

# Test backend
curl http://localhost:8000/api/health

# Run tests
cd backend && python production_test_suite.py
```

---

**Made with ❤️ for safer walking in San Francisco**
