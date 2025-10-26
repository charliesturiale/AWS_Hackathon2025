import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { routeModel } from '../services/LogisticRouteModel';

export const SmartRouteSelector: React.FC = () => {
  const [userProfile, setUserProfile] = useState({
    age: 0.4,           // 40 years old (normalized)
    gender: 'female' as 'female' | 'male' | 'other',
    mobilityScore: 1.0,
    timeOfDay: new Date().getHours(),
    dayOfWeek: new Date().getDay(),
    isRushing: false,
    weatherCondition: 'clear' as 'clear' | 'rain' | 'fog',
    avgWalkingSpeed: 4.5,
    previousSafetyChoices: 0.7,
    incidentHistory: 0,
    familiarityWithArea: 0.5,
    groupSize: 1,
    carryingValuables: false,
  });

  const [prediction, setPrediction] = useState<any>(null);

  // Mock route data for demonstration
  const safeRoute = {
    safetyScore: 0.85,
    distance: 1.2,
    estimatedTime: 15,
    lightingQuality: 0.9,
    crowdDensity: 0.7,
    crimeRate24h: 0.1,
    hillGradient: 5,
    numIntersections: 8,
    policePresence: 0.6,
  };

  const fastRoute = {
    safetyScore: 0.45,
    distance: 0.9,
    estimatedTime: 12,
    lightingQuality: 0.4,
    crowdDensity: 0.3,
    crimeRate24h: 0.8,
    hillGradient: 8,
    numIntersections: 5,
    policePresence: 0.2,
  };

  const runPrediction = () => {
    const result = routeModel.predictRoute(userProfile, safeRoute, fastRoute);
    setPrediction(result);
  };

  const toggleGender = () => {
    setUserProfile(prev => ({
      ...prev,
      gender: prev.gender === 'female' ? 'male' : 'female'
    }));
  };

  const toggleRushing = () => {
    setUserProfile(prev => ({
      ...prev,
      isRushing: !prev.isRushing
    }));
  };

  const toggleAlone = () => {
    setUserProfile(prev => ({
      ...prev,
      groupSize: prev.groupSize === 1 ? 2 : 1
    }));
  };

  const toggleValuables = () => {
    setUserProfile(prev => ({
      ...prev,
      carryingValuables: !prev.carryingValuables
    }));
  };

  const setTimeOfDay = (hour: number) => {
    setUserProfile(prev => ({
      ...prev,
      timeOfDay: hour
    }));
  };

  const setWeather = (weather: 'clear' | 'rain' | 'fog') => {
    setUserProfile(prev => ({
      ...prev,
      weatherCondition: weather
    }));
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🤖 AI Route Selection</Text>
        <Text style={styles.subtitle}>Logistic Regression Model</Text>
      </View>

      {/* User Profile Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>User Profile</Text>
        
        <View style={styles.settingRow}>
          <Text>Gender:</Text>
          <TouchableOpacity style={styles.button} onPress={toggleGender}>
            <Text style={styles.buttonText}>{userProfile.gender}</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.settingRow}>
          <Text>Walking Alone:</Text>
          <TouchableOpacity style={styles.button} onPress={toggleAlone}>
            <Text style={styles.buttonText}>{userProfile.groupSize === 1 ? 'Yes' : 'No'}</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.settingRow}>
          <Text>In a Rush:</Text>
          <TouchableOpacity style={styles.button} onPress={toggleRushing}>
            <Text style={styles.buttonText}>{userProfile.isRushing ? 'Yes' : 'No'}</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.settingRow}>
          <Text>Carrying Valuables:</Text>
          <TouchableOpacity style={styles.button} onPress={toggleValuables}>
            <Text style={styles.buttonText}>{userProfile.carryingValuables ? 'Yes' : 'No'}</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Environmental Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Environment</Text>
        
        <View style={styles.settingRow}>
          <Text>Time:</Text>
          <View style={styles.buttonGroup}>
            <TouchableOpacity 
              style={[styles.smallButton, userProfile.timeOfDay === 14 && styles.activeButton]} 
              onPress={() => setTimeOfDay(14)}
            >
              <Text style={styles.buttonText}>2 PM</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.smallButton, userProfile.timeOfDay === 22 && styles.activeButton]} 
              onPress={() => setTimeOfDay(22)}
            >
              <Text style={styles.buttonText}>10 PM</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.smallButton, userProfile.timeOfDay === 2 && styles.activeButton]} 
              onPress={() => setTimeOfDay(2)}
            >
              <Text style={styles.buttonText}>2 AM</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.settingRow}>
          <Text>Weather:</Text>
          <View style={styles.buttonGroup}>
            <TouchableOpacity 
              style={[styles.smallButton, userProfile.weatherCondition === 'clear' && styles.activeButton]} 
              onPress={() => setWeather('clear')}
            >
              <Text style={styles.buttonText}>☀️</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.smallButton, userProfile.weatherCondition === 'rain' && styles.activeButton]} 
              onPress={() => setWeather('rain')}
            >
              <Text style={styles.buttonText}>🌧️</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.smallButton, userProfile.weatherCondition === 'fog' && styles.activeButton]} 
              onPress={() => setWeather('fog')}
            >
              <Text style={styles.buttonText}>🌫️</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* Run Prediction Button */}
      <TouchableOpacity style={styles.predictButton} onPress={runPrediction}>
        <Text style={styles.predictButtonText}>🔮 Run Logistic Regression</Text>
      </TouchableOpacity>

      {/* Prediction Results */}
      {prediction && (
        <View style={styles.resultSection}>
          <Text style={styles.resultTitle}>Prediction Results</Text>
          
          <View style={[styles.recommendationBox, 
            prediction.recommendedRoute === 'safe' ? styles.safeBox : styles.fastBox]}>
            <Text style={styles.recommendationText}>
              {prediction.recommendedRoute === 'safe' ? '🛡️ SAFE ROUTE' : '⚡ FAST ROUTE'}
            </Text>
            <Text style={styles.probabilityText}>
              Probability: {(prediction.safeRouteProbability * 100).toFixed(1)}% for safe route
            </Text>
            <Text style={styles.confidenceText}>
              Confidence: {(prediction.confidenceScore * 100).toFixed(0)}%
            </Text>
          </View>

          <View style={styles.reasoningBox}>
            <Text style={styles.reasoningTitle}>AI Reasoning:</Text>
            {prediction.reasoning.map((reason: string, index: number) => (
              <Text key={index} style={styles.reasonText}>• {reason}</Text>
            ))}
          </View>

          {/* Feature Importance */}
          <View style={styles.featureBox}>
            <Text style={styles.featureTitle}>Top Factors in Decision:</Text>
            {routeModel.getFeatureImportance().slice(0, 5).map((item, index) => (
              <View key={index} style={styles.featureRow}>
                <Text style={styles.featureText}>{item.feature}</Text>
                <View style={styles.featureBar}>
                  <View style={[styles.featureBarFill, 
                    { width: `${(item.importance / 3.5) * 100}%` }]} />
                </View>
              </View>
            ))}
          </View>
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
  section: {
    backgroundColor: 'white',
    padding: 15,
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 15,
  },
  buttonText: {
    color: 'white',
    fontWeight: '600',
  },
  buttonGroup: {
    flexDirection: 'row',
    gap: 5,
  },
  smallButton: {
    backgroundColor: '#e0e0e0',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 15,
  },
  activeButton: {
    backgroundColor: '#007AFF',
  },
  predictButton: {
    backgroundColor: '#4CAF50',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  predictButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  resultSection: {
    backgroundColor: 'white',
    margin: 15,
    padding: 15,
    borderRadius: 10,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  recommendationBox: {
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
  },
  safeBox: {
    backgroundColor: '#E8F5E9',
    borderColor: '#4CAF50',
    borderWidth: 2,
  },
  fastBox: {
    backgroundColor: '#FFF8E1',
    borderColor: '#FFC107',
    borderWidth: 2,
  },
  recommendationText: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  probabilityText: {
    fontSize: 14,
    marginTop: 5,
  },
  confidenceText: {
    fontSize: 14,
    color: '#666',
  },
  reasoningBox: {
    backgroundColor: '#f5f5f5',
    padding: 10,
    borderRadius: 8,
    marginBottom: 15,
  },
  reasoningTitle: {
    fontWeight: 'bold',
    marginBottom: 8,
  },
  reasonText: {
    fontSize: 13,
    color: '#333',
    marginBottom: 4,
  },
  featureBox: {
    backgroundColor: '#f9f9f9',
    padding: 10,
    borderRadius: 8,
  },
  featureTitle: {
    fontWeight: 'bold',
    marginBottom: 10,
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  featureText: {
    flex: 1,
    fontSize: 12,
  },
  featureBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    marginLeft: 10,
  },
  featureBarFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 4,
  },
});