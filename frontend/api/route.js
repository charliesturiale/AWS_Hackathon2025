export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const { points, vehicle = 'foot' } = req.query;
  
  if (!points || !Array.isArray(points) || points.length < 2) {
    return res.status(400).json({ error: 'At least 2 points are required' });
  }

  const GRAPHHOPPER_API_KEY = 'ee6ac405-9a11-42e2-a0ac-dc333939f34b';
  
  // Build URL with points
  const params = new URLSearchParams({
    vehicle,
    locale: 'en',
    points_encoded: 'false',
    algorithm: 'alternative_route',
    'alternative_route.max_paths': '3',
    key: GRAPHHOPPER_API_KEY
  });
  
  // Add points
  points.forEach(point => {
    params.append('point', point);
  });

  const url = `https://graphhopper.com/api/1/route?${params.toString()}`;

  try {
    const response = await fetch(url);
    const data = await response.json();
    
    res.status(200).json(data);
  } catch (error) {
    console.error('Routing error:', error);
    res.status(500).json({ error: 'Failed to calculate route' });
  }
}