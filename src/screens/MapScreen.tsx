import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, Alert, ScrollView, Image } from 'react-native';
import * as Location from 'expo-location';
import { Ionicons } from '@expo/vector-icons';
import { mockSafetyData, mockCrimeData } from '../data/mockData';

export default function MapScreen() {
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<'safe' | 'fast' | null>(null);
  const [showSafetyOverlay, setShowSafetyOverlay] = useState(true);
  
  // San Francisco center coordinates
  const SF_CENTER = {
    latitude: 37.7749,
    longitude: -122.4194,
    latitudeDelta: 0.05,
    longitudeDelta: 0.05,
  };

  // Mock routes for testing
  const SAFE_ROUTE = [
    { latitude: 37.7749, longitude: -122.4194 },
    { latitude: 37.7751, longitude: -122.4180 },
    { latitude: 37.7760, longitude: -122.4170 },
    { latitude: 37.7780, longitude: -122.4160 },
  ];

  const FAST_ROUTE = [
    { latitude: 37.7749, longitude: -122.4194 },
    { latitude: 37.7765, longitude: -122.4185 },
    { latitude: 37.7780, longitude: -122.4160 },
  ];

  useEffect(() => {
    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission denied', 'Location permission is required for this app');
        return;
      }

      let currentLocation = await Location.getCurrentPositionAsync({});
      setLocation(currentLocation);
    })();
  }, []);

  const handleRouteSelect = (routeType: 'safe' | 'fast') => {
    setSelectedRoute(routeType);
    Alert.alert(
      `${routeType === 'safe' ? 'Safe' : 'Fast'} Route Selected`,
      `${routeType === 'safe' ? 'This route prioritizes safety with a score of 8.5/10' : 'This is the fastest route but passes through less safe areas (6.2/10)'}`
    );
  };

  return (
    <View style={styles.container}>
      {/* Temporary map placeholder - replace with actual MapView when maps are configured */}
      <View style={styles.mapPlaceholder}>
        <Image
          source={{ uri: 'https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/-122.4194,37.7749,13,0/600x400?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw' }}
          style={styles.map}
          resizeMode="cover"
        />
        
        {/* Overlay showing selected route */}
        {selectedRoute && (
          <View style={styles.routeOverlay}>
            <Text style={styles.routeOverlayText}>
              {selectedRoute === 'safe' ? '🛡️ Safe Route Selected' : '⚡ Fast Route Selected'}
            </Text>
          </View>
        )}
        
        {/* Crime indicators */}
        {showSafetyOverlay && (
          <View style={styles.safetyIndicator}>
            <View style={styles.safetyDot} />
            <Text style={styles.safetyText}>Safety Overlay Active</Text>
          </View>
        )}
      </View>

      {/* Route selection buttons */}
      <View style={styles.routeButtons}>
        <TouchableOpacity
          style={[styles.routeButton, selectedRoute === 'safe' && styles.selectedRoute]}
          onPress={() => handleRouteSelect('safe')}
        >
          <Ionicons name="shield-checkmark" size={24} color={selectedRoute === 'safe' ? '#fff' : '#4CAF50'} />
          <Text style={[styles.routeButtonText, selectedRoute === 'safe' && styles.selectedText]}>
            Safe Route
          </Text>
          <Text style={[styles.routeTime, selectedRoute === 'safe' && styles.selectedText]}>
            15 min
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.routeButton, selectedRoute === 'fast' && styles.selectedRoute]}
          onPress={() => handleRouteSelect('fast')}
        >
          <Ionicons name="flash" size={24} color={selectedRoute === 'fast' ? '#fff' : '#FFC107'} />
          <Text style={[styles.routeButtonText, selectedRoute === 'fast' && styles.selectedText]}>
            Fast Route
          </Text>
          <Text style={[styles.routeTime, selectedRoute === 'fast' && styles.selectedText]}>
            12 min
          </Text>
        </TouchableOpacity>
      </View>

      {/* Safety overlay toggle */}
      <TouchableOpacity
        style={styles.overlayToggle}
        onPress={() => setShowSafetyOverlay(!showSafetyOverlay)}
      >
        <Ionicons name={showSafetyOverlay ? "eye" : "eye-off"} size={24} color="#007AFF" />
      </TouchableOpacity>

      {/* Current location button */}
      <TouchableOpacity style={styles.locationButton}>
        <Ionicons name="locate" size={24} color="#007AFF" />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  mapPlaceholder: {
    flex: 1,
    position: 'relative',
  },
  map: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  routeOverlay: {
    position: 'absolute',
    top: 150,
    alignSelf: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    padding: 10,
    borderRadius: 20,
  },
  routeOverlayText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  safetyIndicator: {
    position: 'absolute',
    top: 200,
    left: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    padding: 8,
    borderRadius: 15,
  },
  safetyDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#FF3B30',
    marginRight: 8,
  },
  safetyText: {
    fontSize: 12,
    color: '#333',
  },
  routeButtons: {
    position: 'absolute',
    bottom: 30,
    left: 20,
    right: 20,
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  routeButton: {
    backgroundColor: 'white',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  selectedRoute: {
    backgroundColor: '#007AFF',
  },
  routeButtonText: {
    marginLeft: 8,
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  selectedText: {
    color: '#fff',
  },
  routeTime: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
  },
  overlayToggle: {
    position: 'absolute',
    top: 50,
    right: 20,
    backgroundColor: 'white',
    padding: 10,
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  locationButton: {
    position: 'absolute',
    top: 100,
    right: 20,
    backgroundColor: 'white',
    padding: 10,
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  crimeMarker: {
    width: 20,
    height: 20,
    borderRadius: 10,
    opacity: 0.6,
  },
});