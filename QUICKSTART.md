# SafePath - Quick Start Guide

**Get up and running in 5 minutes!**

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Terminal/Command Prompt

## Step 1: Start the Backend (Terminal 1)

```bash
# Navigate to project
cd AWS_Hackathon2025

# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
cd app
uvicorn main:app --reload --port 8000
```

 **Backend should be running at:** `http://localhost:8000`

You should see:
```
=€ Starting SafePath Backend...
=Ê Fetching initial incident data...
=Þ Fetching crime data from DataSF...
 Fetched XXX crime incidents
=Þ Fetching 311 data from DataSF...
 Fetched XXX 311 incidents
ð Scheduled data updates every 10 minutes
 SafePath Backend ready!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Step 2: Start the Frontend (Terminal 2 - NEW WINDOW)

```bash
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install
# or if you have pnpm:
pnpm install

# Start the development server
npm start
# or:
pnpm start
```

 **Frontend should be running at:** `http://localhost:3000`

Browser should automatically open to the app!

## Step 3: Test the Application

1. **Enter Origin:** Type "Union Square, San Francisco"
2. **Enter Destination:** Type "Ferry Building, San Francisco"
3. **Click:** "Find Safest Route"
4. **Wait:** 5-10 seconds for route analysis
5. **View:** 3 routes with safety scores displayed!

## Verify It's Working

### Test Backend Health

Open a new terminal and run:
```bash
curl http://localhost:8000/api/health
```

You should see:
```json
{
  "status": "healthy",
  "data": {
    "crime_incidents": 245,
    "311_incidents": 178,
    "last_fetch": "2025-10-26T..."
  }
}
```

### Check Frontend Console

Open browser DevTools (F12) and check Console tab:
- Should see: `= Requesting routes from backend...`
- Should see: ` Received routes from backend...`

## Common Issues

### Backend Error: "ModuleNotFoundError"

```bash
# Make sure virtual environment is activated
# You should see (venv) in your terminal prompt

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Error: "Cannot connect to backend"

1. Verify backend is running on port 8000
2. Check for error messages in backend terminal
3. Try restarting both servers

### Port Already in Use

**Backend (Port 8000):**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

**Frontend (Port 3000):**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:3000 | xargs kill -9
```

## What's Happening Behind the Scenes?

1. **Backend** fetches latest crime and 311 data from DataSF APIs
2. **Backend** schedules automatic updates every 10 minutes
3. **User** enters origin and destination
4. **Backend** generates 10 route variations using GraphHopper
5. **Backend** analyzes each route against incident data
6. **Backend** calculates risk scores using time-decay algorithm
7. **Backend** returns top 3 safest routes
8. **Frontend** displays routes on interactive map

## Next Steps

- Read the full [README.md](./README.md) for detailed documentation
- Explore the risk scoring algorithm
- Try different routes across San Francisco
- Check backend logs to see data refresh cycles

## Quick Commands Reference

### Backend
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
cd app
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm start
```

### Test API
```bash
curl http://localhost:8000/api/health
```

## Hackathon Demo Tips

1. **Pre-load data:** Start backend 10 minutes before demo to ensure data is fresh
2. **Test routes:** Try these high-contrast examples:
   - Union Square ’ Ferry Building (central, moderate risk)
   - Tenderloin ’ Civic Center (higher risk area)
   - Marina ’ Presidio (lower risk area)
3. **Show features:**
   - Point out the 3 routes with different colors
   - Highlight safety scores (0-100)
   - Mention real-time data (updated every 10 min)
   - Explain the risk algorithm briefly

## Support

If you encounter issues:
1. Check both terminal windows for error messages
2. Verify all dependencies are installed
3. Ensure `.env` files are properly configured
4. Restart both servers

---

**Time to first route: ~5 minutes from clone to working app!** ¡

Good luck with your hackathon! =€
