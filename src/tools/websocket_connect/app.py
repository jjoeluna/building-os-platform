import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")
connections_table = os.environ.get("CONNECTIONS_TABLE")


def handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        connection_id = event["requestContext"]["connectionId"]
        table = dynamodb.Table(connections_table)
        table.put_item(Item={"connectionId": connection_id})
        print(f"Connected: {connection_id}")
        return {"statusCode": 200, "body": "Connected"}
    except Exception as e:
        print(f"[ERROR] Exception in websocket_connect handler: {e}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
