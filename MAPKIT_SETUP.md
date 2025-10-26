# Apple MapKit JS Setup Guide

To use the interactive Apple Maps in SafePath, you need to set up MapKit JS authentication.

## Steps to Get Your MapKit JS Token:

1. **Sign in to Apple Developer**
   - Go to https://developer.apple.com
   - Sign in with your Apple ID

2. **Create a Maps ID**
   - Navigate to Certificates, Identifiers & Profiles
   - Select "Identifiers" from the sidebar
   - Click the "+" button to create a new identifier
   - Select "Maps IDs" and click "Continue"
   - Enter a description and identifier (e.g., `com.yourcompany.safepath`)
   - Click "Continue" and then "Register"

3. **Create a Key**
   - Go to "Keys" in the sidebar
   - Click the "+" button to create a new key
   - Enter a key name (e.g., "SafePath MapKit Key")
   - Check "MapKit JS" under Key Services
   - Click "Continue" and then "Register"
   - Download the key file (.p8) - you'll need this

4. **Generate JWT Token**
   - You'll need to create a server endpoint that generates JWT tokens
   - Use your Team ID, Key ID, and the .p8 private key
   - The token should be generated server-side for security

5. **Add Environment Variable**
   - Add `NEXT_PUBLIC_MAPKIT_TOKEN` to your environment variables
   - In production, implement a server endpoint to generate tokens dynamically

## Alternative: Use the Demo Mode

For development/testing without a token, the map will show a watermark but remain functional.

## Resources:
- [MapKit JS Documentation](https://developer.apple.com/documentation/mapkitjs)
- [MapKit JS Setup Guide](https://developer.apple.com/documentation/mapkitjs/setting_up_mapkit_js)
