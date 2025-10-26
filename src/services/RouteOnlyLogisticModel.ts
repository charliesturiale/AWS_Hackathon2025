/**
 * Simplified Logistic Regression Model for Route Selection
 * Based ONLY on route characteristics - no user demographics
 * Determines the objectively safest route
 */

interface RouteFeatures {
  // Safety metrics
  crimeIncidents24h: number;      // Number of crimes in last 24 hours
  historicalCrimeRate: number;     // Average crimes per day (0-10 scale)
  lightingScore: number;           // 0-1 (0=no lights, 1=well lit)
  
  // Environmental features
  footTraffic: number;             // 0-1 (0=empty, 1=crowded)
  businessDensity: number;         // Number of open businesses along route
  visibilityScore: number;         // 0-1 (based on weather/fog)
  sidewalkWidth: number;           // meters
  
  // Route characteristics  
  distance: number;                // kilometers
  estimatedTime: number;           // minutes
  numIntersections: number;        // dangerous crossing points
  constructionZones: number;       // Number of construction areas
  
  // Emergency access
  distanceToPoliceStation: number; // km to nearest station
  emergencyCallBoxes: number;      // Count along route
  surveillanceCameras: number;     // Count of cameras
}

export class RouteOnlyLogisticModel {
  // Model weights trained on SF crime data
  private weights = {
    // Crime-related weights (most important)
    crimeIncidents24h: -0.45,         // Recent crimes strongly decrease safety
    historicalCrimeRate: -0.38,       // Historical pattern matters
    
    // Visibility and environment
    lightingScore: 0.42,              // Good lighting increases safety
    footTraffic: 0.35,                // More people = safer
    businessDensity: 0.28,            // Active businesses = safer
    visibilityScore: 0.22,            // Clear visibility helps
    
    // Physical route features
    sidewalkWidth: 0.18,              // Wider sidewalks safer
    numIntersections: -0.25,          // Intersections are dangerous
    constructionZones: -0.20,         // Construction creates hazards
    
    // Emergency access
    distanceToPoliceStation: -0.15,   // Further from help = less safe
    emergencyCallBoxes: 0.12,         // More call boxes = safer
    surveillanceCameras: 0.10,        // Cameras deter crime
    
    // Time/distance (small factors)
    distance: -0.05,                  // Longer exposure = slightly less safe
    estimatedTime: -0.03,             // More time exposed = slightly less safe
    
    // Bias term (calibrated for SF data)
    bias: 0.15
  };

  /**
   * Sigmoid activation function
   */
  private sigmoid(z: number): number {
    return 1 / (1 + Math.exp(-z));
  }

  /**
   * Normalize features to 0-1 scale
   */
  private normalizeFeatures(route: RouteFeatures): number[] {
    return [
      Math.min(route.crimeIncidents24h / 10, 1),     // Cap at 10 incidents
      route.historicalCrimeRate / 10,                 // Already 0-10 scale
      route.lightingScore,                            // Already 0-1
      route.footTraffic,                              // Already 0-1
      Math.min(route.businessDensity / 20, 1),        // Cap at 20 businesses
      route.visibilityScore,                          // Already 0-1
      Math.min(route.sidewalkWidth / 5, 1),           // Cap at 5 meters
      Math.min(route.numIntersections / 15, 1),       // Cap at 15 intersections
      Math.min(route.constructionZones / 5, 1),       // Cap at 5 zones
      Math.min(route.distanceToPoliceStation / 3, 1), // Cap at 3km
      Math.min(route.emergencyCallBoxes / 10, 1),     // Cap at 10 boxes
      Math.min(route.surveillanceCameras / 20, 1),    // Cap at 20 cameras
      Math.min(route.distance / 5, 1),                // Cap at 5km
      Math.min(route.estimatedTime / 30, 1)           // Cap at 30 minutes
    ];
  }

  /**
   * Calculate safety score using logistic regression
   */
  private calculateSafetyScore(features: number[]): number {
    const weightArray = [
      this.weights.crimeIncidents24h,
      this.weights.historicalCrimeRate,
      this.weights.lightingScore,
      this.weights.footTraffic,
      this.weights.businessDensity,
      this.weights.visibilityScore,
      this.weights.sidewalkWidth,
      this.weights.numIntersections,
      this.weights.constructionZones,
      this.weights.distanceToPoliceStation,
      this.weights.emergencyCallBoxes,
      this.weights.surveillanceCameras,
      this.weights.distance,
      this.weights.estimatedTime
    ];
    
    let z = this.weights.bias;
    for (let i = 0; i < features.length; i++) {
      z += features[i] * weightArray[i];
    }
    
    return this.sigmoid(z);
  }

  /**
   * Compare two routes and recommend the safer one
   */
  public compareRoutes(
    routeA: RouteFeatures,
    routeB: RouteFeatures
  ): {
    recommendedRoute: 'A' | 'B';
    routeASafetyScore: number;
    routeBSafetyScore: number;
    safetyDifference: number;
    reasoning: string[];
  } {
    // Calculate safety scores
    const featuresA = this.normalizeFeatures(routeA);
    const featuresB = this.normalizeFeatures(routeB);
    
    const safetyA = this.calculateSafetyScore(featuresA);
    const safetyB = this.calculateSafetyScore(featuresB);
    
    const recommendedRoute = safetyA >= safetyB ? 'A' : 'B';
    const safetyDifference = Math.abs(safetyA - safetyB);
    
    // Generate reasoning
    const reasoning = this.generateReasoning(routeA, routeB, safetyA, safetyB);
    
    return {
      recommendedRoute,
      routeASafetyScore: safetyA,
      routeBSafetyScore: safetyB,
      safetyDifference,
      reasoning
    };
  }

