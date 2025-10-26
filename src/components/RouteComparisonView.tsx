import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { routeSafetyModel } from '../services/RouteOnlyLogisticModel';

export const RouteComparisonView: React.FC = () => {
  const [comparison, setComparison] = useState<any>(null);
  const [showDetails, setShowDetails] = useState(false);

  // Example routes through San Francisco
  const tenderloinRoute = {
    crimeIncidents24h: 8,
    historicalCrimeRate: 7.5,
    lightingScore: 0.3,
    footTraffic: 0.2,
    businessDensity: 5,
    visibilityScore: 0.7,
    sidewalkWidth: 2.5,
    distance: 0.9,
    estimatedTime: 12,
    numIntersections: 6,
    constructionZones: 2,
    distanceToPoliceStation: 0.8,
    emergencyCallBoxes: 1,
    surveillanceCameras: 3,
  };

  const marketStreetRoute = {
    crimeIncidents24h: 2,
    historicalCrimeRate: 3.5,
    lightingScore: 0.9,
    footTraffic: 0.8,
    businessDensity: 15,
    visibilityScore: 0.9,
    sidewalkWidth: 4,
    distance: 1.2,
    estimatedTime: 15,
    numIntersections: 8,
    constructionZones: 0,
    distanceToPoliceStation: 0.3,
    emergencyCallBoxes: 5,
    surveillanceCameras: 12,
  };

  const runComparison = () => {
    const result = routeSafetyModel.compareRoutes(tenderloinRoute, marketStreetRoute);
    setComparison(result);
  };

  const getRouteScoreDetails = (routeData: any) => {
    return routeSafetyModel.getRouteSafetyScore(routeData);
  };

  const getSafetyColor = (score: number) => {
    if (score >= 0.7) return '#4CAF50';
    if (score >= 0.5) return '#FFC107';
    if (score >= 0.3) return '#FF9800';
    return '#FF5252';
  };

  const getSafetyEmoji = (score: number) => {
    if (score >= 0.7) return '✅';
    if (score >= 0.5) return '⚠️';
    if (score >= 0.3) return '⚡';
    return '🚫';
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🤖 Objective Route Safety Analysis</Text>
        <Text style={styles.subtitle}>Logistic Regression Based on Crime & Environmental Data</Text>
      </View>

      {/* Route Options */}
      <View style={styles.routesSection}>
        <Text style={styles.sectionTitle}>Compare Two Routes</Text>
        
        <View style={styles.routeCard}>
          <Text style={styles.routeName}>Route A: Through Tenderloin</Text>
          <View style={styles.routeStats}>
            <Text style={styles.statText}>📍 0.9 km • ⏱️ 12 min</Text>
            <Text style={styles.statText}>🚨 8 recent crimes</Text>
            <Text style={styles.statText}>💡 Poor lighting (30%)</Text>
          </View>
        </View>

        <View style={styles.routeCard}>
          <Text style={styles.routeName}>Route B: Via Market Street</Text>
          <View style={styles.routeStats}>
            <Text style={styles.statText}>📍 1.2 km • ⏱️ 15 min</Text>
            <Text style={styles.statText}>🚨 2 recent crimes</Text>
            <Text style={styles.statText}>💡 Well lit (90%)</Text>
          </View>
        </View>
      </View>

      {/* Run Analysis Button */}
      <TouchableOpacity style={styles.analyzeButton} onPress={runComparison}>
        <Text style={styles.analyzeButtonText}>🔍 Analyze Safety with Logistic Regression</Text>
      </TouchableOpacity>

      {/* Results */}
      {comparison && (
        <View style={styles.resultsSection}>
          <Text style={styles.resultsTitle}>Analysis Results</Text>
          
          {/* Winner */}
          <View style={[styles.winnerCard, { 
            borderColor: comparison.recommendedRoute === 'A' ? '#FF5252' : '#4CAF50' 
          }]}>
            <Text style={styles.winnerText}>
              {comparison.recommendedRoute === 'B' ? '✅ RECOMMENDED' : '⚠️ NOT RECOMMENDED'}
            </Text>
            <Text style={styles.winnerRoute}>
              {comparison.recommendedRoute === 'A' ? 'Tenderloin Route' : 'Market Street Route'}
            </Text>
          </View>

          {/* Safety Scores */}
          <View style={styles.scoresContainer}>
            <View style={styles.scoreBox}>
              <Text style={styles.scoreLabel}>Tenderloin Route</Text>
              <View style={[styles.scoreCircle, { backgroundColor: getSafetyColor(comparison.routeASafetyScore) }]}>
                <Text style={styles.scoreText}>
                  {(comparison.routeASafetyScore * 100).toFixed(0)}%
                </Text>
              </View>
              <Text style={styles.scoreEmoji}>{getSafetyEmoji(comparison.routeASafetyScore)}</Text>
            </View>

            <View style={styles.vsText}>
              <Text style={styles.vs}>VS</Text>
            </View>

            <View style={styles.scoreBox}>
              <Text style={styles.scoreLabel}>Market Street</Text>
              <View style={[styles.scoreCircle, { backgroundColor: getSafetyColor(comparison.routeBSafetyScore) }]}>
                <Text style={styles.scoreText}>
                  {(comparison.routeBSafetyScore * 100).toFixed(0)}%
                </Text>
              </View>
              <Text style={styles.scoreEmoji}>{getSafetyEmoji(comparison.routeBSafetyScore)}</Text>
            </View>
          </View>

          {/* Reasoning */}
          <View style={styles.reasoningSection}>
            <Text style={styles.reasoningTitle}>Key Safety Factors:</Text>
            {comparison.reasoning.map((reason: string, index: number) => (
              <View key={index} style={styles.reasonItem}>
                <Text style={styles.bulletPoint}>•</Text>
                <Text style={styles.reasonText}>{reason}</Text>
              </View>
            ))}
          </View>

          {/* Feature Importance */}
          <TouchableOpacity 
            style={styles.detailsButton}
            onPress={() => setShowDetails(!showDetails)}
          >
            <Text style={styles.detailsButtonText}>
              {showDetails ? '📊 Hide Model Details' : '📊 Show Model Details'}
            </Text>
          </TouchableOpacity>

          {showDetails && (
            <View style={styles.detailsSection}>
              <Text style={styles.detailsTitle}>Feature Importance (Weights)</Text>
              {routeSafetyModel.getFeatureImportance().slice(0, 8).map((item, index) => (
                <View key={index} style={styles.featureRow}>
                  <Text style={styles.featureName}>{item.feature}</Text>
                  <View style={styles.featureBarContainer}>
                    <View 
                      style={[styles.featureBar, { 
                        width: `${(item.importance / 0.5) * 100}%`,
                        backgroundColor: index < 2 ? '#FF5252' : '#2196F3'
                      }]} 
                    />
                  </View>
                  <Text style={styles.featureValue}>{item.importance.toFixed(2)}</Text>
                </View>
              ))}
              
              <Text style={styles.formulaTitle}>Logistic Regression Formula:</Text>
              <View style={styles.formulaBox}>
                <Text style={styles.formulaText}>z = β₀ + Σ(βᵢ × xᵢ)</Text>
                <Text style={styles.formulaText}>P(safe) = 1 / (1 + e⁻ᶻ)</Text>
              </View>
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: 'white',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  routesSection: {
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  routeCard: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  routeName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  routeStats: {
    flexDirection: 'column',
  },
  statText: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  analyzeButton: {
    backgroundColor: '#2196F3',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  analyzeButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  resultsSection: {
    backgroundColor: 'white',
    margin: 15,
    padding: 15,
    borderRadius: 10,
  },
  resultsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  winnerCard: {
    padding: 15,
    borderRadius: 10,
    borderWidth: 3,
    marginBottom: 20,
    alignItems: 'center',
  },
  winnerText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  winnerRoute: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginTop: 5,
  },
  scoresContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    marginBottom: 20,
  },
  scoreBox: {
    alignItems: 'center',
    flex: 1,
  },
  scoreLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  scoreCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scoreText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  scoreEmoji: {
    fontSize: 24,
    marginTop: 10,
  },
  vsText: {
    paddingHorizontal: 20,
  },
  vs: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#999',
  },
  reasoningSection: {
    backgroundColor: '#f9f9f9',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
  },
  reasoningTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
    color: '#333',
  },
  reasonItem: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  bulletPoint: {
    fontSize: 14,
    color: '#666',
    marginRight: 8,
  },
  reasonText: {
    fontSize: 14,
    color: '#666',
    flex: 1,
  },
  detailsButton: {
    backgroundColor: '#f0f0f0',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  detailsButtonText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  detailsSection: {
    marginTop: 15,
    paddingTop: 15,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  detailsTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 15,
    color: '#333',
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  featureName: {
    flex: 3,
    fontSize: 12,
    color: '#666',
  },
  featureBarContainer: {
    flex: 2,
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    marginHorizontal: 10,
  },
  featureBar: {
    height: '100%',
    borderRadius: 4,
  },
  featureValue: {
    width: 40,
    fontSize: 12,
    color: '#999',
    textAlign: 'right',
  },
  formulaTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginTop: 20,
    marginBottom: 10,
    color: '#333',
  },
  formulaBox: {
    backgroundColor: '#f5f5f5',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  formulaText: {
    fontSize: 14,
    fontFamily: 'monospace',
    color: '#333',
    marginVertical: 3,
  },
});