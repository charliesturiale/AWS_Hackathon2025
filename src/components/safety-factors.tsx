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
    <Card className="p-6 shadow-lg border-2 border-border/50 bg-white/90 backdrop-blur">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-display font-bold text-foreground">Safety Factors</h2>
        <Badge
          className={`px-3 py-1.5 font-semibold text-sm ${
            route.safetyScore >= 90
              ? "gradient-accent text-white"
              : route.safetyScore >= 80
                ? "gradient-primary text-white"
                : "bg-yellow-500 text-white"
          }`}
        >
          <CheckCircle2 className="mr-1.5 h-4 w-4" />
          {route.safetyScore >= 90 ? "Very Safe" : route.safetyScore >= 80 ? "Safe Route" : "Caution"}
        </Badge>
      </div>

      <div className="space-y-5">
        {factors.map((factor) => {
          const Icon = factor.icon
          return (
            <div key={factor.label} className="space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${factor.bgColor} shadow-sm`}>
                    <Icon className={`h-5 w-5 ${factor.color}`} />
                  </div>
                  <span className="text-sm font-bold text-foreground">{factor.label}</span>
                </div>
                <div className="flex items-center gap-2.5">
                  <span className="text-base font-bold text-foreground">{factor.score}%</span>
                  <Badge variant="outline" className="text-xs font-semibold border-2">
                    {factor.status}
                  </Badge>
                </div>
              </div>
              <Progress value={factor.score} className="h-2.5" />
            </div>
          )
        })}
      </div>
    </Card>
  )
}
