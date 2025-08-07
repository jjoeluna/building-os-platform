import json
import os
import boto3
import uuid
from datetime import datetime, timezone

# Initialize AWS clients outside the handler for better performance
sns = boto3.client("sns")
bedrock = boto3.client("bedrock-runtime")
dynamodb = boto3.resource("dynamodb")

# Get environment variables set by Terraform
MISSION_TOPIC_ARN = os.environ.get("MISSION_TOPIC_ARN")
INTENTION_RESULT_TOPIC_ARN = os.environ.get("INTENTION_RESULT_TOPIC_ARN")
MISSION_STATE_TABLE_NAME = os.environ.get("MISSION_STATE_TABLE_NAME")
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# DynamoDB table
mission_table = dynamodb.Table(MISSION_STATE_TABLE_NAME)


def get_available_agents():
    """
    Returns available agents and their capabilities for the new stateless architecture.
    """
    return [
        {
            "agent_name": "agent_elevator",
            "description": "Handles elevator operations. Can call elevators to specific floors and monitor their status.",
            "actions": [
                {
                    "action": "call_elevator",
                    "description": "Call an elevator to a floor. For simple calls, from_floor and to_floor should be the same.",
                    "parameters": [
                        {
                            "name": "elevator_id",
                            "type": "string",
                            "description": "The ID of the elevator to be called.",
                        },
                        {
                            "name": "from_floor",
                            "type": "integer",
                            "description": "The floor where the user is.",
                        },
                        {
                            "name": "to_floor",
                            "type": "integer",
                            "description": "Must be the same as from_floor for simple calls.",
                        },
                    ],
                },
                {
                    "action": "check_elevator_status",
                    "description": "Check current elevator position and status.",
                    "parameters": [],
                },
                {
                    "action": "list_floors",
                    "description": "List all available floors in the building.",
                    "parameters": [],
                },
                {
                    "action": "monitor_elevator_arrival",
                    "description": "Monitor if elevator has arrived at target floor and stayed for at least 5 seconds.",
                    "parameters": [
                        {
                            "name": "target_floor",
                            "type": "integer",
                            "description": "The floor to monitor for elevator arrival.",
                        },
                        {
                            "name": "mission_id",
                            "type": "string",
                            "description": "The mission ID for tracking purposes.",
                        },
                    ],
                },
            ],
        },
        {
            "agent_name": "agent_psim",
            "description": "Handles PSIM system operations including person search and access control.",
            "actions": [
                {
                    "action": "get_person_info",
                    "description": "Get information about a person from PSIM.",
                    "parameters": [
                        {
                            "name": "person_name",
                            "type": "string",
                            "description": "The name of the person to search for.",
                        }
                    ],
                },
                {
                    "action": "search_person",
                    "description": "Search for people in PSIM system.",
                    "parameters": [
                        {
                            "name": "query",
                            "type": "string",
                            "description": "Search query for finding people.",
                        }
                    ],
                },
            ],
        },
    ]


def handler(event, context):
    """
    Director Agent - Handles two types of events:
    1. New user requests (API Gateway or SNS from intention_topic)
    2. Mission results (SNS from mission_result_topic)
    """
    print(f"Director Agent invoked with event: {event}")

    try:
        # Determine event type
        if "Records" in event:
            # SNS event
            for record in event["Records"]:
                if record.get("EventSource") == "aws:sns":
                    message_body = json.loads(record["Sns"]["Message"])

                    # Check if this is a mission result (contains mission_id and completed_at)
                    if "mission_id" in message_body and "completed_at" in message_body:
                        return handle_mission_result(message_body)
                    else:
                        # This is a new intention
                        return handle_new_intention(message_body)
        else:
            # API Gateway event
            return handle_api_gateway_request(event, context)

    except Exception as e:
        print(f"Error in Director Agent: {e}")

        # Return error response based on event type
        if "Records" in event:
            raise e
        else:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"status": "ERROR", "error": str(e)}),
            }


def handle_api_gateway_request(event, context):
    """
    Handle new user request from API Gateway
    """
    query_params = event.get("queryStringParameters") or {}
    user_message = query_params.get("user_request", "No message provided.")
    check_mission = query_params.get("check_mission")
    user_id = query_params.get("user_id", f"api-user-{context.aws_request_id}")

    # Handle mission status check
    if check_mission:
        return handle_mission_status_check(check_mission)

    # Create mission and publish
    mission_id = create_and_publish_mission(user_message, user_id)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(
            {
                "status": "SUCCESS",
                "mission_id": mission_id,
                "message": "Mission created and processing started",
            }
        ),
    }


def handle_mission_status_check(mission_id: str):
    """
    Check the status of a specific mission
    """
    try:
        # Get mission from DynamoDB
        response = mission_table.get_item(Key={"mission_id": mission_id})

        if "Item" not in response:
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"error": "Mission not found"}),
            }

        mission = response["Item"]

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "mission_id": mission_id,
                    "status": mission.get("status", "unknown"),
                    "user_request": mission.get("user_request"),
                    "updated_at": mission.get("updated_at"),
                    "results": mission.get("results", []),
                }
            ),
        }

    except Exception as e:
        print(f"Error checking mission status: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": str(e)}),
        }


