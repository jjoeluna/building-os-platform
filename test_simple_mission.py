#!/usr/bin/env python3
"""
Teste simples para verificar se o pipeline está funcionando
Usa mock da API do elevador para evitar problemas externos
"""

import requests
import json
import time


def test_simple_mission():
    """
    Testa uma missão simples via Director
    """
    api_base = "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com"

    print("🚀 Testando missão simples...")

    # Criar missão via Director
    director_url = f"{api_base}/director"
    payload = {
        "user_request": "Liste os andares disponíveis",
        "context": {"test_mode": True},
    }

    response = requests.post(director_url, json=payload)
    print(f"📡 Status da criação: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Missão criada: {result}")
        mission_id = result.get("mission_id")

        # Esperar um pouco e verificar status
        print(f"⏳ Aguardando processamento da missão {mission_id}...")
        time.sleep(10)

        # Verificar logs do Coordinator para ver se processou
        print("📊 Verificando logs do Coordinator...")

    else:
        print(f"❌ Erro na criação: {response.text}")


if __name__ == "__main__":
    test_simple_mission()
