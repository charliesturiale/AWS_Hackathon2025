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
    <Card className="p-6 shadow-lg border-2 border-border/50 bg-white/90 backdrop-blur">
      <h2 className="mb-6 text-xl font-display font-bold text-foreground">Route Details</h2>

      {/* Quick Stats */}
      <div className="mb-6 grid grid-cols-3 gap-4">
        {details.map((detail) => {
          const Icon = detail.icon
          return (
            <div key={detail.label} className="text-center bg-gradient-to-br from-primary/5 to-accent/5 rounded-xl p-3 border border-border/30">
              <div className="mb-2 flex justify-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white shadow-sm">
                  <Icon className={`h-6 w-6 ${detail.color}`} />
                </div>
              </div>
              <p className="text-xs text-muted-foreground font-medium">{detail.label}</p>
              <p className="text-base font-bold text-foreground">{detail.value}</p>
            </div>
          )
        })}
      </div>

      {/* Waypoints */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-foreground mb-4">Key Waypoints</h3>
        {route.waypoints.map((waypoint, index) => (
          <div key={index} className="flex items-start gap-3 bg-gradient-to-r from-primary/5 to-transparent p-3 rounded-xl border border-border/30">
            <div className="flex h-8 w-8 items-center justify-center rounded-full gradient-primary shadow-sm">
              <MapPin className="h-4 w-4 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-bold text-foreground">{waypoint.name}</p>
              <p className="text-xs text-muted-foreground font-medium mt-0.5">{waypoint.type}</p>
            </div>
            <Badge variant="outline" className={`text-xs font-semibold border-2 ${waypoint.safe ? "border-accent/30 text-accent bg-accent/10" : "border-yellow-500/30 text-yellow-600 bg-yellow-500/10"}`}>
              {waypoint.safe ? "Safe" : "Caution"}
            </Badge>
          </div>
        ))}
      </div>
    </Card>
  )
}
