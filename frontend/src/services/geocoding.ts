/**
 * Geocoding Service using GraphHopper Geocoding API
 * Provides address autocomplete and geocoding functionality
 *
 * IMPORTANT: Uses GraphHopper to match backend geocoding service
 * This ensures 100% consistency between autocomplete suggestions and route calculation
 */

export interface AddressSuggestion {
  display_name: string
  lat: string
  lon: string
  place_id: number
  osm_type: string
  type: string
}

// GraphHopper API Configuration
const GRAPHHOPPER_API_KEY = process.env.REACT_APP_GRAPHHOPPER_API_KEY || "72974d83-39d7-4a65-95eb-4440960fde46"
const GRAPHHOPPER_GEOCODE_URL = "https://graphhopper.com/api/1/geocode"

// San Francisco bounding box (min_lon, min_lat, max_lon, max_lat)
const SF_BBOX = {
  min_lon: -122.52,
  min_lat: 37.70,
  max_lon: -122.35,
  max_lat: 37.85
}

// Request throttling to respect API limits (1 request per second for free tier)
let lastRequestTime = 0
const MIN_REQUEST_INTERVAL = 300 // ms (can be more aggressive than Nominatim)

/**
 * Search for address suggestions using GraphHopper Geocoding API
 * Same API used by backend for 100% consistency
 */
export async function searchAddresses(query: string): Promise<AddressSuggestion[]> {
  if (!query || query.trim().length < 3) {
    return []
  }

  // Throttle requests
  const now = Date.now()
  const timeSinceLastRequest = now - lastRequestTime
  if (timeSinceLastRequest < MIN_REQUEST_INTERVAL) {
    await new Promise(resolve => setTimeout(resolve, MIN_REQUEST_INTERVAL - timeSinceLastRequest))
  }

  try {
    // Append ", San Francisco, CA" for better results (matches backend behavior)
    const searchQuery = query.toLowerCase().includes('san francisco')
      ? query
      : `${query}, San Francisco, CA`

    const params = new URLSearchParams({
      q: searchQuery,
      key: GRAPHHOPPER_API_KEY,
      limit: "10",
      locale: "en"
    })

    const response = await fetch(`${GRAPHHOPPER_GEOCODE_URL}?${params}`)

    lastRequestTime = Date.now()

    if (!response.ok) {
      console.error("GraphHopper geocoding error:", response.statusText)
      return []
    }

    const data = await response.json()

    if (!data.hits || data.hits.length === 0) {
      return []
    }

    // Filter to San Francisco bounding box and convert to AddressSuggestion format
    const sfAddresses: AddressSuggestion[] = data.hits
      .filter((hit: any) => {
        const point = hit.point
        const lat = point.lat
        const lng = point.lng

        // Strict San Francisco bounding box filter (matches backend validation)
        return lat >= SF_BBOX.min_lat &&
               lat <= SF_BBOX.max_lat &&
               lng >= SF_BBOX.min_lon &&
               lng <= SF_BBOX.max_lon
      })
      .map((hit: any, index: number) => {
        // Build display name from GraphHopper data
        const parts = []
        if (hit.housenumber && hit.street) {
          parts.push(`${hit.housenumber} ${hit.street}`)
        } else if (hit.street) {
          parts.push(hit.street)
        } else if (hit.name) {
          parts.push(hit.name)
        }

        if (hit.city && hit.city !== "San Francisco") {
          parts.push(hit.city)
        }
        parts.push("San Francisco, CA")

        return {
          display_name: parts.join(", "),
          lat: hit.point.lat.toString(),
          lon: hit.point.lng.toString(),
          place_id: hit.osm_id || index,
          osm_type: hit.osm_type || "node",
          type: hit.osm_value || "place"
        }
      })
      .slice(0, 5) // Return up to 5 suggestions

    return sfAddresses
  } catch (error) {
    console.error("GraphHopper address search error:", error)
    return []
  }
}

/**
 * Format address for display (shorten long addresses)
 */
export function formatAddress(displayName: string): string {
  // Remove country and state from display for brevity
  const parts = displayName.split(", ")
  // Keep only first 3-4 parts (street, city, zip)
  return parts.slice(0, Math.min(4, parts.length)).join(", ")
}
