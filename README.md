# SafePath SF - Real-Time Safety Navigation

🚨 **Live Demo**: [safepath-sf.vercel.app](https://safepath-sf.vercel.app)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation
```bash
npm install --legacy-peer-deps
```

### Development
```bash
# Start development server
npm start

# Build for production
npm run build
```

### 🌐 Deployment

#### Deploy to Vercel (Recommended)
1. Connect your GitHub repo to Vercel
2. Select the `James` branch
3. **Set Root Directory**: `frontend`
4. Build command: `npm run build` (auto-detected)
5. Output directory: `build` (auto-detected)
6. Add environment variables (see below)
7. Deploy!

#### Deploy to Netlify
1. Connect GitHub repo
2. Branch: `James`
3. **Base directory**: `frontend`
4. Build command: `npm run build`
5. Publish directory: `frontend/build`
6. Add environment variables

## 🛠️ Tech Stack
- **Frontend**: React + TypeScript
- **Styling**: Tailwind CSS + Radix UI
- **Maps**: Leaflet + OpenStreetMap
- **Routing**: GraphHopper API
- **Real-Time Data**: San Francisco Open Data APIs
  - 311 Service Requests (encampments, safety concerns)
  - SFPD Dispatch (crime reports)
- **Build Tool**: Create React App + Craco

## 📁 Project Structure
```
safepath-sf/
├── frontend/             # Main frontend application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── safe-path-app.tsx    # Main app component
│   │   │   ├── route-map.tsx        # Leaflet map integration
│   │   │   ├── location-input.tsx   # Address autocomplete
│   │   │   └── route-details.tsx    # Route information
│   │   ├── services/          # API integrations
│   │   │   ├── graphhopper.ts       # Routing service
│   │   │   ├── SafetyDataService.ts # SF Open Data APIs
│   │   │   └── savedLocations.ts    # Local storage
│   │   └── lib/              # Utilities
│   ├── public/           # Static assets
│   ├── vercel.json       # Vercel configuration
│   └── package.json      # Dependencies
├── src/                  # Legacy React app (deprecated)
└── README.md            # Documentation
```

## 🌟 Key Features

### Real-Time Safety Data
- **Live 311 Reports**: Encampments, aggressive behavior, safety concerns
- **SFPD Dispatch**: Real-time crime incidents and suspicious activity
- **Smart Caching**: 15-minute cache for optimal performance
- **Proximity Analysis**: Incidents within 250-500m of routes

### Intelligent Routing
- **Safety Score**: Dynamic calculation based on nearby incidents
- **Crime Score**: Specific to criminal activity
- **Social Score**: Encampments and aggressive behavior
- **Pedestrian Score**: Overall walkability
- **Route Alternatives**: Up to 3 routes with safety trade-offs

### Professional UI/UX
- Responsive design for all devices
- Interactive Leaflet maps
- Real-time route visualization
- Incident markers and waypoints
- Safety score badges

## 📝 Environment Variables
Create a `.env` file:
```bash
# Required - Get free key at graphhopper.com
REACT_APP_GRAPHHOPPER_API_KEY=your_key_here

# Optional - Enhances SF data rate limits
REACT_APP_DATASF_API_KEY=your_key_here

# Optional - Additional map features
REACT_APP_GOOGLE_MAPS_KEY=your_key_here
```

## 🔌 API Integrations

### San Francisco Open Data
The app integrates with official SF government APIs for real-time safety data:

#### 311 Service Requests
- **Endpoint**: `https://data.sfgov.org/resource/vw6y-z8j6.json`
- **Data**: Encampments, aggressive/threatening behavior
- **Update Frequency**: Real-time
- **Time Range**: Last 30 days

#### SFPD Dispatch
- **Endpoint**: `https://data.sfgov.org/resource/nwbb-fxkq.json`  
- **Data**: Crime reports, suspicious activity
- **Incident Types**: Robbery, assault, burglary, threats, etc.
- **Update Frequency**: Real-time

### GraphHopper Routing
- **Geocoding**: Convert addresses to coordinates
- **Routing**: Calculate walking paths with alternatives
- **Free Tier**: 500 requests/day
- **Sign up**: [graphhopper.com](https://graphhopper.com)

### Safety Scoring Algorithm
Scores are calculated dynamically based on:
- **Incident Proximity**: 250-500m radius analysis
- **Severity Weighting**:
  - High severity: -15 points
  - Medium severity: -8 points  
  - Low severity: -3 points
- **Base Score**: 100 points (maximum safety)

## 🚨 Troubleshooting

### File watching issues on macOS
```bash
brew install watchman
watchman watch-del-all
```

### Clear cache
```bash
npx expo start --clear
```

## 📚 Documentation
- [Route Calculation Mathematics](./ROUTE_MATHEMATICS.md) - Deep dive into the algorithms and formulas

## 📄 License
MIT

---
Built for AWS Hackathon 2025 🏆
