#!/usr/bin/env python3
"""
Script para descobrir endpoints disponíveis na API do elevador
"""

import requests
import jwt
import json
from datetime import datetime, timezone

ELEVATOR_API_BASE_URL = "https://anna-minimal-api.neomot.com"
ELEVATOR_API_SECRET = "t3hILevRdzfFyd05U2g+XT4lPZCmT6CB+ytaQljWWOk="


def generate_jwt_token():
    payload = {
        "iss": "building-os",
        "aud": "elevator-api",
        "iat": datetime.now(timezone.utc).timestamp(),
        "exp": datetime.now(timezone.utc).timestamp() + 300,
    }
    return jwt.encode(payload, ELEVATOR_API_SECRET, algorithm="HS256")


def discover_endpoints():
    """Tenta descobrir endpoints disponíveis"""
    print("🔍 Descobrindo endpoints disponíveis...")
    print("=" * 50)

    token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Lista de possíveis endpoints para testar
    possible_endpoints = [
        "/",
        "/health",
        "/status",
        "/elevator",
        "/elevators",
        "/api",
        "/api/health",
        "/api/status",
        "/api/elevator",
        "/api/elevators",
        "/api/v1/elevator",
        "/v1/elevator",
        "/docs",
        "/swagger",
        "/openapi.json",
        "/spec",
        "/elevator/call",
        "/elevator/status",
        "/elevator/floors",
        "/call",
        "/floors",
    ]

    working_endpoints = []

    for endpoint in possible_endpoints:
        try:
            url = f"{ELEVATOR_API_BASE_URL}{endpoint}"
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code != 404:
                print(f"✅ {endpoint} -> Status: {response.status_code}")
                if response.text and len(response.text) < 200:
                    print(f"   📄 Response: {response.text}")
                working_endpoints.append((endpoint, response.status_code))
            else:
                print(f"❌ {endpoint} -> 404")

        except Exception as e:
            print(f"⚠️ {endpoint} -> Erro: {e}")

    print("\n" + "=" * 50)
    print("📋 Resumo dos endpoints funcionais:")
    for endpoint, status in working_endpoints:
        print(f"  {endpoint} -> {status}")

    return working_endpoints


def test_content_types():
    """Testa diferentes content types"""
    print("\n🧪 Testando diferentes content types...")

    token = generate_jwt_token()

    # Test with different headers
    headers_variants = [
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        {"Authorization": f"Bearer {token}"},
        {"Content-Type": "application/json"},
        {},
    ]

    for i, headers in enumerate(headers_variants):
        try:
            response = requests.get(
                f"{ELEVATOR_API_BASE_URL}/", headers=headers, timeout=5
            )
            print(
                f"Headers {i+1}: Status {response.status_code} - {response.text[:50]}"
            )
        except Exception as e:
            print(f"Headers {i+1}: Erro - {e}")


if __name__ == "__main__":
    discover_endpoints()
    test_content_types()
