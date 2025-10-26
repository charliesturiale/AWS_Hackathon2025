import { useEffect, useState } from "react"
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap, Circle } from "react-leaflet"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Route } from "./safe-path-app"
import L from "leaflet"
import "leaflet/dist/leaflet.css"

interface RouteMapProps {
  routeCalculated: boolean
  origin?: string
  destination?: string
  routes?: Route[]
  selectedRouteId?: number
}

interface Incident {
  type: "crime" | "311"
  title: string
  subtype?: string
  date: string
  location?: string
  status?: string
  coordinates: {
    lat: number
    lng: number
  }
}

// Fix for default marker icons in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
})

// Custom icons for start and destination
const createCustomIcon = (color: string, text: string) => {
  return L.divIcon({
    className: "custom-marker",
    html: `
      <div style="
        background: ${color};
        width: 36px;
        height: 36px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 3px solid white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <span style="
          color: white;
          font-weight: bold;
          font-size: 16px;
          transform: rotate(45deg);
        ">${text}</span>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36],
  })
}

const createWaypointIcon = (safe: boolean) => {
  const color = safe ? "#10b981" : "#f59e0b"
  const symbol = safe ? "✓" : "!"

  return L.divIcon({
    className: "waypoint-marker",
    html: `
      <div style="
        background: ${color};
        width: 28px;
        height: 28px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
      ">${symbol}</div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -14],
  })
}

