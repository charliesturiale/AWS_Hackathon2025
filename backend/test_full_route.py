# -*- coding: utf-8 -*-
"""Test full route calculation pipeline"""
import sys
import traceback
sys.path.insert(0, 'C:/Users/natha/AWS_HACKATHON2025/backend')

async def test_full_route():
    from app.main import _calculate_routes_internal, RouteRequest

    request = RouteRequest(
        origin="Pier 39, SF",
        destination="Union Square, SF"
    )

    try:
        print("Testing full route calculation...")
        result = await _calculate_routes_internal(request)
        print(f"\n=== SUCCESS ===")
        print(f"Generated {len(result['routes'])} routes")

    except Exception as e:
        print(f"\n=== ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        print(f"Error repr: {repr(e)}")
        print(f"\n=== FULL TRACEBACK ===")
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_full_route())
