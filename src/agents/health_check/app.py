import json


def handler(event, context):
    """
    A simple handler that returns a success message.
    This acts as a health check for the API.
    """
    print("Health check endpoint was invoked successfully. The system is healthy.")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {"status": "OK", "message": "BuildingOS is up and running!"}
        ),
    }
