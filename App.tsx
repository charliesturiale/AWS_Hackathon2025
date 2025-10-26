import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

// Import screens
import MapScreen from './src/screens/MapScreen';
import RouteScreen from './src/screens/RouteScreen';
import SafetyScreen from './src/screens/SafetyScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <StatusBar style="light" />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              let iconName: any = 'alert-circle';

              if (route.name === 'Map') {
                iconName = focused ? 'map' : 'map-outline';
              } else if (route.name === 'Route') {
                iconName = focused ? 'navigate' : 'navigate-outline';
              } else if (route.name === 'Safety') {
                iconName = focused ? 'shield' : 'shield-outline';
              } else if (route.name === 'Settings') {
                iconName = focused ? 'settings' : 'settings-outline';
              }

              return <Ionicons name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#007AFF',
            tabBarInactiveTintColor: 'gray',
            headerStyle: {
              backgroundColor: '#007AFF',
            },
            headerTintColor: '#fff',
          })}
        >
          <Tab.Screen name="Map" component={MapScreen} options={{ title: 'SafePath SF' }} />
          <Tab.Screen name="Route" component={RouteScreen} options={{ title: 'Plan Route' }} />
          <Tab.Screen name="Safety" component={SafetyScreen} options={{ title: 'Safety Info' }} />
          <Tab.Screen name="Settings" component={SettingsScreen} options={{ title: 'Settings' }} />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}