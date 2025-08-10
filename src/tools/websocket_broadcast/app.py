import json
import boto3
import os

# DynamoDB para buscar conexões
# API Gateway Management API para enviar mensagens

dynamodb = boto3.resource("dynamodb")
connections_table = os.environ.get("CONNECTIONS_TABLE")


def handler(event, context):
    # SNS pode enviar múltiplos registros
    for record in event.get("Records", []):
        message = json.loads(record["Sns"]["Message"])
        connection_id = message.get("connectionId")
        payload = message.get("payload")
        api_endpoint = os.environ.get("WEBSOCKET_API_ENDPOINT")
        apigw = boto3.client("apigatewaymanagementapi", endpoint_url=api_endpoint)
        try:
            apigw.post_to_connection(
                ConnectionId=connection_id, Data=json.dumps(payload).encode("utf-8")
            )
            print(f"Sent to {connection_id}: {payload}")
        except Exception as e:
            print(f"Error sending to {connection_id}: {e}")
    return {"statusCode": 200, "body": "Broadcast complete"}
