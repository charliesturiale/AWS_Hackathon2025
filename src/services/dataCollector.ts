/**
 * SafePath SF Data Collector
 * Fetches data from all required APIs
 */

interface Bounds {
  north: number;
  south: number;
  east: number;
  west: number;
  center: { lat: number; lng: number };
}

interface CrimeData {
  incident_id: string;
  incident_datetime: string;
  incident_category: string;
  incident_subcategory: string;
  latitude: string;
  longitude: string;
  resolution: string;
  police_district: string;
  analysis_neighborhood: string;
}

interface Report311 {
  service_request_id: string;
  requested_datetime: string;
  status_description: string;
  service_name: string;
  service_subtype: string;
  service_details: string;
  address: string;
  lat: string;
  long: string;
  neighborhoods_sffind_boundaries: string;
}

class SafePathDataCollector {
  private baseUrls: { [key: string]: string };

  constructor() {
    this.baseUrls = {
      crime: process.env.REACT_APP_SF_CRIME_API || 'https://data.sfgov.org/resource/wg3w-h783.json',
      hazards: process.env.REACT_APP_SF_311_API || 'https://data.sfgov.org/resource/vw6y-z8j6.json',
      permits: process.env.REACT_APP_SF_PERMITS_API || 'https://data.sfgov.org/resource/i98e-djp9.json',
      events: process.env.REACT_APP_SF_EVENTS_API || 'https://data.sfgov.org/resource/b2xn-6qcy.json',
      bart: `${process.env.REACT_APP_BART_BASE_URL}/stn.aspx?cmd=stns&key=${process.env.REACT_APP_BART_API_KEY}&json=y`,
      muni: `${process.env.REACT_APP_MUNI_BASE_URL}?command=routeList&a=sf-muni`,
    };
  }

