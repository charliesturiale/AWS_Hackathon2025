# Vercel Deployment Guide for SafePath SF

## 🚨 IMPORTANT: Environment Variables

The `.env` file is NOT automatically deployed to Vercel. You must manually add environment variables in the Vercel dashboard.

## Required Environment Variables

### 1. GraphHopper API Key (REQUIRED)
```
Name: REACT_APP_GRAPHHOPPER_API_KEY
Value: ee6ac405-9a11-42e2-a0ac-dc333939f34b
```

### 2. DataSF API Key (Optional)
```
Name: REACT_APP_DATASF_API_KEY
Value: [Your DataSF API key if you have one]
```

## Step-by-Step Setup

1. **Go to your Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Select your SafePath SF project

2. **Navigate to Settings**
   - Click on "Settings" tab
   - Select "Environment Variables" from the left menu

3. **Add the GraphHopper API Key**
   - Click "Add New"
   - Key: `REACT_APP_GRAPHHOPPER_API_KEY`
   - Value: `ee6ac405-9a11-42e2-a0ac-dc333939f34b`
   - Environment: Select all (Production, Preview, Development)
   - Click "Save"

4. **Trigger a Redeploy**
   - Go to "Deployments" tab
   - Click the three dots on the latest deployment
   - Select "Redeploy"
   - Click "Redeploy" in the dialog

## Verification

After redeployment, the app will show a debug card if the API key is missing. Once properly configured, the debug card will disappear and full routing functionality will be available.

## Troubleshooting

### Routes not calculating?
- Check browser console for errors
- Verify the debug card shows "GraphHopper API: ✓ Configured"
- Ensure you redeployed after adding environment variables

### CORS errors?
- The app has fallback mechanisms for CORS issues
- SF APIs may be blocked by CORS but the app will use default safety scores

### Still having issues?
1. Clear browser cache
2. Check Vercel build logs for errors
3. Ensure you're on the `James` branch
4. Verify root directory is set to `frontend` in Vercel settings

## API Key Information

- **GraphHopper API Key**: `ee6ac405-9a11-42e2-a0ac-dc333939f34b`
- **Free Tier**: 500 requests/day
- **Features**: Geocoding, routing, alternative routes

## Support

If you continue to have issues after following these steps, check:
- Vercel build logs
- Browser developer console
- Network tab for API responses