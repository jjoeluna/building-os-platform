#!/usr/bin/env python3
"""
Busca por IDs válidos de elevador e endpoints de listagem
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


def search_valid_elevators():
    """Busca por IDs válidos de elevador"""
    print("🔍 Buscando IDs válidos de elevador...")
    print("=" * 50)

    token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Tentar listar elevadores primeiro
    possible_list_endpoints = [
        "/elevators",
        "/elevator",
        "/elevator/list",
        "/elevators/list",
        "/api/elevators",
        "/api/elevator/list",
        "/list",
    ]

    print("1️⃣ Tentando encontrar endpoint de listagem...")
    for endpoint in possible_list_endpoints:
        try:
            response = requests.get(
                f"{ELEVATOR_API_BASE_URL}{endpoint}", headers=headers, timeout=5
            )
            if response.status_code not in [404, 405]:
                print(f"✅ {endpoint} -> Status: {response.status_code}")
                if response.text:
                    print(f"   📄 Response: {response.text}")
        except Exception as e:
            print(f"⚠️ {endpoint}: {e}")

    # Tentar IDs mais variados
    print("\n2️⃣ Testando mais IDs de elevador...")
    possible_ids = [
        # Números simples
        "0",
        "1",
        "2",
        "3",
        "01",
        "02",
        "03",
        # Formatos comum
        "elev1",
        "elev01",
        "lift1",
        "lift01",
        "A",
        "B",
        "C",
        "E1",
        "E01",
        # IDs específicos
        "anna",
        "neomot",
        "main",
        "primary",
        "default",
        "test",
        "demo",
        "sample",
        # UUID-like
        "12345678-1234-5678-9012-123456789012",
        # Outros formatos
        "ELV_001",
        "ELEVATOR_1",
        "lift_01",
    ]

    valid_elevators = []

    for eid in possible_ids:
        try:
            response = requests.get(
                f"{ELEVATOR_API_BASE_URL}/elevator/{eid}/status",
                headers=headers,
                timeout=5,
            )

            if response.status_code == 200:
                print(f"🎉 SUCESSO! ID '{eid}' é válido!")
                print(f"   📄 Response: {response.text}")
                valid_elevators.append(eid)
            elif response.status_code != 400:
                print(f"🤔 ID '{eid}' -> Status interessante: {response.status_code}")
                if response.text:
                    print(f"   📄 Response: {response.text}")

        except Exception as e:
            continue  # Silenciar erros de timeout/conexão para essa busca

    if valid_elevators:
        print(f"\n🎯 Elevadores válidos encontrados: {valid_elevators}")
        return valid_elevators[0]  # Retorna o primeiro válido
    else:
        print("\n❌ Nenhum ID válido encontrado")
        return None


def test_with_different_payloads():
    """Testa diferentes formatos de payload"""
    print("\n3️⃣ Testando diferentes payloads...")

    token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Usar ID "1" que pelo menos não dá 404
    eid = "1"

    payloads = [
        {"from": 1, "to": 5},
        {"from": "1", "to": "5"},
        {"origin": 1, "destination": 5},
        {"floor": 1, "target": 5},
        {"source_floor": 1, "target_floor": 5},
        {"call_floor": 1, "destination_floor": 5},
    ]

    for i, payload in enumerate(payloads):
        try:
            response = requests.post(
                f"{ELEVATOR_API_BASE_URL}/elevator/{eid}/call",
                headers=headers,
                json=payload,
                timeout=5,
            )
            print(f"Payload {i+1} ({payload}): Status {response.status_code}")
            if response.text and response.status_code != 400:
                print(f"   📄 Response: {response.text}")
        except Exception as e:
            print(f"Payload {i+1}: Erro - {e}")


if __name__ == "__main__":
    valid_id = search_valid_elevators()
    test_with_different_payloads()
    print("\n🏁 Busca finalizada!")
