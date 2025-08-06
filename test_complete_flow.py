#!/usr/bin/env python3
"""
Script para testar o fluxo completo do BuildingOS
Simula o frontend e testa toda a cadeia de eventos
"""

import requests
import json
import time
import sys

# Configuração
API_ENDPOINT = "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com"


def test_health_check():
    """Testa se a API está funcionando"""
    print("🔍 Testando Health Check...")
    try:
        response = requests.get(f"{API_ENDPOINT}/health")
        data = response.json()
        print(f"✅ Health Check: {data}")
        return True
    except Exception as e:
        print(f"❌ Health Check falhou: {e}")
        return False


def test_persona_agent(message):
    """Testa o Persona Agent (fluxo correto)"""
    print(f"🤖 Testando Persona Agent com: '{message}'")

    payload = {"user_id": f"test-user-{int(time.time())}", "message": message}

    try:
        response = requests.post(
            f"{API_ENDPOINT}/persona",
            headers={"Content-Type": "application/json"},
            json=payload,
        )

        print(f"📡 Status: {response.status_code}")

        if response.status_code in [200, 202]:  # Accept both success codes
            data = response.json()
            print(f"✅ Resposta: {data}")
            return data.get("session_id")
        else:
            print(f"❌ Erro: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Exceção: {e}")
        return None


def test_director_direct(message):
    """Testa o Director diretamente (para comparação)"""
    print(f"🧠 Testando Director diretamente com: '{message}'")

    try:
        response = requests.get(
            f"{API_ENDPOINT}/director", params={"user_request": message}
        )

        print(f"📡 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta: {data}")
            return data.get("mission_id")
        else:
            print(f"❌ Erro: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Exceção: {e}")
        return None


def test_mission_status(mission_id):
    """Testa a verificação de status da missão"""
    print(f"📊 Verificando status da missão: {mission_id}")

    try:
        response = requests.get(
            f"{API_ENDPOINT}/director", params={"check_mission": mission_id}
        )

        print(f"📡 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status da Missão: {data}")
            return data
        else:
            print(f"❌ Erro: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Exceção: {e}")
        return None


def monitor_mission(mission_id, max_attempts=12, interval=5):
    """Monitora uma missão até completar"""
    print(
        f"👀 Monitorando missão {mission_id} por até {max_attempts * interval} segundos..."
    )

    for attempt in range(max_attempts):
        print(f"🔄 Tentativa {attempt + 1}/{max_attempts}")

        status_data = test_mission_status(mission_id)
        if status_data:
            status = status_data.get("status", "unknown")
            print(f"📈 Status atual: {status}")

            if status == "completed":
                print("🎉 Missão completada!")
                return status_data
            elif status == "failed":
                print("💥 Missão falhou!")
                return status_data

        time.sleep(interval)

    print("⏰ Timeout no monitoramento")
    return None


def main():
    """Função principal de teste"""
    print("🚀 Iniciando teste completo do BuildingOS")
    print("=" * 50)

    # 1. Health Check
    if not test_health_check():
        print("❌ Sistema não está funcionando. Abortando.")
        sys.exit(1)

    print("\n" + "=" * 50)

    # 2. Teste via Persona Agent (arquitetura correta)
    print("🎯 TESTE 1: Fluxo via Persona Agent (Correto)")
    session_id = test_persona_agent("Chame o elevador para o andar 5")

    if session_id:
        print(f"✅ Sessão criada: {session_id}")
        print("⏳ Aguardando processamento via Event Bus...")
        time.sleep(10)  # Aguarda processamento async
    else:
        print("❌ Falha no Persona Agent")

    print("\n" + "=" * 50)

    # 3. Teste via Director direto (para comparação)
    print("🎯 TESTE 2: Fluxo via Director direto (Comparação)")
    mission_id = test_director_direct("Chame o elevador para o andar 3")

    if mission_id:
        print(f"✅ Missão criada: {mission_id}")

        # 4. Monitorar missão
        print("\n" + "-" * 30)
        final_status = monitor_mission(mission_id)

        if final_status:
            print(f"🏁 Estado final: {final_status}")
        else:
            print("❌ Falha no monitoramento")
    else:
        print("❌ Falha no Director")

    print("\n" + "=" * 50)
    print("🏁 Teste completo finalizado!")


if __name__ == "__main__":
    main()
