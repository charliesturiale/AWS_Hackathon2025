import { getSafetyDataForLocation, getRouteSafetyScore } from '../SafetyDataService';
import { geocodeAddress, calculateRoutes, isGraphHopperConfigured } from '../graphhopper';

describe('SafePath SF Integration Tests', () => {
  describe('SafetyDataService', () => {
    test('getSafetyDataForLocation returns valid metrics', async () => {
      const result = await getSafetyDataForLocation(37.7749, -122.4194);
      
      expect(result).toHaveProperty('safetyScore');
      expect(result).toHaveProperty('crimeScore');
      expect(result).toHaveProperty('socialScore');
      expect(result).toHaveProperty('pedestrianScore');
      expect(result).toHaveProperty('incidents');
      
      expect(result.safetyScore).toBeGreaterThanOrEqual(0);
      expect(result.safetyScore).toBeLessThanOrEqual(100);
    });

    test('getRouteSafetyScore handles empty coordinates', async () => {
      const result = await getRouteSafetyScore([]);
      
      expect(result).toHaveProperty('safetyScore');
      expect(result.safetyScore).toBeGreaterThanOrEqual(0);
      expect(result.safetyScore).toBeLessThanOrEqual(100);
    });

    test('getRouteSafetyScore handles valid route', async () => {
      const coordinates = [
        { lat: 37.7749, lng: -122.4194 },
        { lat: 37.7751, lng: -122.4180 },
        { lat: 37.7753, lng: -122.4170 }
      ];
      
      const result = await getRouteSafetyScore(coordinates);
      
      expect(result).toHaveProperty('safetyScore');
      expect(result).toHaveProperty('incidents');
      expect(Array.isArray(result.incidents)).toBe(true);
    });
  });

  describe('GraphHopper Service', () => {
    test('isGraphHopperConfigured returns boolean', () => {
      const result = isGraphHopperConfigured();
      expect(typeof result).toBe('boolean');
    });

    test('geocodeAddress handles invalid API key gracefully', async () => {
      const result = await geocodeAddress('San Francisco');
      // Should either return null or mock coordinates
      expect(result === null || (result.lat && result.lng)).toBe(true);
    });

    test('calculateRoutes returns fallback data on API failure', async () => {
      const result = await calculateRoutes('Market St, SF', 'Golden Gate Park');
      
      // Should return routes even with invalid API key (mock data)
      expect(result).not.toBeNull();
      if (result) {
        expect(result).toHaveProperty('routes');
        expect(result).toHaveProperty('originCoords');
        expect(result).toHaveProperty('destCoords');
        expect(Array.isArray(result.routes)).toBe(true);
        expect(result.routes.length).toBeGreaterThan(0);
      }
    });
  });

  describe('Error Handling', () => {
    test('Services handle network errors gracefully', async () => {
      // Simulate network error by using invalid coordinates
      const result = await getSafetyDataForLocation(999, 999);
      
      expect(result).toHaveProperty('safetyScore');
      expect(result.safetyScore).toBeGreaterThanOrEqual(0);
    });
  });
});