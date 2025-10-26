import React from 'react';
import { View, StyleSheet, Text, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function SafetyScreen() {
  const neighborhoods = [
    { 
      name: 'Tenderloin', 
      safety: 3.2, 
      status: 'High Caution',
      color: '#FF3B30',
      tips: ['Avoid after 10 PM', 'Stay on main streets', 'Travel in groups']
    },
    { 
      name: 'Financial District', 
      safety: 7.8, 
      status: 'Generally Safe',
      color: '#4CAF50',
      tips: ['Well-lit streets', 'Less safe after business hours', 'Good police presence']
    },
    { 
      name: 'Mission District', 
      safety: 6.5, 
      status: 'Use Caution',
      color: '#FFC107',
      tips: ['Varies by block', 'Busy Valencia St is safer', 'Watch for pickpockets']
    },
    { 
      name: 'Castro', 
      safety: 7.9, 
      status: 'Generally Safe',
      color: '#4CAF50',
      tips: ['Well-populated', 'Active nightlife', 'Good lighting']
    },
    { 
      name: 'SOMA', 
      safety: 5.8, 
      status: 'Mixed Safety',
      color: '#FF9500',
      tips: ['Varies greatly', 'Avoid alleys', 'Better during events']
    },
  ];

  const getSafetyIcon = (score: number) => {
    if (score >= 7) return 'shield-checkmark' as any;
    if (score >= 5) return 'warning' as any;
    return 'alert-circle' as any;
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>SF Neighborhood Safety</Text>
        <Text style={styles.headerSubtitle}>Real-time safety information</Text>
      </View>

      {neighborhoods.map((neighborhood, index) => (
        <View key={index} style={styles.card}>
          <View style={styles.cardHeader}>
            <View>
              <Text style={styles.neighborhoodName}>{neighborhood.name}</Text>
              <Text style={[styles.status, { color: neighborhood.color }]}>
                {neighborhood.status}
              </Text>
            </View>
            <View style={[styles.scoreContainer, { backgroundColor: neighborhood.color + '20' }]}>
              <Text style={[styles.score, { color: neighborhood.color }]}>
                {neighborhood.safety}
              </Text>
              <Ionicons 
                name={getSafetyIcon(neighborhood.safety)} 
                size={20} 
                color={neighborhood.color} 
              />
            </View>
          </View>
          
          <View style={styles.tipsContainer}>
            {neighborhood.tips.map((tip, tipIndex) => (
              <View key={tipIndex} style={styles.tip}>
                <Ionicons name="information-circle" size={16} color="#666" />
                <Text style={styles.tipText}>{tip}</Text>
              </View>
            ))}
          </View>
        </View>
      ))}

      <View style={styles.legendCard}>
        <Text style={styles.legendTitle}>Safety Score Legend</Text>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: '#4CAF50' }]} />
          <Text style={styles.legendText}>7.0+ - Generally Safe</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: '#FFC107' }]} />
          <Text style={styles.legendText}>5.0-6.9 - Use Caution</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: '#FF3B30' }]} />
          <Text style={styles.legendText}>Below 5.0 - High Caution</Text>
        </View>
      </View>

      <View style={styles.emergencyCard}>
        <Text style={styles.emergencyTitle}>Emergency Contacts</Text>
        <View style={styles.emergencyItem}>
          <Ionicons name="call" size={20} color="#FF3B30" />
          <Text style={styles.emergencyText}>Emergency: 911</Text>
        </View>
        <View style={styles.emergencyItem}>
          <Ionicons name="call-outline" size={20} color="#007AFF" />
          <Text style={styles.emergencyText}>Non-Emergency: 415-553-0123</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  card: {
    backgroundColor: '#fff',
    marginHorizontal: 15,
    marginTop: 15,
    borderRadius: 12,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  neighborhoodName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  status: {
    fontSize: 14,
    fontWeight: '500',
    marginTop: 3,
  },
  scoreContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
  },
  score: {
    fontSize: 18,
    fontWeight: '700',
    marginRight: 5,
  },
  tipsContainer: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 12,
  },
  tip: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  tipText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 8,
    flex: 1,
  },
  legendCard: {
    backgroundColor: '#fff',
    margin: 15,
    borderRadius: 12,
    padding: 15,
  },
  legendTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  legendColor: {
    width: 20,
    height: 20,
    borderRadius: 4,
    marginRight: 10,
  },
  legendText: {
    fontSize: 14,
    color: '#666',
  },
  emergencyCard: {
    backgroundColor: '#FFF5F5',
    margin: 15,
    marginBottom: 30,
    borderRadius: 12,
    padding: 15,
    borderWidth: 1,
    borderColor: '#FFE0E0',
  },
  emergencyTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  emergencyItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  emergencyText: {
    fontSize: 14,
    color: '#333',
    marginLeft: 10,
    fontWeight: '500',
  },
});