def handle_new_intention(intention_manifest):
    """
    Handle new intention from SNS
    """
    user_message = intention_manifest.get("message", "No message provided.")
    user_id = intention_manifest.get(
        "user_id", intention_manifest.get("session_id", "unknown-user")
    )

    # Create mission and publish
    mission_id = create_and_publish_mission(user_message, user_id)

    return {"status": "SUCCESS", "mission_id": mission_id}


def handle_mission_result(result_data):
    """
    Handle mission result from coordinator and synthesize final response
    """
    mission_id = result_data["mission_id"]
    user_id = result_data["user_id"]
    status = result_data["status"]
    tasks = result_data.get("tasks", [])

    print(f"Mission {mission_id} completed with status: {status}")

    # Synthesize a user-friendly response using Bedrock
    response_text = synthesize_response(result_data)

    # Create intention result message
    intention_result = {
        "user_id": user_id,
        "mission_id": mission_id,
        "status": status,
        "response": response_text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "agent_director",
    }

    # Publish to intention_result_topic for persona
    try:
        sns.publish(
            TopicArn=INTENTION_RESULT_TOPIC_ARN,
            Message=json.dumps(intention_result),
            Subject=f"Intention Result for Mission {mission_id}",
        )
        print(f"Published intention result for mission {mission_id} to persona")
    except Exception as e:
        print(f"Error publishing intention result: {str(e)}")

    return {
        "status": "SUCCESS",
        "message": "Mission result processed and response sent",
    }


def synthesize_response(result_data):
    """
    Use Bedrock to synthesize a user-friendly response from mission results
    """
    mission_id = result_data["mission_id"]
    status = result_data["status"]
    tasks = result_data.get("tasks", [])

    # Build context for LLM
    tasks_summary = []
    for task in tasks:
        task_info = {
            "action": task.get("action", "unknown"),
            "status": task.get("status", "unknown"),
            "result": task.get("result", {}),
        }
        tasks_summary.append(task_info)

    prompt = f"""
    Human: You are the Director Agent in a building automation system. You need to synthesize a user-friendly response based on mission results.

    Mission ID: {mission_id}
    Overall Status: {status}
    
    Task Results:
    {json.dumps(tasks_summary, indent=2)}

    Create a friendly, informative response to the user explaining what was accomplished. Be specific about results but keep it conversational and helpful. If something failed, explain what happened and suggest next steps.

    Response should be 1-3 sentences maximum.

    Assistant: """

    try:
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 200,
                    "messages": [{"role": "user", "content": prompt}],
                }
            ),
        )

        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"].strip()

    except Exception as e:
        print(f"Error synthesizing response with Bedrock: {str(e)}")
        # Fallback to simple response
        if status == "completed":
            return f"Your request has been completed successfully. Mission {mission_id} finished with all tasks done."
        else:
            return f"Your request encountered some issues. Mission {mission_id} completed with status: {status}."


def create_and_publish_mission(user_message: str, user_id: str) -> str:
    """
    Create a mission plan using Bedrock and publish to mission topic
    """
    # Generate unique mission ID
    mission_id = str(uuid.uuid4())

    # Get available agents
    agents_json = json.dumps(get_available_agents(), indent=2)

    # Build prompt for LLM
    prompt = f"""
    Human: You are the Director Agent in a building automation system. You receive user requests and create mission plans.

    Available agents and their capabilities:
    <agents>
    {agents_json}
    </agents>

    User request: "{user_message}"
    User ID: "{user_id}"
    Mission ID: "{mission_id}"

    Create a mission plan as a JSON object with this structure:
    {{
        "mission_id": "{mission_id}",
        "user_id": "{user_id}",
        "status": "pending",
        "created_at": "{datetime.now(timezone.utc).isoformat()}",
        "updated_at": "{datetime.now(timezone.utc).isoformat()}",
        "user_request": "{user_message}",
        "tasks": [
            {{
                "task_id": "task-1",
                "agent": "agent_name",
                "action": "action_name",
                "parameters": {{}},
                "status": "pending",
                "result": null,
                "started_at": null,
                "completed_at": null
            }}
        ],
        "final_result": null
    }}

    Generate ONLY the JSON mission plan. For elevator calls, remember that from_floor and to_floor should be the same for simple calls.

    Assistant:
    """

    # Invoke Bedrock
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    response = bedrock.invoke_model(
        body=json.dumps(request_body),
        modelId=BEDROCK_MODEL_ID,
        accept="application/json",
        contentType="application/json",
    )

    response_body = json.loads(response.get("body").read())
    mission_plan_text = response_body["content"][0]["text"]

    print(f"Generated mission plan: {mission_plan_text}")

    # Publish to mission topic
    sns.publish(
        TopicArn=MISSION_TOPIC_ARN,
        Message=mission_plan_text,
        Subject=f"New Mission: {mission_id}",
    )

    print(f"Published mission {mission_id} to mission topic")

    return mission_id
