#!/usr/bin/env python3
"""
Script para testar a API externa do elevador
Testa se a API está funcionando corretamente com autenticação JWT
"""

import requests
import jwt
import json
from datetime import datetime, timezone

# Configurações da API do Elevador
ELEVATOR_API_BASE_URL = "https://anna-minimal-api.neomot.com"
ELEVATOR_API_SECRET = "t3hILevRdzfFyd05U2g+XT4lPZCmT6CB+ytaQljWWOk="


def generate_jwt_token():
    """
    Gera JWT token para autenticação na API do elevador
    """
    try:
        payload = {
            "iss": "building-os",
            "aud": "elevator-api",
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": datetime.now(timezone.utc).timestamp() + 300,  # 5 minutos
        }

        token = jwt.encode(payload, ELEVATOR_API_SECRET, algorithm="HS256")
        print(f"🔑 Token JWT gerado: {token[:50]}...")
        return token

    except Exception as e:
        print(f"❌ Erro gerando JWT token: {str(e)}")
        raise


def test_elevator_api_endpoints():
    """
    Testa os endpoints da API do elevador com ID correto: 010504
    """
    print("🏗️ Testando API Externa do Elevador")
    print("=" * 50)

    # ID correto fornecido
    elevator_id = "010504"
    print(f"🏢 Usando ID do elevador: {elevator_id}")

    # Gerar token
    try:
        token = generate_jwt_token()
    except Exception as e:
        print(f"❌ Falha na geração do token: {e}")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # 1. Testar endpoint raiz
    print("\n1️⃣ Testando endpoint raiz...")
    try:
        response = requests.get(
            f"{ELEVATOR_API_BASE_URL}/", headers=headers, timeout=10
        )
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")

    # 2. Testar status do elevador com ID correto
    print(f"\n2️⃣ Testando status do elevador {elevator_id}...")
    try:
        response = requests.get(
            f"{ELEVATOR_API_BASE_URL}/elevator/{elevator_id}/status",
            headers=headers,
            timeout=10,
        )
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")

    # 3. Testar lista de andares com ID correto
    print(f"\n3️⃣ Testando lista de andares do elevador {elevator_id}...")
    try:
        response = requests.get(
            f"{ELEVATOR_API_BASE_URL}/elevator/{elevator_id}/floors",
            headers=headers,
            timeout=10,
        )
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")

    # 4. Testar chamada do elevador com ID correto
    print(f"\n4️⃣ Testando chamada do elevador {elevator_id}...")
    try:
        payload = {"from": 1, "to": 5}
        response = requests.post(
            f"{ELEVATOR_API_BASE_URL}/elevator/{elevator_id}/call",
            headers=headers,
            json=payload,
            timeout=10,
        )
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")

    # 5. Testar endpoints alternativos
    print("\n5️⃣ Testando endpoints alternativos...")

    # Sem /api
    try:
        response = requests.get(
            f"{ELEVATOR_API_BASE_URL}/elevator/status", headers=headers, timeout=10
        )
        print(f"📡 /elevator/status: {response.status_code}")
    except Exception as e:
        print(f"❌ /elevator/status erro: {e}")

    # Diferentes versões
    try:
        response = requests.get(
            f"{ELEVATOR_API_BASE_URL}/v1/elevator/status", headers=headers, timeout=10
        )
        print(f"📡 /v1/elevator/status: {response.status_code}")
    except Exception as e:
        print(f"❌ /v1/elevator/status erro: {e}")


def test_without_auth():
    """
    Testa a API sem autenticação para ver que tipo de erro retorna
    """
    print("\n" + "=" * 50)
    print("🔓 Testando API sem autenticação...")

    try:
        response = requests.get(
            f"{ELEVATOR_API_BASE_URL}/api/elevator/status", timeout=10
        )
        print(f"📡 Status sem auth: {response.status_code}")
        print(f"📄 Response sem auth: {response.text}")
    except Exception as e:
        print(f"❌ Erro sem auth: {e}")


if __name__ == "__main__":
    test_elevator_api_endpoints()
    test_without_auth()
    print("\n🏁 Teste da API externa finalizado!")
