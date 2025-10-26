# GraphHopper API Setup Guide

SafePath uses GraphHopper's Routing API to calculate real walking routes with turn-by-turn navigation.

## Quick Setup (5 minutes)

### Step 1: Get Your Free API Key

1. Go to [https://www.graphhopper.com/](https://www.graphhopper.com/)
2. Click **"Sign Up"** (top right)
3. Create a free account
4. Once logged in, go to the [Dashboard](https://graphhopper.com/dashboard/)
5. Click **"API Keys"** in the sidebar
6. Click **"Create API Key"**
7. Give it a name (e.g., "SafePath Development")
8. Copy your API key

### Step 2: Add API Key to Your Project

1. In your project root directory, create a `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and add your API key:
   ```
   REACT_APP_GRAPHHOPPER_API_KEY=your_actual_api_key_here
   ```

3. **Restart your development server:**
   ```bash
   # Stop the current server (Ctrl+C)
   # Then restart:
   npm start
   ```

### Step 3: Test It Out!

1. Open your app at [http://localhost:3000](http://localhost:3000)
2. Enter a starting point (e.g., "San Francisco City Hall")
3. Enter a destination (e.g., "Ferry Building San Francisco")
4. Click **"Find Safest Route"**
5. The app will fetch real routes from GraphHopper! 🎉

## Features You Get

With GraphHopper integration, you get:

✅ **Real Route Calculation** - Actual walking routes, not mock data
✅ **Multiple Alternatives** - Up to 3 different route options
✅ **Accurate Distance & Time** - Real-world estimates
✅ **Turn-by-Turn Coordinates** - Detailed path coordinates for map display
✅ **Geocoding** - Convert addresses to GPS coordinates automatically

## Free Tier Limits

GraphHopper's free tier includes:
- **500 requests per day**
- **Routing & Geocoding APIs**
- All standard features

Perfect for development and small-scale applications!

## API Endpoints Used

SafePath uses two GraphHopper APIs:

1. **Geocoding API** - Converts addresses to coordinates
   - Endpoint: `https://graphhopper.com/api/1/geocode`

2. **Routing API** - Calculates walking routes
   - Endpoint: `https://graphhopper.com/api/1/route`
   - Vehicle type: `foot` (walking routes)
   - Algorithm: `alternative_route` (for multiple options)

## Troubleshooting

**Error: "GraphHopper API key not configured"**
- Make sure you created the `.env` file
- Verify the API key is correctly copied
- Restart your development server after adding the key

**Error: "Could not calculate routes"**
- Check that your API key is valid
- Verify you haven't exceeded the daily limit (500 requests)
- Make sure the addresses are specific enough (include city/state)

**Routes not showing on map**
- Check the browser console for errors
- Verify the addresses are valid locations
- Try more specific addresses (e.g., "123 Market St, San Francisco, CA")

## Example Addresses to Test

Try these address pairs to see routing in action:

**San Francisco:**
- Start: "Union Square, San Francisco"
- End: "Fisherman's Wharf, San Francisco"

**New York:**
- Start: "Times Square, New York"
- End: "Central Park, New York"

**Any City:**
- Use specific landmarks or street addresses
- Include city and state for best results

## Next Steps

Once you have routing working, you can:
- Integrate real crime data for safety scoring
- Add real-time weather conditions
- Implement user location tracking
- Store favorite routes
- Add transit integration

## Resources

- [GraphHopper Documentation](https://docs.graphhopper.com/)
- [API Playground](https://graphhopper.com/api/1/examples/)
- [Routing API Docs](https://docs.graphhopper.com/#tag/Routing-API)
- [Geocoding API Docs](https://docs.graphhopper.com/#tag/Geocoding-API)

---

**Need help?** Check the [GraphHopper Community Forum](https://discuss.graphhopper.com/)
