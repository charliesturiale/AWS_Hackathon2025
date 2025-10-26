import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, ScrollView } from 'react-native';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

interface PathRiskResult {
  index: number;
  risk_score: number;
  crime_risk: number;
  '311_risk': number;
}

interface SafePathAnalysisProps {
  paths?: number[][][];  // Array of paths, each path is array of [lat, lon] points
  onPathSelect?: (pathIndex: number) => void;
}

export const SafePathAnalysis: React.FC<SafePathAnalysisProps> = ({ 
  paths = [], 
  onPathSelect 
}) => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<PathRiskResult[]>([]);
  const [safestPaths, setSafestPaths] = useState<PathRiskResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Sample paths for SF (if no paths provided)
  const samplePaths = [
    // Path 1: Through Financial District
    [[37.7849, -122.4094], [37.7855, -122.4086], [37.7861, -122.4078]],
    // Path 2: Through SOMA
    [[37.7849, -122.4094], [37.7845, -122.4102], [37.7841, -122.4110]],
    // Path 3: Through Union Square area
    [[37.7849, -122.4094], [37.7852, -122.4090], [37.7855, -122.4086]],
    // Path 4: Through Tenderloin edge
    [[37.7849, -122.4094], [37.7840, -122.4120], [37.7835, -122.4130]],
    // Path 5: Through safer downtown route
    [[37.7849, -122.4094], [37.7860, -122.4080], [37.7870, -122.4070]]
  ];

  const analyzePaths = async () => {
    setLoading(true);
    setError(null);
    
    const pathsToAnalyze = paths.length > 0 ? paths : samplePaths;
    
    try {
      const response = await fetch(`${API_URL}/analyze-paths`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ paths: pathsToAnalyze }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze paths');
      }

      const data = await response.json();
      
      if (data.success) {
        setResults(data.all_paths);
        setSafestPaths(data.safest_paths);
      } else {
        throw new Error(data.error || 'Analysis failed');
      }
    } catch (err) {
      console.error('Error analyzing paths:', err);
      setError(err instanceof Error ? err.message : 'Failed to analyze paths');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (paths.length > 0 || results.length === 0) {
      analyzePaths();
    }
  }, [paths]);

  const getRiskLevel = (score: number): { text: string; color: string } => {
    if (score < 5) return { text: 'Very Safe', color: '#4CAF50' };
    if (score < 10) return { text: 'Safe', color: '#8BC34A' };
    if (score < 20) return { text: 'Moderate', color: '#FFC107' };
    if (score < 30) return { text: 'Caution', color: '#FF9800' };
    return { text: 'High Risk', color: '#F44336' };
  };

  const formatRiskScore = (score: number): string => {
    return score.toFixed(2);
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Analyzing path safety...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>⚠️ {error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={analyzePaths}>
          <Text style={styles.retryButtonText}>Retry Analysis</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🛡️ SafePath Analysis</Text>
        <Text style={styles.subtitle}>Real-time risk assessment using SF Open Data</Text>
      </View>

      {safestPaths.length > 0 && (
        <View style={styles.safestSection}>
          <Text style={styles.sectionTitle}>🏆 Top 3 Safest Routes</Text>
          {safestPaths.map((path, idx) => {
            const riskLevel = getRiskLevel(path.risk_score);
            return (
              <TouchableOpacity
                key={path.index}
                style={[styles.pathCard, styles.safestCard]}
                onPress={() => onPathSelect?.(path.index)}
              >
                <View style={styles.pathHeader}>
                  <Text style={styles.pathTitle}>
                    {idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉'} Route {path.index + 1}
                  </Text>
                  <View style={[styles.riskBadge, { backgroundColor: riskLevel.color }]}>
                    <Text style={styles.riskBadgeText}>{riskLevel.text}</Text>
                  </View>
                </View>
                <View style={styles.scoreContainer}>
                  <View style={styles.scoreItem}>
                    <Text style={styles.scoreLabel}>Total Risk:</Text>
                    <Text style={[styles.scoreValue, { color: riskLevel.color }]}>
                      {formatRiskScore(path.risk_score)}
                    </Text>
                  </View>
                  <View style={styles.scoreItem}>
                    <Text style={styles.scoreLabel}>Crime Risk:</Text>
                    <Text style={styles.scoreValue}>{formatRiskScore(path.crime_risk)}</Text>
                  </View>
                  <View style={styles.scoreItem}>
                    <Text style={styles.scoreLabel}>311 Risk:</Text>
                    <Text style={styles.scoreValue}>{formatRiskScore(path['311_risk'])}</Text>
                  </View>
                </View>
              </TouchableOpacity>
            );
          })}
        </View>
      )}

      {results.length > 0 && (
        <View style={styles.allSection}>
          <Text style={styles.sectionTitle}>📊 All Routes Analysis</Text>
          {results.map((path) => {
            const riskLevel = getRiskLevel(path.risk_score);
            const isSafest = safestPaths.some(sp => sp.index === path.index);
            
            return (
              <TouchableOpacity
                key={path.index}
                style={[
                  styles.pathCard,
                  isSafest && styles.highlightedCard
                ]}
                onPress={() => onPathSelect?.(path.index)}
              >
                <View style={styles.pathHeader}>
                  <Text style={styles.pathTitle}>
                    Route {path.index + 1} {isSafest && '⭐'}
                  </Text>
                  <View style={[styles.riskBadge, { backgroundColor: riskLevel.color }]}>
                    <Text style={styles.riskBadgeText}>{riskLevel.text}</Text>
                  </View>
                </View>
                <View style={styles.scoreContainer}>
                  <View style={styles.scoreItem}>
                    <Text style={styles.scoreLabel}>Total:</Text>
                    <Text style={[styles.scoreValue, { color: riskLevel.color }]}>
                      {formatRiskScore(path.risk_score)}
                    </Text>
                  </View>
                  <View style={styles.scoreItem}>
                    <Text style={styles.scoreLabel}>Crime:</Text>
                    <Text style={styles.scoreValue}>{formatRiskScore(path.crime_risk)}</Text>
                  </View>
                  <View style={styles.scoreItem}>
                    <Text style={styles.scoreLabel}>311:</Text>
                    <Text style={styles.scoreValue}>{formatRiskScore(path['311_risk'])}</Text>
                  </View>
                </View>
                <View style={styles.riskBar}>
                  <View 
                    style={[
                      styles.riskBarFill, 
                      { 
                        width: `${Math.min(path.risk_score * 2, 100)}%`,
                        backgroundColor: riskLevel.color 
                      }
                    ]} 
                  />
                </View>
              </TouchableOpacity>
            );
          })}
        </View>
      )}

      <TouchableOpacity style={styles.refreshButton} onPress={analyzePaths}>
        <Text style={styles.refreshButtonText}>🔄 Refresh Analysis</Text>
      </TouchableOpacity>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Powered by SF Open Data • Crime & 311 Reports
        </Text>
        <Text style={styles.footerText}>
          Using time-decay risk algorithm (high-risk: 72hr, low-risk: 24hr)
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  header: {
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#F44336',
    marginBottom: 15,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  safestSection: {
    padding: 15,
  },
  allSection: {
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  pathCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 15,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  safestCard: {
    borderWidth: 2,
    borderColor: '#4CAF50',
  },
  highlightedCard: {
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  pathHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  pathTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  riskBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  riskBadgeText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  scoreContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  scoreItem: {
    flex: 1,
  },
  scoreLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  scoreValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  riskBar: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    overflow: 'hidden',
  },
  riskBarFill: {
    height: '100%',
    borderRadius: 2,
  },
  refreshButton: {
    backgroundColor: '#007AFF',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  refreshButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    marginBottom: 5,
  },
});

export default SafePathAnalysis;