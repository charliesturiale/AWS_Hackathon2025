export const mockSafetyData = [
  {
    id: '1',
    location: { latitude: 37.7840, longitude: -122.4090 },
    neighborhood: 'Tenderloin',
    safetyScore: 3.2,
    timeOfDay: 'night',
    incidents24h: 12,
  },
  {
    id: '2',
    location: { latitude: 37.7955, longitude: -122.3937 },
    neighborhood: 'Financial District',
    safetyScore: 7.8,
    timeOfDay: 'day',
    incidents24h: 2,
  },
  {
    id: '3',
    location: { latitude: 37.7599, longitude: -122.4148 },
    neighborhood: 'Mission District',
    safetyScore: 6.5,
    timeOfDay: 'evening',
    incidents24h: 5,
  },
];

export const mockCrimeData = [
  {
    coordinate: { latitude: 37.7835, longitude: -122.4089 },
    type: 'ASSAULT',
    severity: 'high',
    time: '2024-10-25T02:30:00Z',
  },
  {
    coordinate: { latitude: 37.7842, longitude: -122.4095 },
    type: 'THEFT',
    severity: 'medium',
    time: '2024-10-25T14:15:00Z',
  },
  {
    coordinate: { latitude: 37.7850, longitude: -122.4100 },
    type: 'ROBBERY',
    severity: 'high',
    time: '2024-10-25T22:45:00Z',
  },
  {
    coordinate: { latitude: 37.7820, longitude: -122.4080 },
    type: 'VANDALISM',
    severity: 'low',
    time: '2024-10-25T09:00:00Z',
  },
  {
    coordinate: { latitude: 37.7765, longitude: -122.4142 },
    type: 'THEFT',
    severity: 'medium',
    time: '2024-10-25T18:30:00Z',
  },
];

export const mockRoutes = {
  safe: {
    path: [
      { latitude: 37.7749, longitude: -122.4194 },
      { latitude: 37.7751, longitude: -122.4180 },
      { latitude: 37.7760, longitude: -122.4170 },
      { latitude: 37.7770, longitude: -122.4165 },
      { latitude: 37.7780, longitude: -122.4160 },
    ],
    safetyScore: 8.5,
    distance: 1.2,
    duration: 15,
    warnings: ['Avoid 6th Street', 'Well-lit route'],
  },
  fast: {
    path: [
      { latitude: 37.7749, longitude: -122.4194 },
      { latitude: 37.7765, longitude: -122.4185 },
      { latitude: 37.7780, longitude: -122.4160 },
    ],
    safetyScore: 6.2,
    distance: 0.9,
    duration: 12,
    warnings: ['Passes through Tenderloin edge', 'Less populated area'],
  },
  balanced: {
    path: [
      { latitude: 37.7749, longitude: -122.4194 },
      { latitude: 37.7755, longitude: -122.4185 },
      { latitude: 37.7765, longitude: -122.4175 },
      { latitude: 37.7780, longitude: -122.4160 },
    ],
    safetyScore: 7.3,
    distance: 1.0,
    duration: 13,
    warnings: ['Moderate safety', 'Some unlit areas'],
  },
};

export const sfNeighborhoods = [
  {
    name: 'Tenderloin',
    boundaries: [
      { latitude: 37.7875, longitude: -122.4186 },
      { latitude: 37.7875, longitude: -122.4097 },
      { latitude: 37.7825, longitude: -122.4097 },
      { latitude: 37.7825, longitude: -122.4186 },
    ],
    safetyScore: 3.2,
    color: 'rgba(255, 59, 48, 0.3)',
  },
  {
    name: 'Financial District',
    boundaries: [
      { latitude: 37.7982, longitude: -122.4059 },
      { latitude: 37.7982, longitude: -122.3950 },
      { latitude: 37.7905, longitude: -122.3950 },
      { latitude: 37.7905, longitude: -122.4059 },
    ],
    safetyScore: 7.8,
    color: 'rgba(76, 175, 80, 0.3)',
  },
  {
    name: 'Mission District',
    boundaries: [
      { latitude: 37.7700, longitude: -122.4250 },
      { latitude: 37.7700, longitude: -122.4100 },
      { latitude: 37.7500, longitude: -122.4100 },
      { latitude: 37.7500, longitude: -122.4250 },
    ],
    safetyScore: 6.5,
    color: 'rgba(255, 193, 7, 0.3)',
  },
];