// Incident marker icon - different styling for crime vs 311
const createIncidentIcon = (type: "crime" | "311", count?: number) => {
  const color = type === "crime" ? "#ef4444" : "#f59e0b"
  const size = 26
  const displayText = count && count > 1 ? count.toString() : "!"

  return L.divIcon({
    className: "incident-marker",
    html: `
      <div style="
        background: ${color};
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 3px 6px rgba(0,0,0,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: ${count && count > 9 ? '10px' : '13px'};
        opacity: 0.9;
      ">${displayText}</div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  })
}

// Component to handle map bounds updates
function MapBoundsUpdater({ routes, routeCalculated }: { routes?: Route[]; routeCalculated: boolean }) {
  const map = useMap()

  useEffect(() => {
    if (!routeCalculated || !routes || routes.length === 0) return

    const firstRoute = routes[0]
    const bounds = L.latLngBounds(
      firstRoute.coordinates.map((coord) => [coord.lat, coord.lng] as [number, number])
    )

    map.fitBounds(bounds, { padding: [50, 50] })
  }, [routes, routeCalculated, map])

  return null
}

export default function RouteMap({ routeCalculated, origin, destination, routes, selectedRouteId }: RouteMapProps) {
  // Default center on San Francisco
  const defaultCenter: [number, number] = [37.7749, -122.4194]
  const defaultZoom = 13

  const [incidents, setIncidents] = useState<Incident[]>([])
  const [incidentsLoading, setIncidentsLoading] = useState(false)

  // Fetch incidents on component mount
  useEffect(() => {
    const fetchIncidents = async () => {
      setIncidentsLoading(true)
      try {
        const response = await fetch('http://localhost:8000/api/incidents')
        const data = await response.json()
        if (data.incidents) {
          setIncidents(data.incidents)
          console.log(`Loaded ${data.total_count} incidents: ${data.crime_count} crimes, ${data.incident_311_count} 311 incidents`)
        }
      } catch (error) {
        console.error('Failed to fetch incidents:', error)
      } finally {
        setIncidentsLoading(false)
      }
    }

    fetchIncidents()
  }, [])

  const startIcon = createCustomIcon("#8b5cf6", "S")
  const endIcon = createCustomIcon("#06b6d4", "D")

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  return (
    <Card className="relative h-[calc(100vh-12rem)] overflow-hidden shadow-lg border-2 border-border/50">
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        style={{ height: "100%", width: "100%", zIndex: 0 }}
        zoomControl={true}
        scrollWheelZoom={true}
      >
        {/* OpenStreetMap Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Incident Markers - Always visible */}
        {incidents.map((incident, index) => (
          <Marker
            key={`incident-${index}`}
            position={[incident.coordinates.lat, incident.coordinates.lng]}
            icon={createIncidentIcon(incident.type)}
          >
            <Popup>
              <div className="min-w-[200px]">
                <div className="font-semibold text-base mb-1">{incident.title}</div>
                {incident.subtype && (
                  <div className="text-sm text-muted-foreground mb-1">{incident.subtype}</div>
                )}
                {incident.location && (
                  <div className="text-sm text-muted-foreground mb-1">{incident.location}</div>
                )}
                <div className="text-xs text-muted-foreground mt-2">
                  {formatDate(incident.date)}
                </div>
                {incident.status && (
                  <div className="text-xs mt-1">
                    <span className={`px-2 py-0.5 rounded-full ${
                      incident.status.toLowerCase() === 'open'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {incident.status}
                    </span>
                  </div>
                )}
                <div className="mt-2 pt-2 border-t border-border">
                  <span className={`text-xs font-semibold ${
                    incident.type === 'crime' ? 'text-red-600' : 'text-orange-600'
                  }`}>
                    {incident.type === 'crime' ? 'Crime Incident' : '311 Report'}
                  </span>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Render routes if calculated */}
        {routeCalculated && routes && routes.length > 0 && (
          <>
            {/* Update map bounds */}
            <MapBoundsUpdater routes={routes} routeCalculated={routeCalculated} />

            {/* Draw all routes */}
            {routes.map((route) => {
              const isSelected = route.id === selectedRouteId
              const positions = route.coordinates.map((coord) => [coord.lat, coord.lng] as [number, number])

              return (
                <Polyline
                  key={route.id}
                  positions={positions}
                  pathOptions={{
                    color: route.color,
                    weight: isSelected ? 6 : 4,
                    opacity: isSelected ? 1 : 0.5,
                    lineCap: "round",
                    lineJoin: "round",
                  }}
                />
              )
            })}

            {/* Start and End markers */}
            {(() => {
              const firstRoute = routes[0]
              const startCoord = firstRoute.coordinates[0]
              const endCoord = firstRoute.coordinates[firstRoute.coordinates.length - 1]

              return (
                <>
                  <Marker position={[startCoord.lat, startCoord.lng]} icon={startIcon}>
                    <Popup>
                      <div className="font-semibold">Start</div>
                      <div className="text-sm text-muted-foreground">{origin || "Starting Point"}</div>
                    </Popup>
                  </Marker>

                  <Marker position={[endCoord.lat, endCoord.lng]} icon={endIcon}>
                    <Popup>
                      <div className="font-semibold">Destination</div>
                      <div className="text-sm text-muted-foreground">{destination || "Your Destination"}</div>
                    </Popup>
                  </Marker>
                </>
              )
            })()}

            {/* Waypoint markers for selected route */}
            {(() => {
              const selectedRoute = routes.find((r) => r.id === selectedRouteId)
              if (!selectedRoute) return null

              return selectedRoute.waypoints.map((waypoint, index) => {
                // Calculate waypoint position along the route
                const waypointIndex = Math.floor(
                  (index + 1) * (selectedRoute.coordinates.length / (selectedRoute.waypoints.length + 1))
                )
                const coord = selectedRoute.coordinates[waypointIndex]

                return (
                  <Marker
                    key={index}
                    position={[coord.lat, coord.lng]}
                    icon={createWaypointIcon(waypoint.safe)}
                  >
                    <Popup>
                      <div className="font-semibold">{waypoint.name}</div>
                      <div className="text-sm text-muted-foreground">{waypoint.type}</div>
                      <div className={`text-xs font-semibold mt-1 ${waypoint.safe ? "text-green-600" : "text-yellow-600"}`}>
                        {waypoint.safe ? "Safe Area" : "Use Caution"}
                      </div>
                    </Popup>
                  </Marker>
                )
              })
            })()}
          </>
        )}
      </MapContainer>

      {/* Live Tracking Badge */}
      {routeCalculated && (
        <div className="absolute bottom-4 left-4 z-[1000]">
          <Badge className="gradient-primary text-white shadow-glow px-3 py-1.5">
            <div className="mr-2 h-2 w-2 animate-pulse rounded-full bg-white" />
            Live Map
          </Badge>
        </div>
      )}

      {/* Map Attribution */}
      {!routeCalculated && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm z-[1000]">
          <div className="text-center p-6">
            <div className="text-lg font-display font-bold text-foreground mb-2">
              Enter a route to get started
            </div>
            <p className="text-sm text-muted-foreground">
              Interactive map powered by OpenStreetMap
            </p>
          </div>
        </div>
      )}
    </Card>
  )
}