  /**
   * Collect all data for a given area
   */
  async collectAllData(bounds: Bounds) {
    console.log('📊 Collecting data for SafePath SF...');
    
    const [
      crimes,
      hazards,
      construction,
      transitStops,
      lighting,
      events
    ] = await Promise.allSettled([
      this.getCrimeData(bounds),
      this.get311Reports(bounds),
      this.getConstructionPermits(bounds),
      this.getTransitStops(),
      this.getStreetLights(bounds),
      this.getEvents(bounds)
    ]);

    return {
      crimes: crimes.status === 'fulfilled' ? crimes.value : [],
      hazards: hazards.status === 'fulfilled' ? hazards.value : [],
      construction: construction.status === 'fulfilled' ? construction.value : [],
      transitStops: transitStops.status === 'fulfilled' ? transitStops.value : { bart: [], muni: [] },
      lighting: lighting.status === 'fulfilled' ? lighting.value : [],
      events: events.status === 'fulfilled' ? events.value : [],
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Get crime data from SF Police Department
   */
  async getCrimeData(bounds: Bounds): Promise<CrimeData[]> {
    try {
      // Get crimes from last 30 days
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      const dateString = thirtyDaysAgo.toISOString().split('T')[0];
      
      const query = `${this.baseUrls.crime}?$where=latitude>${bounds.south} AND latitude<${bounds.north} AND longitude>${bounds.west} AND longitude<${bounds.east} AND incident_datetime>'${dateString}'&$limit=1000`;
      
      console.log('🚔 Fetching crime data...');
      const response = await fetch(query);
      
      if (!response.ok) throw new Error(`Crime API error: ${response.status}`);
      
      const data = await response.json();
      console.log(`✅ Found ${data.length} crime incidents`);
      return data;
    } catch (error) {
      console.error('❌ Error fetching crime data:', error);
      return [];
    }
  }

  /**
   * Get 311 hazard reports
   */
  async get311Reports(bounds: Bounds): Promise<Report311[]> {
    try {
      // Get hazards from last 7 days that are still open
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      const dateString = sevenDaysAgo.toISOString();
      
      const safetyCategories = [
        'Street and Sidewalk Cleaning',
        'Streetlight',
        'Street Defects',
        'Sidewalk or Curb',
        'Encampment',
        'Blocked Street or SideWalk'
      ];
      
      const categoryFilter = safetyCategories.map(cat => `service_name='${cat}'`).join(' OR ');
      
      const query = `${this.baseUrls.hazards}?$where=(${categoryFilter}) AND requested_datetime>'${dateString}' AND lat>${bounds.south} AND lat<${bounds.north} AND long>${bounds.west} AND long<${bounds.east}&$limit=500`;
      
      console.log('🚧 Fetching 311 reports...');
      const response = await fetch(query);
      
      if (!response.ok) throw new Error(`311 API error: ${response.status}`);
      
      const data = await response.json();
      console.log(`✅ Found ${data.length} hazard reports`);
      return data;
    } catch (error) {
      console.error('❌ Error fetching 311 reports:', error);
      return [];
    }
  }

  /**
   * Get active construction permits
   */
  async getConstructionPermits(bounds: Bounds) {
    try {
      const query = `${this.baseUrls.permits}?status=ISSUED&$limit=100`;
      
      console.log('🏗️ Fetching construction permits...');
      const response = await fetch(query);
      
      if (!response.ok) throw new Error(`Permits API error: ${response.status}`);
      
      const data = await response.json();
      console.log(`✅ Found ${data.length} active permits`);
      return data;
    } catch (error) {
      console.error('❌ Error fetching permits:', error);
      return [];
    }
  }

  /**
   * Get transit stops (BART and Muni)
   */
  async getTransitStops() {
    try {
      console.log('🚇 Fetching transit stops...');
      
      // BART stations
      const bartResponse = await fetch(this.baseUrls.bart);
      const bartData = bartResponse.ok ? await bartResponse.text() : '';
      
      // Parse BART XML response (it returns XML even with json=y parameter)
      // For now, we'll use known BART stations in SF
      const bartStations = [
        { name: 'Embarcadero', lat: 37.793, lng: -122.397 },
        { name: 'Montgomery St', lat: 37.789, lng: -122.401 },
        { name: 'Powell St', lat: 37.785, lng: -122.407 },
        { name: 'Civic Center', lat: 37.780, lng: -122.414 },
        { name: '16th St Mission', lat: 37.765, lng: -122.420 },
        { name: '24th St Mission', lat: 37.752, lng: -122.418 },
        { name: 'Glen Park', lat: 37.733, lng: -122.433 },
        { name: 'Balboa Park', lat: 37.722, lng: -122.448 }
      ];
      
      // Muni routes (NextBus API)
      // For now, we'll return placeholder data
      const muniRoutes = [];
      
      console.log(`✅ Found ${bartStations.length} BART stations`);
      
      return { bart: bartStations, muni: muniRoutes };
    } catch (error) {
      console.error('❌ Error fetching transit stops:', error);
      return { bart: [], muni: [] };
    }
  }

  /**
   * Get street light outages
   */
  async getStreetLights(bounds: Bounds) {
    try {
      const query = `${this.baseUrls.hazards}?service_name=Streetlight&status_description=Open&$limit=200`;
      
      console.log('💡 Fetching street light issues...');
      const response = await fetch(query);
      
      if (!response.ok) throw new Error(`Street lights API error: ${response.status}`);
      
      const data = await response.json();
      console.log(`✅ Found ${data.length} street light issues`);
      return data;
    } catch (error) {
      console.error('❌ Error fetching street lights:', error);
      return [];
    }
  }

  /**
   * Get events happening in the area
   */
  async getEvents(bounds: Bounds) {
    try {
      // For now, return empty array as events API requires specific format
      console.log('🎉 Events API not configured yet');
      return [];
    } catch (error) {
      console.error('❌ Error fetching events:', error);
      return [];
    }
  }

  /**
   * Calculate safety score for a location based on collected data
   */
  calculateLocationSafety(lat: number, lng: number, data: any) {
    let safetyScore = 100; // Start with perfect score
    
    // Check crimes within 200m
    const nearbyCrimes = data.crimes.filter((crime: CrimeData) => {
      const distance = this.calculateDistance(
        lat, lng,
        parseFloat(crime.latitude), 
        parseFloat(crime.longitude)
      );
      return distance < 200; // 200 meters
    });
    
    // Deduct points for crimes
    safetyScore -= nearbyCrimes.length * 5;
    
    // Check hazards within 100m
    const nearbyHazards = data.hazards.filter((hazard: Report311) => {
      const distance = this.calculateDistance(
        lat, lng,
        parseFloat(hazard.lat),
        parseFloat(hazard.long)
      );
      return distance < 100;
    });
    
    // Deduct points for hazards
    safetyScore -= nearbyHazards.length * 2;
    
    // Add points for nearby transit (safety havens)
    const nearbyTransit = data.transitStops.bart.filter((station: any) => {
      const distance = this.calculateDistance(lat, lng, station.lat, station.lng);
      return distance < 500;
    });
    
    safetyScore += nearbyTransit.length * 10;
    
    // Ensure score is between 0 and 100
    return Math.max(0, Math.min(100, safetyScore));
  }

  /**
   * Calculate distance between two points in meters
   */
  private calculateDistance(lat1: number, lng1: number, lat2: number, lng2: number): number {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = lat1 * Math.PI/180;
    const φ2 = lat2 * Math.PI/180;
    const Δφ = (lat2-lat1) * Math.PI/180;
    const Δλ = (lng2-lng1) * Math.PI/180;

    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c;
  }

  /**
   * Get neighborhood-specific data
   */
  getNeighborhoodData(neighborhood: string) {
    const neighborhoods: { [key: string]: Bounds } = {
      'Tenderloin': {
        north: 37.7875,
        south: 37.7825,
        east: -122.4097,
        west: -122.4186,
        center: { lat: 37.785, lng: -122.414 }
      },
      'Financial District': {
        north: 37.7982,
        south: 37.7905,
        east: -122.3950,
        west: -122.4059,
        center: { lat: 37.794, lng: -122.400 }
      },
      'Mission': {
        north: 37.7700,
        south: 37.7500,
        east: -122.4100,
        west: -122.4250,
        center: { lat: 37.760, lng: -122.418 }
      },
      'Castro': {
        north: 37.7650,
        south: 37.7550,
        east: -122.4300,
        west: -122.4400,
        center: { lat: 37.760, lng: -122.435 }
      },
      'Golden Gate Park': {
        north: 37.7736,
        south: 37.7661,
        east: -122.4534,
        west: -122.5116,
        center: { lat: 37.770, lng: -122.482 }
      }
    };

    return neighborhoods[neighborhood] || neighborhoods['Financial District'];
  }
}

export default SafePathDataCollector;