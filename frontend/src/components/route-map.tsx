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


// Categorize incidents by type for specific icons
const categorizeIncident = (incident: Incident): { category: string; color: string; icon: string } => {
  const title = incident.title.toUpperCase()
  const subtype = incident.subtype?.toUpperCase() || ""

  // Crime categories (high severity)
  if (title.includes("ROBBERY") || title.includes("ASSAULT") || title.includes("BATTERY") ||
      title.includes("WEAPON") || title.includes("EXPLOSIVE")) {
    return { category: "violent", color: "#dc2626", icon: "⚠" }
  }
  if (title.includes("BURGLARY") || title.includes("THEFT") || title.includes("PURSE SNATCH")) {
    return { category: "theft", color: "#ea580c", icon: "🔓" }
  }
  if (title.includes("SUSPICIOUS") || title.includes("FIGHT")) {
    return { category: "suspicious", color: "#f59e0b", icon: "👁" }
  }
  if (title.includes("THREAT") || title.includes("HARASSMENT") || title.includes("INDECENT")) {
    return { category: "harassment", color: "#eab308", icon: "🗣" }
  }

  // 311 categories
  if (title.includes("ENCAMPMENT") || subtype.includes("ENCAMPMENT")) {
    return { category: "encampment", color: "#a855f7", icon: "⛺" }
  }
  if (title.includes("AGGRESSIVE") || title.includes("THREATENING")) {
    return { category: "aggressive", color: "#f97316", icon: "❗" }
  }

  // Default categories
  if (incident.type === "crime") {
    return { category: "crime", color: "#ef4444", icon: "!" }
  }
  return { category: "311", color: "#6366f1", icon: "📋" }
}

// Incident marker icon - different styling and icons by category
const createIncidentIcon = (incident: Incident, count?: number) => {
  const { category, color, icon } = categorizeIncident(incident)
  const size = 30
  const displayText = count && count > 1 ? count.toString() : icon

  return L.divIcon({
    className: "incident-marker",
    html: `
      <div style="
        background: ${color};
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 3px 8px rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: ${count && count > 1 ? '12px' : '15px'};
        opacity: 0.95;
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
  const [incidentsLoading, setIncidentsLoading] = useState(true)
  const [incidentsLoaded, setIncidentsLoaded] = useState(false)

  // Fetch incidents IMMEDIATELY on component mount (before anything else)
  useEffect(() => {
    const fetchIncidents = async () => {
      console.log('Starting incident fetch...')
      setIncidentsLoading(true)
      try {
        const response = await fetch('http://localhost:8000/api/incidents')
        const data = await response.json()
        if (data.incidents) {
          setIncidents(data.incidents)
          setIncidentsLoaded(true)
          console.log(`✓ Loaded ${data.total_count} incidents: ${data.crime_count} crimes, ${data.incident_311_count} 311 incidents`)
        }
      } catch (error) {
        console.error('Failed to fetch incidents:', error)
        setIncidentsLoaded(true) // Continue even if fetch fails
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

        {/* Incident Markers - Always visible with category-specific icons */}
        {incidents.map((incident, index) => {
          const { category, color } = categorizeIncident(incident)
          return (
            <Marker
              key={`incident-${index}`}
              position={[incident.coordinates.lat, incident.coordinates.lng]}
              icon={createIncidentIcon(incident)}
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
                    <span className={`text-xs font-semibold uppercase`} style={{ color }}>
                      {category === 'violent' ? 'High Risk Crime' :
                       category === 'theft' ? 'Property Crime' :
                       category === 'suspicious' ? 'Suspicious Activity' :
                       category === 'harassment' ? 'Harassment/Threats' :
                       category === 'encampment' ? 'Encampment Report' :
                       category === 'aggressive' ? 'Aggressive Behavior' :
                       incident.type === 'crime' ? 'Crime Incident' : '311 Report'}
                    </span>
                  </div>
                </div>
              </Popup>
            </Marker>
          )
        })}

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
