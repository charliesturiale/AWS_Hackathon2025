"use client"

import { useEffect, useRef, useState } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Info } from "lucide-react"
import type { Route } from "./safe-path-app"

interface RouteMapProps {
  routeCalculated: boolean
  origin?: string
  destination?: string
  routes?: Route[]
  selectedRouteId?: number
}

// Declare MapKit types
declare global {
  interface Window {
    mapkit: any
    initMapKit: () => void
  }
}

export default function RouteMap({ routeCalculated, origin, destination, routes, selectedRouteId }: RouteMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const [mapReady, setMapReady] = useState(false)
  const [mapError, setMapError] = useState<string | null>(null)

  useEffect(() => {
    const initMap = async () => {
      if (!window.mapkit || !mapRef.current) return

      try {
        // Fetch token from API route
        const response = await fetch("/api/mapkit-token")
        const { token } = await response.json()

        window.mapkit.init({
          authorizationCallback: (done: (token: string) => void) => {
            done(token)
          },
          language: "en",
        })

        // Create map centered on San Francisco
        const map = new window.mapkit.Map(mapRef.current, {
          center: new window.mapkit.Coordinate(37.7749, -122.4194),
          zoom: 13,
          colorScheme: window.mapkit.Map.ColorSchemes.Dark,
          showsCompass: window.mapkit.FeatureVisibility.Visible,
          showsZoomControl: true,
          showsUserLocation: true,
          showsUserLocationControl: true,
        })

        mapInstanceRef.current = map
        setMapReady(true)
        setMapError(null)
      } catch (error) {
        console.error("[v0] MapKit initialization error:", error)
        setMapError("Unable to load map. Please check MapKit JS configuration.")
      }
    }

    // Set up callback for MapKit initialization
    window.initMapKit = initMap

    // If MapKit is already loaded, initialize immediately
    if (window.mapkit) {
      initMap()
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.destroy()
      }
    }
  }, [])

  useEffect(() => {
    if (!mapReady || !routeCalculated || !mapInstanceRef.current || !routes || routes.length === 0) return

    const map = mapInstanceRef.current

    // Clear existing annotations and overlays
    map.removeAnnotations(map.annotations)
    map.removeOverlays(map.overlays)

    // Get start and end coordinates from first route
    const firstRoute = routes[0]
    const startCoord = firstRoute.coordinates[0]
    const endCoord = firstRoute.coordinates[firstRoute.coordinates.length - 1]

    const startCoordinate = new window.mapkit.Coordinate(startCoord.lat, startCoord.lng)
    const endCoordinate = new window.mapkit.Coordinate(endCoord.lat, endCoord.lng)

    // Create start marker
    const startAnnotation = new window.mapkit.MarkerAnnotation(startCoordinate, {
      color: "#10b981",
      title: "Start",
      subtitle: origin || "Starting Point",
      glyphText: "S",
    })

    // Create end marker
    const endAnnotation = new window.mapkit.MarkerAnnotation(endCoordinate, {
      color: "#3b82f6",
      title: "Destination",
      subtitle: destination || "Your Destination",
      glyphText: "D",
    })

    // Add markers to map
    map.addAnnotations([startAnnotation, endAnnotation])

    routes.forEach((route) => {
      const routeCoordinates = route.coordinates.map((coord) => new window.mapkit.Coordinate(coord.lat, coord.lng))

      // Determine line width and opacity based on selection
      const isSelected = route.id === selectedRouteId
      const lineWidth = isSelected ? 6 : 4
      const opacity = isSelected ? 1 : 0.4

      // Create polyline for route
      const routeLine = new window.mapkit.PolylineOverlay(routeCoordinates, {
        style: new window.mapkit.Style({
          lineWidth: lineWidth,
          strokeColor: route.color,
          lineCap: "round",
          lineJoin: "round",
        }),
      })

      // Set opacity by modifying the overlay's element after it's added
      map.addOverlay(routeLine)

      // Add waypoint markers only for selected route
      if (isSelected) {
        route.waypoints.forEach((waypoint, index) => {
          // Use waypoint coordinates from route (skip first and last as they're start/end)
          const waypointIndex = Math.floor((index + 1) * (route.coordinates.length / (route.waypoints.length + 1)))
          const coord = route.coordinates[waypointIndex]

          const waypointAnnotation = new window.mapkit.MarkerAnnotation(
            new window.mapkit.Coordinate(coord.lat, coord.lng),
            {
              color: waypoint.safe ? "#10b981" : "#f59e0b",
              glyphText: waypoint.safe ? "✓" : "!",
              title: waypoint.name,
              subtitle: waypoint.type,
            },
          )
          map.addAnnotations([waypointAnnotation])
        })
      }
    })

    // Fit map to show entire route
    const region = map.regionThatFits(
      new window.mapkit.BoundingRegion(
        startCoordinate.latitude,
        startCoordinate.longitude,
        endCoordinate.latitude,
        endCoordinate.longitude,
      ).toCoordinateRegion(),
    )
    map.setRegionAnimated(region)
  }, [mapReady, routeCalculated, origin, destination, routes, selectedRouteId])

  return (
    <Card className="relative h-[calc(100vh-12rem)] overflow-hidden">
      {/* Interactive Apple Maps */}
      <div ref={mapRef} className="h-full w-full" />

      {/* Current Location Indicator */}
      {routeCalculated && mapReady && (
        <div className="absolute bottom-4 left-4 z-10">
          <Badge className="bg-card text-card-foreground shadow-lg">
            <div className="mr-2 h-2 w-2 animate-pulse rounded-full bg-accent" />
            Live Tracking
          </Badge>
        </div>
      )}

      {/* Error State */}
      {mapError && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted p-4">
          <Alert className="max-w-md">
            <Info className="h-4 w-4" />
            <AlertDescription>
              {mapError}
              <br />
              <span className="text-xs text-muted-foreground">See MAPKIT_SETUP.md for configuration instructions.</span>
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* Loading State */}
      {!mapReady && !mapError && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted">
          <div className="text-center">
            <div className="mb-2 h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            <p className="text-sm text-muted-foreground">Loading map...</p>
          </div>
        </div>
      )}
    </Card>
  )
}
