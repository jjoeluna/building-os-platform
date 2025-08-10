#!/usr/bin/env python3
"""
Quick diagnostic test for BuildingOS API endpoints.
Tests only the core endpoints for rapid feedback during development.
"""

import requests
import time
from config import config


def quick_test_endpoint(method, endpoint, payload=None):
    """Test a single endpoint and return result summary."""
    url = f"{config.base_url}{endpoint}"

    try:
        start_time = time.time()

        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=payload, timeout=10)
        else:
            return {"status": "❌", "error": f"Unsupported method: {method}"}

        duration = (time.time() - start_time) * 1000

        return {
            "status": "✅" if response.status_code < 400 else "❌",
            "code": response.status_code,
            "time": f"{duration:.0f}ms",
            "size": len(response.content),
        }

    except Exception as e:
        return {"status": "💥", "error": str(e)[:100]}


def main():
    """Run quick diagnostic tests."""
    print("\n🚀 BuildingOS Quick API Test")
    print("=" * 50)
    print(f"🌐 Base URL: {config.base_url}")
    print(f"🏷️  Environment: {config.environment}")
    print()

    # Test endpoints
    tests = [
        ("GET", "/health", None),
        ("GET", "/director", None),
        ("POST", "/persona", {"user_id": "test-user", "message": "test"}),
        ("POST", "/psim/search", {"action": "search_person", "query": "test-user"}),
        (
            "POST",
            "/elevator/call",
            {
                "mission_id": "test-mission-123",
                "action": "call_elevator",
                "parameters": {"from_floor": 1, "to_floor": 3},
            },
        ),
        ("GET", "/coordinator/status", None),
    ]

    results = []
    for method, endpoint, payload in tests:
        print(f"🧪 {method} {endpoint}... ", end="", flush=True)
        result = quick_test_endpoint(method, endpoint, payload)
        results.append((endpoint, result))

        if result["status"] == "✅":
            print(f"{result['status']} {result['code']} ({result['time']})")
        elif "error" in result:
            print(f"{result['status']} {result.get('error', 'Unknown error')}")
        else:
            print(f"{result['status']} {result['code']} ({result['time']})")

    # Summary
    print("\n📊 Quick Test Summary:")
    print("-" * 30)
    success_count = sum(1 for _, result in results if result["status"] == "✅")
    total_count = len(results)

    for endpoint, result in results:
        status_icon = result["status"]
        if result["status"] == "✅":
            print(f"{status_icon} {endpoint} - {result['code']} ({result['time']})")
        elif "error" in result:
            print(f"{status_icon} {endpoint} - {result.get('error', 'Unknown error')}")
        else:
            print(f"{status_icon} {endpoint} - {result['code']}")

    print(
        f"\n🎯 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)"
    )

    if success_count < total_count:
        print(f"\n🔍 Next Steps:")
        print(f"   - Check CloudWatch logs for 500 errors")
        print(f"   - Verify environment variables in Lambda functions")
        print(f"   - Check IAM permissions")


if __name__ == "__main__":
    main()
