"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MapPin, Navigation, Shield, ChevronRight, Settings } from "lucide-react"
import RouteMap from "@/components/route-map"
import SafetyFactors from "@/components/safety-factors"
import RouteDetails from "@/components/route-details"

export interface Route {
  id: number
  name: string
  distance: string
  time: string
  safetyScore: number
  crimeScore: number
  timeScore: number
  socialScore: number
  pedestrianScore: number
  coordinates: Array<{ lat: number; lng: number }>
  waypoints: Array<{ name: string; type: string; safe: boolean }>
  color: string
}

export default function SafePathApp() {
  const [origin, setOrigin] = useState("")
  const [destination, setDestination] = useState("")
  const [routeCalculated, setRouteCalculated] = useState(false)
  const [routes, setRoutes] = useState<Route[]>([])
  const [selectedRouteId, setSelectedRouteId] = useState<number>(1)

  const handleCalculateRoute = () => {
    if (origin && destination) {
      const generatedRoutes: Route[] = [
        {
          id: 1,
          name: "Safest Route",
          distance: "2.6 mi",
          time: "35 min",
          safetyScore: 95,
          crimeScore: 96,
          timeScore: 92,
          socialScore: 94,
          pedestrianScore: 96,
          color: "#10b981",
          coordinates: [
            { lat: 37.7749, lng: -122.4194 },
            { lat: 37.7769, lng: -122.4174 },
            { lat: 37.7789, lng: -122.4154 },
            { lat: 37.7809, lng: -122.4134 },
            { lat: 37.7829, lng: -122.4114 },
            { lat: 37.7849, lng: -122.4094 },
          ],
          waypoints: [
            { name: "Market Street", type: "Well-lit area", safe: true },
            { name: "Union Square", type: "High foot traffic", safe: true },
            { name: "Powell Street", type: "Main thoroughfare", safe: true },
          ],
        },
        {
          id: 2,
          name: "Balanced Route",
          distance: "2.4 mi",
          time: "32 min",
          safetyScore: 88,
          crimeScore: 92,
          timeScore: 85,
          socialScore: 78,
          pedestrianScore: 88,
          color: "#3b82f6",
          coordinates: [
            { lat: 37.7749, lng: -122.4194 },
            { lat: 37.7759, lng: -122.4164 },
            { lat: 37.7779, lng: -122.4144 },
            { lat: 37.7799, lng: -122.4124 },
            { lat: 37.7819, lng: -122.4104 },
            { lat: 37.7849, lng: -122.4094 },
          ],
          waypoints: [
            { name: "Mission Street", type: "Moderate traffic", safe: true },
            { name: "5th Street", type: "Commercial area", safe: true },
            { name: "Howard Street", type: "Mixed use", safe: true },
          ],
        },
        {
          id: 3,
          name: "Fastest Route",
          distance: "2.1 mi",
          time: "28 min",
          safetyScore: 78,
          crimeScore: 82,
          timeScore: 75,
          socialScore: 68,
          pedestrianScore: 78,
          color: "#f59e0b",
          coordinates: [
            { lat: 37.7749, lng: -122.4194 },
            { lat: 37.7754, lng: -122.4154 },
            { lat: 37.7774, lng: -122.4134 },
            { lat: 37.7804, lng: -122.4114 },
            { lat: 37.7834, lng: -122.4104 },
            { lat: 37.7849, lng: -122.4094 },
          ],
          waypoints: [
            { name: "6th Street", type: "Direct route", safe: false },
            { name: "Folsom Street", type: "Less traffic", safe: true },
            { name: "Harrison Street", type: "Industrial area", safe: false },
          ],
        },
      ]
      setRoutes(generatedRoutes)
      setSelectedRouteId(1)
      setRouteCalculated(true)
    }
  }

  const selectedRoute = routes.find((r) => r.id === selectedRouteId)

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <Shield className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-foreground">SafePath</h1>
                <p className="text-xs text-muted-foreground">San Francisco</p>
              </div>
            </div>
            <Button variant="ghost" size="icon">
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left Column - Route Input & Details */}
          <div className="space-y-6 lg:col-span-1">
            {/* Route Input Card */}
            <Card className="p-6">
              <h2 className="mb-4 text-lg font-semibold text-card-foreground">Plan Your Route</h2>

              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-card-foreground">Starting Point</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Enter your location"
                      value={origin}
                      onChange={(e) => setOrigin(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-card-foreground">Destination</label>
                  <div className="relative">
                    <Navigation className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Where are you going?"
                      value={destination}
                      onChange={(e) => setDestination(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                <Button onClick={handleCalculateRoute} className="w-full" disabled={!origin || !destination}>
                  Find Safest Route
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </Card>

            {routeCalculated && routes.length > 0 && (
              <Card className="p-6">
                <h2 className="mb-4 text-lg font-semibold text-card-foreground">Route Options</h2>
                <div className="space-y-3">
                  {routes.map((route) => (
                    <button
                      key={route.id}
                      onClick={() => setSelectedRouteId(route.id)}
                      className={`w-full rounded-lg border p-4 text-left transition-all ${
                        selectedRouteId === route.id
                          ? "border-primary bg-primary/10"
                          : "border-border bg-card hover:border-primary/50"
                      }`}
                    >
                      <div className="mb-2 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="h-3 w-3 rounded-full" style={{ backgroundColor: route.color }} />
                          <h3 className="font-semibold text-card-foreground">{route.name}</h3>
                        </div>
                        <span
                          className={`text-sm font-semibold ${
                            route.safetyScore >= 90
                              ? "text-accent"
                              : route.safetyScore >= 80
                                ? "text-primary"
                                : "text-yellow-500"
                          }`}
                        >
                          {route.safetyScore}/100
                        </span>
                      </div>
                      <div className="flex gap-4 text-xs text-muted-foreground">
                        <span>{route.distance}</span>
                        <span>•</span>
                        <span>{route.time}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </Card>
            )}

            {/* Safety Factors */}
            {routeCalculated && selectedRoute && <SafetyFactors route={selectedRoute} />}

            {/* Route Details */}
            {routeCalculated && selectedRoute && <RouteDetails route={selectedRoute} />}
          </div>

          {/* Right Column - Map */}
          <div className="lg:col-span-2">
            <RouteMap
              routeCalculated={routeCalculated}
              origin={origin}
              destination={destination}
              routes={routes}
              selectedRouteId={selectedRouteId}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
