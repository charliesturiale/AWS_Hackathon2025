"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MapPin, Navigation, Shield, ChevronRight, Settings, Loader2, AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import RouteMap from "@/components/route-map"
import LocationInput from "@/components/location-input"
import { calculateRoutes, isGraphHopperConfigured } from "@/services/graphhopper"
import { saveLocation } from "@/services/savedLocations"
import { DebugEnv } from "@/components/debug-env"

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
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCalculateRoute = async () => {
    if (!origin || !destination) return

    // Log API configuration status
    console.log('GraphHopper configured:', isGraphHopperConfigured());
    if (!isGraphHopperConfigured()) {
      console.warn('GraphHopper API key not configured. Using fallback mock data.');
    }

    setLoading(true)
    setError(null)
    setRouteCalculated(false)

    try {
      const result = await calculateRoutes(origin, destination)

      if (!result) {
        throw new Error("Could not calculate routes. Please check your addresses and try again.")
      }

      setRoutes(result.routes)
      setSelectedRouteId(1)
      setRouteCalculated(true)

      // Save locations to localStorage for future use
      saveLocation(origin)
      saveLocation(destination)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred while calculating routes")
      console.error("Route calculation error:", err)
    } finally {
      setLoading(false)
    }
  }

  const selectedRoute = routes.find((r) => r.id === selectedRouteId)

  return (
    <div className="min-h-screen gradient-bg">
      {/* Header */}
      <header className="border-b border-border/50 bg-white/80 backdrop-blur-lg shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl gradient-primary shadow-glow">
                <Shield className="h-7 w-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-display font-bold text-gradient">SafePath</h1>
                <p className="text-xs text-muted-foreground font-medium">San Francisco, CA</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" className="hover:bg-primary/10">
              <Settings className="h-5 w-5 text-foreground/70" />
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {/* Top Section - Route Input/Options and Map */}
        <div className="grid gap-6 lg:grid-cols-3 mb-6">
          {/* Left Column - Route Input & Options */}
          <div className="space-y-6 lg:col-span-1">
            {/* Route Input Card */}
            <Card className="p-6 shadow-lg border-2 border-border/50 bg-white/90 backdrop-blur">
              <h2 className="mb-6 text-xl font-display font-bold text-foreground">Plan Your Route</h2>

              <div className="space-y-5">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-foreground">Starting Point</label>
                  <LocationInput
                    value={origin}
                    onChange={setOrigin}
                    placeholder="Enter your location"
                    icon={<MapPin className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-primary" />}
                    className="focus:border-primary focus:ring-2 focus:ring-primary/20"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-semibold text-foreground">Destination</label>
                  <LocationInput
                    value={destination}
                    onChange={setDestination}
                    placeholder="Where are you going?"
                    icon={<Navigation className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-accent" />}
                    className="focus:border-accent focus:ring-2 focus:ring-accent/20"
                  />
                </div>

                <Button
                  onClick={handleCalculateRoute}
                  className="w-full h-11 text-base font-semibold gradient-primary shadow-glow-hover transition-all"
                  disabled={!origin || !destination || loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Calculating Routes...
                    </>
                  ) : (
                    <>
                      Find Safest Route
                      <ChevronRight className="ml-2 h-5 w-5" />
                    </>
                  )}
                </Button>

                {/* Error Display */}
                {error && (
                  <Alert variant="destructive" className="mt-4">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
              </div>
            </Card>

            {routeCalculated && routes.length > 0 && (
              <Card className="p-6 shadow-lg border-2 border-border/50 bg-white/90 backdrop-blur">
                <h2 className="mb-5 text-xl font-display font-bold text-foreground">Route Options</h2>
                <div className="space-y-3">
                  {routes.map((route) => (
                    <button
                      key={route.id}
                      onClick={() => setSelectedRouteId(route.id)}
                      className={`w-full rounded-xl border-2 p-4 text-left transition-all duration-200 ${
                        selectedRouteId === route.id
                          ? "border-primary bg-primary/10 shadow-md scale-[1.02]"
                          : "border-border/50 bg-white hover:border-primary/50 hover:shadow-md"
                      }`}
                    >
                      <div className="mb-2 flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <div className="h-4 w-4 rounded-full shadow-sm" style={{ backgroundColor: route.color }} />
                          <h3 className="font-display font-bold text-foreground">{route.name}</h3>
                        </div>
                        <span
                          className={`text-sm font-bold px-2.5 py-1 rounded-lg ${
                            route.safetyScore >= 90
                              ? "bg-accent/15 text-accent"
                              : route.safetyScore >= 80
                                ? "bg-primary/15 text-primary"
                                : "bg-yellow-500/15 text-yellow-600"
                          }`}
                        >
                          {route.safetyScore}/100
                        </span>
                      </div>
                      <div className="flex gap-4 text-sm text-muted-foreground font-medium">
                        <span>{route.distance}</span>
                        <span>•</span>
                        <span>{route.time}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </Card>
            )}
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
      
      {/* Environment Debug Helper */}
      <DebugEnv />
    </div>
  )
}
