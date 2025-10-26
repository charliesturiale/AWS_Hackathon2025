# SafePath SF - Integration Guide

## Overview
SafePath SF is a path risk analysis system that helps users find the safest walking routes in San Francisco by analyzing real-time crime and 311 data from SF Open Data.

## Architecture

### Backend API (Python Flask)
- **Location**: `/api/path_risk_analysis.py`
- **No AWS Dependencies**: Runs standalone without Lambda
- **Data Sources**: SF Open Data APIs (no API keys required!)
  - Crime Data: https://data.sfgov.org/resource/gnap-fj3t.json
  - 311 Data: https://data.sfgov.org/resource/vw6y-z8j6.json

### Frontend (React Native/Expo)
- **Component**: `/src/components/SafePathAnalysis.tsx`
- **Integration**: Calls backend API for risk analysis
- **Features**: Visual risk scoring, route ranking, real-time updates

## How It Works

### Risk Calculation Algorithm
Based on the Jupyter notebook analysis with time-decay formulas:
- **High-risk incidents (w=3)**: Decay over 72 hours
- **Low-risk incidents (w=1,2)**: Decay over 24 hours
- **Formula**: `f(d,t,w) = (ReLU(w-wt/decay))² × e^(-d²/0.02)`

### Risk Categories
- **High Risk (3)**: Explosives, Robbery, Assault
- **Medium Risk (2)**: Purse Snatch, Fights, Breaking In
- **Low Risk (1)**: Suspicious Person, Threats, Encampments

## Deployment

### Local Development

1. **Install API dependencies**:
```bash
cd api
pip install -r requirements.txt
```

2. **Run the Flask API**:
```bash
python path_risk_analysis.py
```
API will be available at http://localhost:5000

3. **Run the React Native app**:
```bash
npm install
npm start
```

### Production Deployment (Vercel)

1. **Deploy to Vercel**:
```bash
vercel --prod
```

2. **Environment Variables**:
Set in your Vercel dashboard:
```
REACT_APP_API_URL=https://your-vercel-app.vercel.app/api
```

## API Endpoints

### POST /analyze-paths
Analyze multiple paths and return risk scores
```json
{
  "paths": [
    [[37.7849, -122.4094], [37.7855, -122.4086]],
    [[37.7849, -122.4094], [37.7845, -122.4102]]
  ]
}
```

Response:
```json
{
  "success": true,
  "safest_paths": [...],
  "all_paths": [...],
  "timestamp": "2024-10-26T10:00:00"
}
```

### GET /crime-data
Get cached crime data (first 100 records)

### GET /311-data
Get cached 311 data (first 100 records)

### GET /health
Health check endpoint

## Integration with Existing Frontend

1. **Import the component**:
```tsx
import SafePathAnalysis from './src/components/SafePathAnalysis';
```

2. **Use in your app**:
```tsx
<SafePathAnalysis 
  paths={yourPathsArray}
  onPathSelect={(index) => handlePathSelection(index)}
/>
```

3. **Or use with sample paths**:
```tsx
<SafePathAnalysis />  // Will use built-in SF sample paths
```

## Features

- ✅ Real-time risk analysis using SF Open Data
- ✅ No API keys required (public data!)
- ✅ Time-decay algorithm for incident relevance
- ✅ Visual risk scoring and route ranking
- ✅ Mobile-optimized React Native components
- ✅ Caching to reduce API calls
- ✅ Standalone deployment (no AWS required)

## Next Steps

1. **Add Google Maps integration** for actual route generation
2. **Implement user preferences** (avoid hills, prefer lit streets)
3. **Add real-time notifications** for incidents along saved routes
4. **Create heat map visualization** of risk areas
5. **Add weather integration** (rain affects visibility/safety)

## Data Sources

- **SF Crime Data**: Updated hourly, includes police calls for service
- **SF 311 Data**: Updated daily, includes encampments and street issues
- **No API Keys Required**: All data is publicly available!

## Support

For issues or questions, please check:
- The Jupyter notebook documentation in `/docs/`
- The HTML report: `SafePath_SF_Report.html`
- SF Open Data documentation: https://datasf.org/opendata/