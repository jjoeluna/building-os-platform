#!/usr/bin/env python3
"""
Teste Específico de Fluxo: Persona → Director
"""

import json
import boto3
from datetime import datetime


def test_persona_to_director_flow():
    """Testa o fluxo específico Persona → Director"""

    sns = boto3.client("sns")
    lambda_client = boto3.client("lambda")

    mission_id = f"flow-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    print("🔄 TESTE DE FLUXO: PERSONA → DIRECTOR")
    print("=" * 60)
    print(f"🆔 Mission ID: {mission_id}")

    # 1. Simular Persona publicando intenção
    print("\n📝 PASSO 1: Persona publica intenção")

    persona_message = {
        "mission_id": mission_id,
        "user_id": "test-user-001",
        "user_intention": "Chamar elevador para o 5º andar",
        "timestamp": datetime.now().isoformat(),
        "context": {
            "current_floor": 5,
            "destination_floor": 0,
            "building_id": "building-001",
        },
    }

    try:
        # Simular o que o Persona faz: publicar no persona_intention_topic
        response = sns.publish(
            TopicArn="arn:aws:sns:us-east-1:481251881947:bos-persona-intention-topic-dev",
            Message=json.dumps(persona_message),
            Subject=f"User Intention from Persona - {mission_id}",
        )

        print(f"  ✅ Persona publicou: Message ID {response['MessageId']}")
        print(f"  📋 Intenção: {persona_message['user_intention']}")

    except Exception as e:
        print(f"  ❌ Erro ao publicar: {e}")
        return False

    # 2. Aguardar processamento
    print("\n⏳ PASSO 2: Aguardando Director processar...")
    import time

    time.sleep(5)

    # 3. Verificar logs do Director
    print("\n📊 PASSO 3: Verificando logs do Director")

    try:
        logs_client = boto3.client("logs")

        # Obter stream mais recente
        streams_response = logs_client.describe_log_streams(
            logGroupName="/aws/lambda/bos-agent-director-dev",
            orderBy="LastEventTime",
            descending=True,
            limit=1,
        )

        if streams_response["logStreams"]:
            stream_name = streams_response["logStreams"][0]["logStreamName"]

            # Obter eventos recentes
            events_response = logs_client.get_log_events(
                logGroupName="/aws/lambda/bos-agent-director-dev",
                logStreamName=stream_name,
                limit=20,
            )

            # Procurar por nosso mission_id nos logs
            found_processing = False
            found_success = False

            for event in events_response["events"]:
                message = event["message"]
                if mission_id in message:
                    print(f"  📋 Log encontrado: {message.strip()}")

                    if "Processing persona intention" in message:
                        found_processing = True
                    if (
                        "Mission plan created" in message
                        or "success" in message.lower()
                    ):
                        found_success = True

            if found_processing:
                print("  ✅ Director recebeu e processou a intenção")
                if found_success:
                    print("  ✅ Processamento bem-sucedido detectado")
                    return True
                else:
                    print("  ⚠️  Processamento iniciado mas resultado incerto")
                    return False
            else:
                print("  ❌ Não encontrado processamento da intenção nos logs")
                return False
        else:
            print("  ❌ Nenhum stream de log encontrado")
            return False

    except Exception as e:
        print(f"  ❌ Erro ao verificar logs: {e}")
        return False


def test_director_direct_invoke():
    """Testa invocação direta do Director"""

    print("\n🧪 TESTE DIRETO: Invocação Director")
    print("=" * 60)

    lambda_client = boto3.client("lambda")
    mission_id = f"direct-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Simular evento SNS que Director deveria receber
    sns_event = {
        "Records": [
            {
                "EventSource": "aws:sns",
                "Sns": {
                    "TopicArn": "arn:aws:sns:us-east-1:481251881947:bos-persona-intention-topic-dev",
                    "Message": json.dumps(
                        {
                            "mission_id": mission_id,
                            "user_id": "test-user-001",
                            "user_intention": "Chamar elevador para o 5º andar",
                            "timestamp": datetime.now().isoformat(),
                            "context": {
                                "current_floor": 5,
                                "destination_floor": 0,
                                "building_id": "building-001",
                            },
                        }
                    ),
                },
            }
        ]
    }

    try:
        response = lambda_client.invoke(
            FunctionName="bos-agent-director-dev",
            Payload=json.dumps(sns_event),
            InvocationType="RequestResponse",
        )

        result = json.loads(response["Payload"].read())
        status_code = result.get("statusCode", "unknown")

        print(f"  ✅ Director Response: {status_code}")
        print(f"  📄 Full Response: {json.dumps(result, indent=2)}")

        if status_code == 200:
            print("  ✅ Director processou com sucesso!")
            return True
        else:
            print(f"  ⚠️  Director retornou código {status_code}")
            return False

    except Exception as e:
        print(f"  ❌ Erro na invocação direta: {e}")
        return False


if __name__ == "__main__":
    print("🚀 TESTES DE FLUXO PERSONA → DIRECTOR")
    print("=" * 80)

    # Teste 1: Fluxo via SNS
    result1 = test_persona_to_director_flow()

    # Teste 2: Invocação direta
    result2 = test_director_direct_invoke()

    print("\n" + "=" * 80)
    print("📊 RESUMO DOS TESTES")
    print("=" * 80)
    print(f"🔄 Fluxo via SNS: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"🧪 Invocação Direta: {'✅ PASS' if result2 else '❌ FAIL'}")

    if result1 and result2:
        print("\n🎯 Status: ✅ FLUXO PERSONA → DIRECTOR FUNCIONANDO")
    else:
        print("\n🎯 Status: ⚠️  NECESSITA CORREÇÕES")