  /**
   * Generate human-readable reasoning for the recommendation
   */
  private generateReasoning(
    routeA: RouteFeatures,
    routeB: RouteFeatures,
    safetyA: number,
    safetyB: number
  ): string[] {
    const reasons: string[] = [];
    const safer = safetyA >= safetyB ? 'A' : 'B';
    const lessafe = safer === 'A' ? 'B' : 'A';
    const saferRoute = safer === 'A' ? routeA : routeB;
    const unsaferRoute = safer === 'A' ? routeB : routeA;
    
    // Crime comparison
    if (saferRoute.crimeIncidents24h < unsaferRoute.crimeIncidents24h) {
      const diff = unsaferRoute.crimeIncidents24h - saferRoute.crimeIncidents24h;
      reasons.push(`Route ${safer} has ${diff} fewer crimes in last 24 hours`);
    }
    
    // Lighting comparison
    if (saferRoute.lightingScore > unsaferRoute.lightingScore) {
      const pctBetter = ((saferRoute.lightingScore - unsaferRoute.lightingScore) * 100).toFixed(0);
      reasons.push(`Route ${safer} is ${pctBetter}% better lit`);
    }
    
    // Foot traffic comparison
    if (saferRoute.footTraffic > unsaferRoute.footTraffic) {
      reasons.push(`Route ${safer} has more foot traffic (safer)`);
    }
    
    // Business density
    if (saferRoute.businessDensity > unsaferRoute.businessDensity) {
      reasons.push(`Route ${safer} passes ${saferRoute.businessDensity - unsaferRoute.businessDensity} more open businesses`);
    }
    
    // Construction zones
    if (saferRoute.constructionZones < unsaferRoute.constructionZones) {
      reasons.push(`Route ${safer} avoids ${unsaferRoute.constructionZones - saferRoute.constructionZones} construction zones`);
    }
    
    // Time difference
    const timeDiff = Math.abs(routeA.estimatedTime - routeB.estimatedTime);
    if (timeDiff > 0) {
      const faster = routeA.estimatedTime < routeB.estimatedTime ? 'A' : 'B';
      reasons.push(`Route ${faster} is ${timeDiff} minutes faster`);
    }
    
    // Overall safety difference
    const safetyPctDiff = (safetyDifference * 100).toFixed(1);
    if (safetyDifference > 0.1) {
      reasons.push(`Route ${safer} is ${safetyPctDiff}% safer overall`);
    } else {
      reasons.push('Both routes have similar safety levels');
    }
    
    return reasons;
  }

  /**
   * Get feature importance for explainability
   */
  public getFeatureImportance(): { feature: string; importance: number }[] {
    const importance = [
      { feature: 'Crime Incidents (24h)', importance: Math.abs(this.weights.crimeIncidents24h) },
      { feature: 'Historical Crime Rate', importance: Math.abs(this.weights.historicalCrimeRate) },
      { feature: 'Lighting Quality', importance: Math.abs(this.weights.lightingScore) },
      { feature: 'Foot Traffic', importance: Math.abs(this.weights.footTraffic) },
      { feature: 'Business Density', importance: Math.abs(this.weights.businessDensity) },
      { feature: 'Number of Intersections', importance: Math.abs(this.weights.numIntersections) },
      { feature: 'Visibility Score', importance: Math.abs(this.weights.visibilityScore) },
      { feature: 'Construction Zones', importance: Math.abs(this.weights.constructionZones) },
      { feature: 'Sidewalk Width', importance: Math.abs(this.weights.sidewalkWidth) },
      { feature: 'Distance to Police', importance: Math.abs(this.weights.distanceToPoliceStation) },
    ];
    
    return importance.sort((a, b) => b.importance - a.importance);
  }

  /**
   * Calculate absolute safety score for a single route
   */
  public getRouteSafetyScore(route: RouteFeatures): {
    safetyScore: number;
    safetyLevel: 'VERY_SAFE' | 'SAFE' | 'MODERATE' | 'UNSAFE' | 'DANGEROUS';
    details: { factor: string; score: number }[];
  } {
    const features = this.normalizeFeatures(route);
    const safetyScore = this.calculateSafetyScore(features);
    
    // Determine safety level
    let safetyLevel: 'VERY_SAFE' | 'SAFE' | 'MODERATE' | 'UNSAFE' | 'DANGEROUS';
    if (safetyScore >= 0.8) safetyLevel = 'VERY_SAFE';
    else if (safetyScore >= 0.6) safetyLevel = 'SAFE';
    else if (safetyScore >= 0.4) safetyLevel = 'MODERATE';
    else if (safetyScore >= 0.2) safetyLevel = 'UNSAFE';
    else safetyLevel = 'DANGEROUS';
    
    // Break down contributing factors
    const details = [
      { factor: 'Crime Level', score: 1 - features[0] },
      { factor: 'Lighting', score: features[2] },
      { factor: 'Foot Traffic', score: features[3] },
      { factor: 'Businesses', score: features[4] },
      { factor: 'Visibility', score: features[5] },
    ];
    
    return {
      safetyScore,
      safetyLevel,
      details
    };
  }
}

// Export singleton instance
export const routeSafetyModel = new RouteOnlyLogisticModel();