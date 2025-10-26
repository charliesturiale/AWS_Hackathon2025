#!/bin/bash

# SafePath SF - DataSF Download Script
# Downloads essential datasets for route safety calculation

echo "🚀 SafePath SF - DataSF Download Script"
echo "======================================="

# Create data directory if it doesn't exist
DATA_DIR="./data/datasf"
mkdir -p $DATA_DIR

# Get current date for filtering
CURRENT_DATE=$(date -u +"%Y-%m-%dT%H:%M:%S")
THIRTY_DAYS_AGO=$(date -v-30d -u +"%Y-%m-%d")
NINETY_DAYS_AGO=$(date -v-90d -u +"%Y-%m-%d")

echo "📅 Downloading data from $NINETY_DAYS_AGO to $CURRENT_DATE"
echo ""

# Function to download with progress
download_dataset() {
    local name=$1
    local url=$2
    local output=$3
    
    echo "📥 Downloading $name..."
    curl -X GET "$url" \
        --progress-bar \
        -H "Accept: application/json" \
        -o "$DATA_DIR/$output"
    
    # Check if download was successful
    if [ $? -eq 0 ]; then
        local size=$(ls -lh "$DATA_DIR/$output" | awk '{print $5}')
        echo "✅ $name downloaded successfully ($size)"
    else
        echo "❌ Failed to download $name"
    fi
    echo ""
}

# 1. CRIME DATA (Last 30 days - most critical for safety)
echo "🚨 [1/5] Fetching Crime Data..."
CRIME_URL="https://data.sfgov.org/resource/wg3w-h783.json?\$where=incident_datetime>'${THIRTY_DAYS_AGO}'&\$limit=50000&\$select=incident_id,incident_datetime,incident_category,incident_subcategory,latitude,longitude,analysis_neighborhood"
download_dataset "Crime Data (30 days)" "$CRIME_URL" "crime_data.json"

# 2. 311 HAZARDS (Open cases only - real-time hazards)
echo "🚧 [2/5] Fetching 311 Hazards..."
HAZARDS_URL="https://data.sfgov.org/resource/vw6y-z8j6.json?\$where=status_description='Open' AND (service_name='Streetlight' OR service_name='Encampment' OR service_name='Blocked Street or SideWalk' OR service_name='Street Defects' OR service_name='Sidewalk or Curb')&\$limit=10000&\$select=service_request_id,requested_datetime,status_description,service_name,lat,long,address"
download_dataset "311 Hazards (Open)" "$HAZARDS_URL" "hazards_311.json"

# 3. STREET LIGHTS (Full dataset - infrastructure)
echo "💡 [3/5] Fetching Street Lights..."
# Note: This dataset might have a different endpoint - using placeholder
LIGHTS_URL="https://data.sfgov.org/resource/vw6y-z8j6.json?\$where=service_name='Streetlight'&\$limit=5000&\$select=service_request_id,lat,long,address,status_description"
download_dataset "Street Light Issues" "$LIGHTS_URL" "street_lights.json"

# 4. TRAFFIC CRASHES (Pedestrian involved - last 2 years)
echo "🚗 [4/5] Fetching Traffic Crash Data..."
TWO_YEARS_AGO=$(date -v-730d -u +"%Y-%m-%d")
# Note: Using crime data endpoint as placeholder - replace with actual traffic crash endpoint
CRASHES_URL="https://data.sfgov.org/resource/wg3w-h783.json?\$where=incident_datetime>'${TWO_YEARS_AGO}' AND incident_category='Vehicle Collision'&\$limit=10000&\$select=incident_id,incident_datetime,latitude,longitude"
download_dataset "Traffic Crashes" "$CRASHES_URL" "traffic_crashes.json"

# 5. Create a summary file
echo "📊 [5/5] Creating Summary..."
cat > "$DATA_DIR/download_summary.json" << EOF
{
  "download_date": "$CURRENT_DATE",
  "date_range": {
    "crime_data": "$THIRTY_DAYS_AGO to $CURRENT_DATE",
    "hazards": "Open cases only",
    "crashes": "$TWO_YEARS_AGO to $CURRENT_DATE"
  },
  "files": [
    "crime_data.json",
    "hazards_311.json",
    "street_lights.json",
    "traffic_crashes.json"
  ]
}
EOF

echo "✅ Summary created"
echo ""

# Calculate total size
echo "📦 Download Complete!"
echo "===================="
echo "Total data downloaded:"
du -sh $DATA_DIR
echo ""
echo "Files:"
ls -lh $DATA_DIR/*.json

echo ""
echo "🎉 All essential DataSF datasets downloaded!"
echo "📍 Data location: $DATA_DIR"
echo ""
echo "Next steps:"
echo "1. Review the data in $DATA_DIR"
echo "2. Run 'npm run process-data' to preprocess for the app"
echo "3. Upload to AWS S3 for production use"