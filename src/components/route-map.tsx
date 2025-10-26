import { useEffect, useState } from "react"
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Route } from "./safe-path-app"
import { getRecentIncidents, type Incident } from "@/services/SafetyDataService"
import L from "leaflet"
import "leaflet/dist/leaflet.css"

interface RouteMapProps {
  routeCalculated: boolean
  origin?: string
  destination?: string
  routes?: Route[]
  selectedRouteId?: number
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

// Create icon for incidents
const createIncidentIcon = (incident: Incident) => {
  const colors = {
    encampment: "#9333ea",
    aggressive: "#dc2626",
    crime: "#ef4444",
    suspicious: "#f97316"
  }
  
  const symbols = {
    encampment: "⛺",
    aggressive: "⚠",
    crime: "🚨",
    suspicious: "👁"
  }
  
  const severitySize = {
    high: 24,
    medium: 20,
    low: 16
  }
  
  const color = colors[incident.type]
  const symbol = symbols[incident.type]
  const size = severitySize[incident.severity]
  
  return L.divIcon({
    className: "incident-marker",
    html: `
      <div style="
        background: ${color};
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: ${size * 0.6}px;
        opacity: 0.9;
      ">${symbol}</div>
    `,
    iconSize: [size, size],
    iconAnchor: [size/2, size/2],
    popupAnchor: [0, -size/2],
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
  const [showIncidents, setShowIncidents] = useState(true)

  const startIcon = createCustomIcon("#8b5cf6", "S")
  const endIcon = createCustomIcon("#06b6d4", "D")
  
  // Load incidents when component mounts or route is calculated
  useEffect(() => {
    async function loadIncidents() {
      try {
        const recentIncidents = await getRecentIncidents()
        setIncidents(recentIncidents)
      } catch (error) {
        console.error("Failed to load incidents:", error)
      }
    }
    
    if (routeCalculated) {
      loadIncidents()
    }
  }, [routeCalculated])

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
            
            {/* Incident markers from 311 and dispatch data */}
            {showIncidents && incidents.map((incident) => (
              <Marker
                key={incident.id}
                position={[incident.location.lat, incident.location.lng]}
                icon={createIncidentIcon(incident)}
              >
                <Popup>
                  <div className="p-2">
                    <div className="font-semibold text-sm">
                      {incident.type === 'encampment' && '311: Encampment'}
                      {incident.type === 'aggressive' && '311: Aggressive/Threatening'}
                      {incident.type === 'crime' && 'SFPD: Crime Report'}
                      {incident.type === 'suspicious' && 'SFPD: Suspicious Activity'}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {incident.description}
                    </div>
                    <div className="text-xs mt-1">
                      <span className={`font-semibold ${
                        incident.severity === 'high' ? 'text-red-600' :
                        incident.severity === 'medium' ? 'text-orange-600' :
                        'text-yellow-600'
                      }`}>
                        {incident.severity.toUpperCase()} severity
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {new Date(incident.datetime).toLocaleString()}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Status: {incident.status}
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </>
        )}
      </MapContainer>

      {/* Map Controls */}
      {routeCalculated && (
        <>
          <div className="absolute bottom-4 left-4 z-[1000] space-y-2">
            <Badge className="gradient-primary text-white shadow-glow px-3 py-1.5">
              <div className="mr-2 h-2 w-2 animate-pulse rounded-full bg-white" />
              Live Map
            </Badge>
            
            {/* Incident Toggle */}
            <button
              onClick={() => setShowIncidents(!showIncidents)}
              className="flex items-center gap-2 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 text-sm font-medium shadow-lg border border-border/50 hover:bg-white transition-colors"
            >
              <span className="text-lg">{showIncidents ? '🚨' : '🔒'}</span>
              <span>{showIncidents ? 'Hide' : 'Show'} Incidents</span>
              {incidents.length > 0 && (
                <Badge variant="secondary" className="ml-1">
                  {incidents.length}
                </Badge>
              )}
            </button>
          </div>
          
          {/* Incident Statistics */}
          {showIncidents && incidents.length > 0 && (
            <div className="absolute top-4 right-4 z-[1000] bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg border border-border/50 max-w-xs">
              <div className="text-sm font-semibold mb-2">Recent Incidents (48hr)</div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center gap-1">
                  <span>⛺</span>
                  <span>Encampments: {incidents.filter(i => i.type === 'encampment').length}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>⚠</span>
                  <span>Aggressive: {incidents.filter(i => i.type === 'aggressive').length}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>🚨</span>
                  <span>Crimes: {incidents.filter(i => i.type === 'crime').length}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>👁</span>
                  <span>Suspicious: {incidents.filter(i => i.type === 'suspicious').length}</span>
                </div>
              </div>
              <div className="mt-2 pt-2 border-t text-xs text-muted-foreground">
                Total: {incidents.length} incidents
              </div>
            </div>
          )}
        </>
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
