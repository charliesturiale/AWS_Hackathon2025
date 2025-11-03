import requests

query = {
    "$limit": 50,
    "$order": "requested_datetime DESC",
    "$where": "service_name = 'Aggressive/Threatening' OR service_subtype = 'encampment'"
}

r = requests.get('https://data.sfgov.org/resource/vw6y-z8j6.json', params=query, timeout=30)
print(f"Status: {r.status_code}")
print(f"URL: {r.url}")
data = r.json()
print(f"Count: {len(data)}")
if data:
    print(f"First item service_name: {data[0].get('service_name')}")
    print(f"First item service_subtype: {data[0].get('service_subtype')}")
    print(f"First item date: {data[0].get('requested_datetime')}")
