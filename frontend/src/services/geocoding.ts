/**
 * Geocoding Service using Nominatim OpenStreetMap API
 * Provides address autocomplete and geocoding functionality
 */

export interface AddressSuggestion {
  display_name: string
  lat: string
  lon: string
  place_id: number
  osm_type: string
  type: string
}

const NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
const SEARCH_PARAMS = {
  format: "json",
  limit: "5",
  countrycodes: "us",
  // Removed bounded and viewbox to allow dynamic search results
}

// Request throttling to respect Nominatim usage policy (max 1 request per second)
let lastRequestTime = 0
const MIN_REQUEST_INTERVAL = 1000 // ms

/**
 * Search for address suggestions based on user input
 * Debounced and throttled to respect API limits
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
    const params = new URLSearchParams({
      ...SEARCH_PARAMS,
      q: query, // Use query as-is for dynamic narrowing
    })

    const response = await fetch(`${NOMINATIM_BASE_URL}/search?${params}`, {
      headers: {
        "User-Agent": "SafePath-App/1.0", // Required by Nominatim usage policy
      },
    })

    lastRequestTime = Date.now()

    if (!response.ok) {
      console.error("Geocoding API error:", response.statusText)
      return []
    }

    const data: AddressSuggestion[] = await response.json()
    return data
  } catch (error) {
    console.error("Address search error:", error)
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
