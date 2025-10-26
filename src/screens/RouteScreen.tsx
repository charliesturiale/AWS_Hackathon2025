import React, { useState } from 'react';
import { View, StyleSheet, Text, TextInput, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function RouteScreen() {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [preference, setPreference] = useState<'safest' | 'balanced' | 'fastest'>('balanced');

  const popularDestinations = [
    { name: 'Union Square', address: '333 Post St, SF', safety: 8.2 },
    { name: 'Ferry Building', address: '1 Ferry Building, SF', safety: 8.8 },
    { name: 'Salesforce Tower', address: '415 Mission St, SF', safety: 7.9 },
    { name: 'Golden Gate Park', address: 'Golden Gate Park, SF', safety: 7.5 },
    { name: 'Fisherman\'s Wharf', address: 'Pier 39, SF', safety: 8.0 },
  ];

  const handleCalculateRoute = () => {
    console.log('Calculating route:', { from, to, preference });
    // TODO: Implement route calculation
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Route Input */}
        <View style={styles.inputSection}>
          <Text style={styles.sectionTitle}>Plan Your Route</Text>
          
          <View style={styles.inputContainer}>
            <View style={styles.inputIcon}>
              <Ionicons name="location" size={20} color="#007AFF" />
            </View>
            <TextInput
              style={styles.input}
              placeholder="From: Current Location or Address"
              value={from}
              onChangeText={setFrom}
            />
          </View>

          <View style={styles.inputContainer}>
            <View style={styles.inputIcon}>
              <Ionicons name="flag" size={20} color="#FF3B30" />
            </View>
            <TextInput
              style={styles.input}
              placeholder="To: Destination"
              value={to}
              onChangeText={setTo}
            />
          </View>
        </View>

        {/* Routing Preferences */}
        <View style={styles.preferenceSection}>
          <Text style={styles.sectionTitle}>Routing Preference</Text>
          
          <TouchableOpacity
            style={[styles.preferenceOption, preference === 'safest' && styles.selectedPreference]}
            onPress={() => setPreference('safest')}
          >
            <Ionicons 
              name="shield-checkmark" 
              size={24} 
              color={preference === 'safest' ? '#fff' : '#4CAF50'} 
            />
            <View style={styles.preferenceText}>
              <Text style={[styles.preferenceTitle, preference === 'safest' && styles.selectedText]}>
                Safest Route
              </Text>
              <Text style={[styles.preferenceDesc, preference === 'safest' && styles.selectedText]}>
                Prioritize well-lit, populated areas
              </Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.preferenceOption, preference === 'balanced' && styles.selectedPreference]}
            onPress={() => setPreference('balanced')}
          >
            <Ionicons 
              name="analytics" 
              size={24} 
              color={preference === 'balanced' ? '#fff' : '#007AFF'} 
            />
            <View style={styles.preferenceText}>
              <Text style={[styles.preferenceTitle, preference === 'balanced' && styles.selectedText]}>
                Balanced
              </Text>
              <Text style={[styles.preferenceDesc, preference === 'balanced' && styles.selectedText]}>
                Balance safety and travel time
              </Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.preferenceOption, preference === 'fastest' && styles.selectedPreference]}
            onPress={() => setPreference('fastest')}
          >
            <Ionicons 
              name="flash" 
              size={24} 
              color={preference === 'fastest' ? '#fff' : '#FFC107'} 
            />
            <View style={styles.preferenceText}>
              <Text style={[styles.preferenceTitle, preference === 'fastest' && styles.selectedText]}>
                Fastest Route
              </Text>
              <Text style={[styles.preferenceDesc, preference === 'fastest' && styles.selectedText]}>
                Get there as quickly as possible
              </Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Popular Destinations */}
        <View style={styles.popularSection}>
          <Text style={styles.sectionTitle}>Popular Destinations</Text>
          
          {popularDestinations.map((dest, index) => (
            <TouchableOpacity 
              key={index} 
              style={styles.destinationCard}
              onPress={() => setTo(dest.address)}
            >
              <View style={styles.destinationInfo}>
                <Text style={styles.destinationName}>{dest.name}</Text>
                <Text style={styles.destinationAddress}>{dest.address}</Text>
              </View>
              <View style={styles.safetyBadge}>
                <Text style={styles.safetyScore}>{dest.safety}</Text>
                <Ionicons name="shield-checkmark" size={16} color="#4CAF50" />
              </View>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>

      {/* Calculate Route Button */}
      <TouchableOpacity style={styles.calculateButton} onPress={handleCalculateRoute}>
        <Text style={styles.calculateButtonText}>Calculate Route</Text>
        <Ionicons name="arrow-forward" size={20} color="#fff" />
      </TouchableOpacity>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  inputSection: {
    backgroundColor: '#fff',
    padding: 20,
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 15,
    color: '#333',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f8f8',
    borderRadius: 10,
    marginBottom: 10,
    paddingHorizontal: 15,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    paddingVertical: 15,
    fontSize: 16,
  },
  preferenceSection: {
    backgroundColor: '#fff',
    padding: 20,
    marginBottom: 10,
  },
  preferenceOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderRadius: 10,
    backgroundColor: '#f8f8f8',
    marginBottom: 10,
  },
  selectedPreference: {
    backgroundColor: '#007AFF',
  },
  preferenceText: {
    marginLeft: 15,
    flex: 1,
  },
  preferenceTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 3,
  },
  preferenceDesc: {
    fontSize: 14,
    color: '#666',
  },
  selectedText: {
    color: '#fff',
  },
  popularSection: {
    backgroundColor: '#fff',
    padding: 20,
    marginBottom: 100,
  },
  destinationCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#f8f8f8',
    borderRadius: 10,
    marginBottom: 10,
  },
  destinationInfo: {
    flex: 1,
  },
  destinationName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 3,
  },
  destinationAddress: {
    fontSize: 14,
    color: '#666',
  },
  safetyBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F5E9',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 15,
  },
  safetyScore: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4CAF50',
    marginRight: 5,
  },
  calculateButton: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    backgroundColor: '#007AFF',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 18,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  calculateButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginRight: 8,
  },
});