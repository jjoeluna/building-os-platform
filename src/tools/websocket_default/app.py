import json
import boto3
import os

sns = boto3.client("sns")
dynamodb = boto3.resource("dynamodb")
connections_table = os.environ.get("CONNECTIONS_TABLE")
chat_intention_topic_arn = os.environ.get("CHAT_INTENTION_TOPIC_ARN")


# Recebe mensagem do cliente e publica no tópico SNS
# Exemplo de payload: { "action": "sendMessage", "data": { ... } }
def handler(event, context):
    connection_id = event["requestContext"]["connectionId"]
    body = json.loads(event.get("body", "{}"))
    print(f"Received from {connection_id}: {body}")
    # Publica intenção no SNS
    sns.publish(
        TopicArn=chat_intention_topic_arn,
        Message=json.dumps({"connectionId": connection_id, "payload": body}),
    )
    return {"statusCode": 200, "body": "Message published"}
