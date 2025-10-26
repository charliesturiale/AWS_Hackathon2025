import type { Route } from "@/components/safe-path-app"

// Backend API Configuration
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000"

// For backward compatibility - still check if GraphHopper key is configured
const GRAPHHOPPER_API_KEY = process.env.REACT_APP_GRAPHHOPPER_API_KEY || ""

/**
 * Calculate routes using SafePath backend
 * Backend will:
 * 1. Geocode addresses
 * 2. Generate 10 route variations
 * 3. Analyze each route against real-time crime and 311 data
 * 4. Return the top 3 safest routes
 */
export async function calculateRoutes(
  origin: string,
  destination: string
): Promise<{ routes: Route[]; originCoords: { lat: number; lng: number }; destCoords: { lat: number; lng: number } } | null> {
  try {
    console.log(`🔍 Requesting routes from backend: ${origin} → ${destination}`)

    const response = await fetch(`${BACKEND_URL}/api/routes`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        origin,
        destination,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Backend error: ${response.statusText}`)
    }

    const data = await response.json()

    console.log("✅ Received routes from backend:", data)

    // Backend returns routes with risk scores and safety scores already calculated
    // Generate waypoints for visualization (client-side only)
    const routesWithWaypoints: Route[] = data.routes.map((route: any) => {
      // Generate mock waypoints based on route length
      const numWaypoints = 3
      const waypoints = Array.from({ length: numWaypoints }, (_, i) => {
        return {
          name: `Waypoint ${i + 1}`,
          type: route.safetyScore >= 90 ? "Safe area" : route.safetyScore >= 80 ? "Moderate area" : "Caution area",
          safe: route.safetyScore >= 85,
        }
      })

      return {
        ...route,
        // Add computed scores for backward compatibility with existing UI
        crimeScore: route.safetyScore,
        timeScore: route.safetyScore,
        socialScore: route.safetyScore,
        pedestrianScore: route.safetyScore,
        waypoints,
      }
    })

    return {
      routes: routesWithWaypoints,
      originCoords: data.originCoords,
      destCoords: data.destCoords,
    }
  } catch (error) {
    console.error("Backend routing error:", error)

    // Check if backend is unreachable
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error("Cannot connect to SafePath backend. Please ensure the backend server is running on http://localhost:8000")
    }

    throw error
  }
}

/**
 * Check if backend is available
 */
export async function isBackendAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`, {
      method: "GET",
      signal: AbortSignal.timeout(5000), // 5 second timeout
    })
    return response.ok
  } catch (error) {
    console.error("Backend health check failed:", error)
    return false
  }
}

/**
 * Check if GraphHopper API key is configured (for backward compatibility)
 */
export function isGraphHopperConfigured(): boolean {
  return GRAPHHOPPER_API_KEY.length > 0
}
