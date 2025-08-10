#!/usr/bin/env python3
"""
Manual CORS Testing Tool
Tests CORS headers directly from each endpoint
"""

import requests
import json
import os
import sys


# Simple test without rich library to avoid encoding issues
def test_cors_headers():
    """Test CORS headers on all endpoints"""

    base_url = "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com"

    endpoints = [
        ("/health", "GET", None),
        ("/director", "GET", None),
        ("/persona", "POST", {"user_id": "cors-test", "message": "test"}),
        ("/elevator/call", "POST", {"mission_id": "cors-test", "action": "test"}),
        ("/psim/search", "POST", {"action": "search_person", "query": "test"}),
    ]

    print("CORS Headers Test")
    print("=" * 50)

    for endpoint, method, payload in endpoints:
        print(f"\nTesting {method} {endpoint}")
        print("-" * 30)

        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(
                    f"{base_url}{endpoint}", json=payload, timeout=10
                )

            print(f"Status: {response.status_code}")

            # Check CORS headers
            cors_headers = {}
            for header, value in response.headers.items():
                if "access-control" in header.lower():
                    cors_headers[header] = value

            if cors_headers:
                print("CORS Headers Found:")
                for header, value in cors_headers.items():
                    print(f"  {header}: {value}")
            else:
                print("NO CORS Headers Found!")
                print("All headers:")
                for header, value in response.headers.items():
                    print(f"  {header}: {value}")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    test_cors_headers()
