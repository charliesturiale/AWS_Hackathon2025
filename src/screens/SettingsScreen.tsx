import React, { useState } from 'react';
import { View, StyleSheet, Text, Switch, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function SettingsScreen() {
  const [notifications, setNotifications] = useState(true);
  const [avoidHills, setAvoidHills] = useState(false);
  const [accessibility, setAccessibility] = useState(false);
  const [voiceGuidance, setVoiceGuidance] = useState(true);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Safety Preferences</Text>
        
        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Safety Notifications</Text>
            <Text style={styles.settingDescription}>Alert me about unsafe areas</Text>
          </View>
          <Switch
            value={notifications}
            onValueChange={setNotifications}
            ios_backgroundColor="#e0e0e0"
          />
        </View>

        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Voice Guidance</Text>
            <Text style={styles.settingDescription}>Audio navigation instructions</Text>
          </View>
          <Switch
            value={voiceGuidance}
            onValueChange={setVoiceGuidance}
            ios_backgroundColor="#e0e0e0"
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Route Preferences</Text>
        
        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Avoid Steep Hills</Text>
            <Text style={styles.settingDescription}>Route around SF's steepest streets</Text>
          </View>
          <Switch
            value={avoidHills}
            onValueChange={setAvoidHills}
            ios_backgroundColor="#e0e0e0"
          />
        </View>

        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Accessibility Mode</Text>
            <Text style={styles.settingDescription}>Wheelchair-friendly routes</Text>
          </View>
          <Switch
            value={accessibility}
            onValueChange={setAccessibility}
            ios_backgroundColor="#e0e0e0"
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        
        <TouchableOpacity style={styles.linkRow}>
          <Text style={styles.linkText}>Privacy Policy</Text>
          <Ionicons name="chevron-forward" size={20} color="#666" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.linkRow}>
          <Text style={styles.linkText}>Terms of Service</Text>
          <Ionicons name="chevron-forward" size={20} color="#666" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.linkRow}>
          <Text style={styles.linkText}>Report an Issue</Text>
          <Ionicons name="chevron-forward" size={20} color="#666" />
        </TouchableOpacity>
      </View>

      <View style={styles.versionContainer}>
        <Text style={styles.versionText}>SafePath SF v1.0.0</Text>
        <Text style={styles.versionSubtext}>AWS x INRIX Hackathon 2024</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  section: {
    backgroundColor: '#fff',
    marginTop: 20,
    paddingHorizontal: 20,
    paddingVertical: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
    marginTop: 10,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingInfo: {
    flex: 1,
    marginRight: 10,
  },
  settingLabel: {
    fontSize: 16,
    color: '#333',
    marginBottom: 3,
  },
  settingDescription: {
    fontSize: 14,
    color: '#666',
  },
  linkRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  linkText: {
    fontSize: 16,
    color: '#007AFF',
  },
  versionContainer: {
    alignItems: 'center',
    marginVertical: 30,
  },
  versionText: {
    fontSize: 14,
    color: '#999',
    marginBottom: 5,
  },
  versionSubtext: {
    fontSize: 12,
    color: '#bbb',
  },
});