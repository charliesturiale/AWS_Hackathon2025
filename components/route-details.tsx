"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Clock, Navigation, TrendingUp, MapPin } from "lucide-react"
import type { Route } from "./safe-path-app"

interface RouteDetailsProps {
  route: Route
}

export default function RouteDetails({ route }: RouteDetailsProps) {
  const details = [
    {
      icon: Navigation,
      label: "Distance",
      value: route.distance,
      color: "text-primary",
    },
    {
      icon: Clock,
      label: "Est. Time",
      value: route.time,
      color: "text-primary",
    },
    {
      icon: TrendingUp,
      label: "Safety Score",
      value: `${route.safetyScore}/100`,
      color: "text-accent",
    },
  ]

  return (
    <Card className="p-6">
      <h2 className="mb-4 text-lg font-semibold text-card-foreground">Route Details</h2>

      {/* Quick Stats */}
      <div className="mb-6 grid grid-cols-3 gap-4">
        {details.map((detail) => {
          const Icon = detail.icon
          return (
            <div key={detail.label} className="text-center">
              <div className="mb-2 flex justify-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                  <Icon className={`h-5 w-5 ${detail.color}`} />
                </div>
              </div>
              <p className="text-xs text-muted-foreground">{detail.label}</p>
              <p className="text-sm font-semibold text-card-foreground">{detail.value}</p>
            </div>
          )
        })}
      </div>

      {/* Waypoints */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-card-foreground">Key Waypoints</h3>
        {route.waypoints.map((waypoint, index) => (
          <div key={index} className="flex items-start gap-3">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-muted">
              <MapPin className="h-3 w-3 text-muted-foreground" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-card-foreground">{waypoint.name}</p>
              <p className="text-xs text-muted-foreground">{waypoint.type}</p>
            </div>
            <Badge variant="outline" className={`text-xs ${waypoint.safe ? "text-accent" : "text-yellow-500"}`}>
              {waypoint.safe ? "Safe" : "Caution"}
            </Badge>
          </div>
        ))}
      </div>
    </Card>
  )
}
