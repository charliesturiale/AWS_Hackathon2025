/**
 * Logistic Regression Model for Route Selection
 * Predicts the optimal route (safe vs fast) based on user features
 */

interface UserFeatures {
  // Demographic features
  age: number;                    // Normalized 0-1 (18-80 years)
  gender: 'male' | 'female' | 'other';
  mobilityScore: number;          // 0-1 (0=impaired, 1=fully mobile)
  
  // Contextual features
  timeOfDay: number;              // 0-24 hours
  dayOfWeek: number;              // 0-6 (0=Sunday)
  isRushing: boolean;             // User in a hurry
  weatherCondition: 'clear' | 'rain' | 'fog';
  
  // Historical preferences
  avgWalkingSpeed: number;        // km/h
  previousSafetyChoices: number;  // % of times chose safe route
  incidentHistory: number;        // Number of reported incidents
  
  // Environmental awareness
  familiarityWithArea: number;    // 0-1 (0=tourist, 1=local)
  groupSize: number;              // 1=alone, 2+=group
  carryingValuables: boolean;
}

interface RouteFeatures {
  safetyScore: number;            // 0-1
  distance: number;               // kilometers
  estimatedTime: number;          // minutes
  lightingQuality: number;        // 0-1
  crowdDensity: number;          // 0-1
  crimeRate24h: number;          // incidents per hour
  hillGradient: number;          // average % grade
  numIntersections: number;
  policePresence: number;        // 0-1
}

export class LogisticRouteModel {
  // Model weights (would be trained on real data)
  private weights = {
    // User feature weights
    age: -0.8,                    // Older users prefer safer routes
    genderFemale: -1.2,          // Female users prefer safer routes
    mobilityScore: 0.5,          // Higher mobility = more route options
    nightTime: -2.1,             // Night time strongly favors safe routes
    isRushing: 1.5,              // Rushing favors fast routes
    rainWeather: -0.9,           // Bad weather favors safe routes
    previousSafetyChoices: -1.8, // Historical preference for safety
    familiarityWithArea: 0.7,    // Locals more willing to take shortcuts
    alone: -1.3,                 // Being alone favors safe routes
    carryingValuables: -1.5,    // Valuables favor safe routes
    
    // Route feature weights  
    safetyScore: -3.2,           // High safety score favors this route
    timeDifference: 2.1,         // Large time difference favors fast
    distanceDifference: 1.8,     // Shorter distance favors fast
    lightingQuality: -1.4,       // Good lighting favors safe
    crowdDensity: -1.1,          // Crowds favor safe
    crimeRate: 2.5,              // High crime strongly avoids
    hillGradient: 0.9,           // Hills slightly favor fast route
    
    // Interaction terms
    ageNightTime: -1.5,         // Older + night = very safe
    femaleAlone: -1.8,           // Female + alone = very safe
    rushingFamiliarity: 1.2,    // Rushing + local = take shortcuts
    
    // Bias term
    bias: 0.3
  };

  /**
   * Sigmoid activation function
   */
  private sigmoid(z: number): number {
    return 1 / (1 + Math.exp(-z));
  }

  /**
   * Extract and normalize features from user and route data
   */
  private extractFeatures(
    user: UserFeatures,
    safeRoute: RouteFeatures,
    fastRoute: RouteFeatures
  ): number[] {
    const features: number[] = [];
    
    // User features
    features.push(user.age);
    features.push(user.gender === 'female' ? 1 : 0);
    features.push(user.mobilityScore);
    features.push(this.isNightTime(user.timeOfDay) ? 1 : 0);
    features.push(user.isRushing ? 1 : 0);
    features.push(user.weatherCondition === 'rain' ? 1 : 0);
    features.push(user.previousSafetyChoices);
    features.push(user.familiarityWithArea);
    features.push(user.groupSize === 1 ? 1 : 0);
    features.push(user.carryingValuables ? 1 : 0);
    
    // Route comparison features
    features.push(safeRoute.safetyScore - fastRoute.safetyScore);
    features.push((fastRoute.estimatedTime - safeRoute.estimatedTime) / 60); // Normalize to hours
    features.push((fastRoute.distance - safeRoute.distance));
    features.push(safeRoute.lightingQuality - fastRoute.lightingQuality);
    features.push(safeRoute.crowdDensity - fastRoute.crowdDensity);
    features.push(fastRoute.crimeRate24h - safeRoute.crimeRate24h);
    features.push(fastRoute.hillGradient - safeRoute.hillGradient);
    
    // Interaction features
    features.push(user.age * (this.isNightTime(user.timeOfDay) ? 1 : 0));
    features.push((user.gender === 'female' ? 1 : 0) * (user.groupSize === 1 ? 1 : 0));
    features.push((user.isRushing ? 1 : 0) * user.familiarityWithArea);
    
    return features;
  }

  /**
   * Calculate the linear combination of features and weights
   */
  private calculateZ(features: number[]): number {
    const weightArray = [
      this.weights.age,
      this.weights.genderFemale,
      this.weights.mobilityScore,
      this.weights.nightTime,
      this.weights.isRushing,
      this.weights.rainWeather,
      this.weights.previousSafetyChoices,
      this.weights.familiarityWithArea,
      this.weights.alone,
      this.weights.carryingValuables,
      this.weights.safetyScore,
      this.weights.timeDifference,
      this.weights.distanceDifference,
      this.weights.lightingQuality,
      this.weights.crowdDensity,
      this.weights.crimeRate,
      this.weights.hillGradient,
      this.weights.ageNightTime,
      this.weights.femaleAlone,
      this.weights.rushingFamiliarity
    ];
    
    let z = this.weights.bias;
    for (let i = 0; i < features.length; i++) {
      z += features[i] * weightArray[i];
    }
    
    return z;
  }

