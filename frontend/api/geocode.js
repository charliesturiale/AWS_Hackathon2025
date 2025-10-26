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

  const { q } = req.query;
  
  if (!q) {
    return res.status(400).json({ error: 'Address parameter is required' });
  }

  const GRAPHHOPPER_API_KEY = 'ee6ac405-9a11-42e2-a0ac-dc333939f34b';
  const url = `https://graphhopper.com/api/1/geocode?q=${encodeURIComponent(q)}&key=${GRAPHHOPPER_API_KEY}`;

  try {
    const response = await fetch(url);
    const data = await response.json();
    
    res.status(200).json(data);
  } catch (error) {
    console.error('Geocoding error:', error);
    res.status(500).json({ error: 'Failed to geocode address' });
  }
}