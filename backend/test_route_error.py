# -*- coding: utf-8 -*-
"""Test script to reproduce route calculation error"""
import sys
import traceback
sys.path.insert(0, 'C:/Users/natha/AWS_HACKATHON2025/backend')

# Test the route calculation
async def test_route():
    from app.main import geocode_address, get_graphhopper_routes

    try:
        print("Testing geocoding...")
        origin = await geocode_address("Pier 39, SF")
        print(f"Origin geocoded: {origin}")

        dest = await geocode_address("Union Square, SF")
        print(f"Destination geocoded: {dest}")

        print("\nTesting route generation...")
        routes = await get_graphhopper_routes(origin, dest, num_routes=3)
        print(f"Routes generated: {len(routes) if routes else 0}")

    except Exception as e:
        print(f"\n=== ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        print(f"\n=== FULL TRACEBACK ===")
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_route())