  /**
   * Predict the best route for a user
   * Returns probability of choosing the SAFE route
   */
  public predictRoute(
    user: UserFeatures,
    safeRoute: RouteFeatures,
    fastRoute: RouteFeatures
  ): {
    recommendedRoute: 'safe' | 'fast';
    safeRouteProbability: number;
    confidenceScore: number;
    reasoning: string[];
  } {
    // Extract features
    const features = this.extractFeatures(user, safeRoute, fastRoute);
    
    // Calculate linear combination
    const z = this.calculateZ(features);
    
    // Apply sigmoid to get probability
    const safeRouteProbability = this.sigmoid(z);
    
    // Determine recommendation
    const recommendedRoute = safeRouteProbability > 0.5 ? 'safe' : 'fast';
    const confidenceScore = Math.abs(safeRouteProbability - 0.5) * 2; // Scale to 0-1
    
    // Generate reasoning
    const reasoning = this.generateReasoning(user, safeRoute, fastRoute, features);
    
    return {
      recommendedRoute,
      safeRouteProbability,
      confidenceScore,
      reasoning
    };
  }

  /**
   * Generate human-readable reasoning for the recommendation
   */
  private generateReasoning(
    user: UserFeatures,
    safeRoute: RouteFeatures,
    fastRoute: RouteFeatures,
    features: number[]
  ): string[] {
    const reasons: string[] = [];
    
    // Time of day reasoning
    if (this.isNightTime(user.timeOfDay)) {
      reasons.push('It\'s nighttime - safety is prioritized');
    }
    
    // Gender and alone reasoning
    if (user.gender === 'female' && user.groupSize === 1) {
      reasons.push('Walking alone as a female - extra safety recommended');
    }
    
    // Weather reasoning
    if (user.weatherCondition === 'rain' || user.weatherCondition === 'fog') {
      reasons.push(`${user.weatherCondition} conditions - visibility reduced`);
    }
    
    // Time difference reasoning
    const timeDiff = fastRoute.estimatedTime - safeRoute.estimatedTime;
    if (timeDiff > 5) {
      reasons.push(`Safe route only adds ${timeDiff} minutes`);
    } else if (timeDiff < 2) {
      reasons.push('Minimal time difference between routes');
    }
    
    // Crime rate reasoning
    if (fastRoute.crimeRate24h > safeRoute.crimeRate24h * 2) {
      reasons.push('Fast route has significantly higher crime rate');
    }
    
    // Rushing reasoning
    if (user.isRushing && user.familiarityWithArea > 0.7) {
      reasons.push('You\'re rushing and familiar with the area');
    }
    
    // Age reasoning
    if (user.age > 0.7) { // Elderly
      reasons.push('Route optimized for comfortable walking pace');
    }
    
    // Mobility reasoning
    if (user.mobilityScore < 0.5) {
      reasons.push('Route selected for accessibility');
    }
    
    return reasons;
  }

  /**
   * Helper function to determine if it's nighttime
   */
  private isNightTime(hour: number): boolean {
    return hour < 6 || hour > 20;
  }

  /**
   * Update model weights based on user feedback (online learning)
   */
  public updateWeights(
    user: UserFeatures,
    safeRoute: RouteFeatures,
    fastRoute: RouteFeatures,
    actualChoice: 'safe' | 'fast',
    learningRate: number = 0.01
  ): void {
    const features = this.extractFeatures(user, safeRoute, fastRoute);
    const z = this.calculateZ(features);
    const prediction = this.sigmoid(z);
    
    // Calculate error
    const actual = actualChoice === 'safe' ? 1 : 0;
    const error = actual - prediction;
    
    // Update weights using gradient descent
    const weightKeys = Object.keys(this.weights) as Array<keyof typeof this.weights>;
    const weightArray = [
      'age', 'genderFemale', 'mobilityScore', 'nightTime', 'isRushing',
      'rainWeather', 'previousSafetyChoices', 'familiarityWithArea', 'alone',
      'carryingValuables', 'safetyScore', 'timeDifference', 'distanceDifference',
      'lightingQuality', 'crowdDensity', 'crimeRate', 'hillGradient',
      'ageNightTime', 'femaleAlone', 'rushingFamiliarity'
    ] as const;
    
    // Update feature weights
    for (let i = 0; i < features.length && i < weightArray.length; i++) {
      const key = weightArray[i];
      (this.weights as any)[key] += learningRate * error * features[i];
    }
    
    // Update bias
    this.weights.bias += learningRate * error;
  }

  /**
   * Get feature importance scores
   */
  public getFeatureImportance(): { feature: string; importance: number }[] {
    const importance = [
      { feature: 'Night Time', importance: Math.abs(this.weights.nightTime) },
      { feature: 'Crime Rate', importance: Math.abs(this.weights.crimeRate) },
      { feature: 'Safety Score', importance: Math.abs(this.weights.safetyScore) },
      { feature: 'Female Alone', importance: Math.abs(this.weights.femaleAlone) },
      { feature: 'Previous Safety Choices', importance: Math.abs(this.weights.previousSafetyChoices) },
      { feature: 'Carrying Valuables', importance: Math.abs(this.weights.carryingValuables) },
      { feature: 'Age at Night', importance: Math.abs(this.weights.ageNightTime) },
      { feature: 'Lighting Quality', importance: Math.abs(this.weights.lightingQuality) },
      { feature: 'Being Alone', importance: Math.abs(this.weights.alone) },
      { feature: 'Gender (Female)', importance: Math.abs(this.weights.genderFemale) },
    ];
    
    return importance.sort((a, b) => b.importance - a.importance);
  }
}

// Export singleton instance
export const routeModel = new LogisticRouteModel();