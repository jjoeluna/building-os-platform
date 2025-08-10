#!/usr/bin/env python3
"""
Debug test for Persona Agent
"""

import json
import boto3
from datetime import datetime


def test_persona_direct_invoke():
    """Test direct Lambda invocation"""
    lambda_client = boto3.client("lambda")

    # Test with SNS event structure
    sns_event = {
        "Records": [
            {
                "EventSource": "aws:sns",
                "Sns": {
                    "TopicArn": "arn:aws:sns:us-east-1:481251881947:bos-persona-intention-topic-dev",
                    "Message": json.dumps(
                        {
                            "mission_id": f"debug-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                            "user_id": "test-user-001",
                            "intention": "Chamar elevador para o 5º andar",
                            "timestamp": datetime.now().isoformat(),
                            "test_mode": True,
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

    print("🧪 Testing Persona Agent Direct Invoke")
    print(f"📋 Event: {json.dumps(sns_event, indent=2)}")

    try:
        response = lambda_client.invoke(
            FunctionName="bos-agent-persona-dev",
            Payload=json.dumps(sns_event),
            InvocationType="RequestResponse",
        )

        result = json.loads(response["Payload"].read())
        status_code = result.get("statusCode", "unknown")

        print(f"✅ Response Status: {status_code}")
        print(f"📄 Full Response: {json.dumps(result, indent=2)}")

        if response.get("FunctionError"):
            print(f"❌ Function Error: {response['FunctionError']}")

        return result

    except Exception as e:
        print(f"❌ Invoke failed: {e}")
        return None


if __name__ == "__main__":
    test_persona_direct_invoke()
