import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")
connections_table = os.environ.get("CONNECTIONS_TABLE")


def handler(event, context):
    connection_id = event["requestContext"]["connectionId"]
    table = dynamodb.Table(connections_table)
    table.delete_item(Key={"connectionId": connection_id})
    print(f"Disconnected: {connection_id}")
    return {"statusCode": 200, "body": "Disconnected"}
