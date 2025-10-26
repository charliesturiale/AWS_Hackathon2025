"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Shield, Clock, Users, CheckCircle2, Construction } from "lucide-react"
import type { Route } from "./safe-path-app"

interface SafetyFactorsProps {
  route: Route
}

export default function SafetyFactors({ route }: SafetyFactorsProps) {
  const factors = [
    {
      icon: Shield,
      label: "Crime Safety",
      score: route.crimeScore,
      status: route.crimeScore >= 90 ? "Excellent" : route.crimeScore >= 80 ? "Good" : "Fair",
      color: "text-accent",
      bgColor: "bg-accent/10",
    },
    {
      icon: Clock,
      label: "Time of Day",
      score: route.timeScore,
      status: route.timeScore >= 90 ? "Excellent" : route.timeScore >= 80 ? "Good" : "Fair",
      color: "text-primary",
      bgColor: "bg-primary/10",
    },
    {
      icon: Construction,
      label: "Social Obstructions",
      score: route.socialScore,
      status: route.socialScore >= 90 ? "Excellent" : route.socialScore >= 80 ? "Good" : "Fair",
      color: "text-primary",
      bgColor: "bg-primary/10",
    },
    {
      icon: Users,
      label: "Pedestrian Score",
      score: route.pedestrianScore,
      status: route.pedestrianScore >= 90 ? "Excellent" : route.pedestrianScore >= 80 ? "Good" : "Fair",
      color: "text-accent",
      bgColor: "bg-accent/10",
    },
  ]

  return (
    <Card className="p-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-card-foreground">Safety Factors</h2>
        <Badge
          className={
            route.safetyScore >= 90
              ? "bg-accent text-accent-foreground"
              : route.safetyScore >= 80
                ? "bg-primary text-primary-foreground"
                : "bg-yellow-500 text-white"
          }
        >
          <CheckCircle2 className="mr-1 h-3 w-3" />
          {route.safetyScore >= 90 ? "Very Safe" : route.safetyScore >= 80 ? "Safe Route" : "Caution"}
        </Badge>
      </div>

      <div className="space-y-4">
        {factors.map((factor) => {
          const Icon = factor.icon
          return (
            <div key={factor.label} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${factor.bgColor}`}>
                    <Icon className={`h-4 w-4 ${factor.color}`} />
                  </div>
                  <span className="text-sm font-medium text-card-foreground">{factor.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-card-foreground">{factor.score}%</span>
                  <Badge variant="outline" className="text-xs">
                    {factor.status}
                  </Badge>
                </div>
              </div>
              <Progress value={factor.score} className="h-2" />
            </div>
          )
        })}
      </div>
    </Card>
  )
}
