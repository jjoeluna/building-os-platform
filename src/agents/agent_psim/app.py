import json
import os
import boto3
import requests
from datetime import datetime, timezone
from typing import Dict, Any

# AWS clients
sns = boto3.client("sns")

# Environment variables
PSIM_API_BASE_URL = os.environ["PSIM_API_BASE_URL"]
PSIM_API_USERNAME = os.environ["PSIM_API_USERNAME"]
PSIM_API_PASSWORD = os.environ["PSIM_API_PASSWORD"]

# New standardized topics
COORDINATOR_TASK_TOPIC_ARN = os.environ.get("COORDINATOR_TASK_TOPIC_ARN")
AGENT_TASK_RESULT_TOPIC_ARN = os.environ.get("AGENT_TASK_RESULT_TOPIC_ARN")

# Determine which architecture to use (prefer new if available)
USE_NEW_ARCHITECTURE = bool(COORDINATOR_TASK_TOPIC_ARN and AGENT_TASK_RESULT_TOPIC_ARN)
print(f"Agent PSIM using {'NEW' if USE_NEW_ARCHITECTURE else 'LEGACY'} architecture")

# Session for maintaining authentication
session = requests.Session()


def handler(event, context):
    """
    PSIM Agent - Handles PSIM-related tasks

    Supports multiple types of events:
    1. SNS events (from coordinator-task-topic or task_result_topic)
    2. Direct Lambda invocation (legacy from Coordinator Agent)
    3. API Gateway POST requests (direct API calls for debugging)
    """
    try:
        print(f"Agent PSIM received event: {json.dumps(event)}")

        # Explicitly check for API Gateway event first
        if "httpMethod" in event:
            return handle_api_request(event, context)

        # Check if this is an SNS event
        if "Records" in event:
            for record in event["Records"]:
                if record.get("EventSource") == "aws:sns":
                    topic_arn = record["Sns"]["TopicArn"]
                    message_body = json.loads(record["Sns"]["Message"])

                    print(f"Processing SNS event from topic: {topic_arn}")

                    # Check if this task is for us
                    if message_body.get("agent") == "agent_psim":
                        return handle_task_from_sns(message_body)
                    else:
                        print(
                            f"Task not for agent_psim, ignoring: {message_body.get('agent')}"
                        )
                        return {
                            "status": "IGNORED",
                            "reason": "Task not for this agent",
                        }

        # Check if this is a direct Lambda invocation from Coordinator (legacy)
        if "mission_id" in event and "task_id" in event and "action" in event:
            return handle_legacy_task(event)

        # Fallback for unknown event types
        print(f"Unknown event format: {event}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid event format"}),
        }

    except Exception as e:
        print(f"Error in PSIM agent: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def handle_task_from_sns(task_data):
    """
    Handle task from Coordinator Agent via NEW SNS architecture
    """
    try:
        # Extract task information
        mission_id = task_data["mission_id"]
        task_id = task_data["task_id"]
        action = task_data["action"]
        parameters = task_data["parameters"]

        print(f"Processing SNS task {task_id} for mission {mission_id}: {action}")

        # Execute the PSIM action
        result = execute_psim_action(action, parameters)

        # Publish task completion using new architecture
        publish_task_completion(mission_id, task_id, "completed", result)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f"Task {task_id} completed successfully", "result": result}
            ),
        }

    except Exception as e:
        print(f"Error processing SNS task: {str(e)}")

        # Try to publish failure if we have the required info
        try:
            mission_id = task_data.get("mission_id")
            task_id = task_data.get("task_id")
            if mission_id and task_id:
                publish_task_completion(
                    mission_id, task_id, "failed", {"error": str(e)}
                )
        except Exception as pub_error:
            print(f"Error publishing failure: {str(pub_error)}")

        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }


def handle_legacy_task(event):
    """
    Handle task from direct Lambda invocation (LEGACY architecture)
    """
    try:
        # Extract task information from direct event
        mission_id = event["mission_id"]
        task_id = event["task_id"]
        action = event["action"]
        parameters = event["parameters"]

        print(f"Processing LEGACY task {task_id} for mission {mission_id}: {action}")

        # Execute the PSIM action
        result = execute_psim_action(action, parameters)

        # Publish task completion using legacy architecture
        publish_task_completion(mission_id, task_id, "completed", result)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f"Task {task_id} completed successfully", "result": result}
            ),
        }

    except Exception as e:
        print(f"Error processing legacy task: {str(e)}")

        # Try to publish failure if we have the required info
        try:
            mission_id = event.get("mission_id")
            task_id = event.get("task_id")
            if mission_id and task_id:
                publish_task_completion(
                    mission_id, task_id, "failed", {"error": str(e)}
                )
        except Exception as pub_error:
            print(f"Error publishing failure: {str(pub_error)}")

        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }


def handle_api_request(event, context):
    """
    Handle direct API Gateway request for debugging/testing
    """
    try:
        # Add CORS headers
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        }

        # Handle OPTIONS requests for CORS
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"message": "CORS preflight response"}),
            }

        # Parse request body
        if "body" not in event or not event["body"]:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Request body is required"}),
            }

        body = json.loads(event["body"])

        # Validate required fields
        if "action" not in body:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Missing required field: action"}),
            }

        action = body["action"]
        parameters = body.get("parameters", {})

        print(f"Processing API request - Action: {action}, Parameters: {parameters}")

        # Execute the PSIM action
        result = execute_psim_action(action, parameters)

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(
                {
                    "message": f"PSIM action '{action}' completed successfully",
                    "action": action,
                    "result": result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
        }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Invalid JSON in request body"}),
        }
    except Exception as e:
        print(f"Error in API request: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)}),
        }


def execute_psim_action(action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute PSIM action based on the action type
    """
    if action == "get_person_info":
        return get_person_info(parameters.get("person_name"))
    elif action == "search_person":
        return search_person(parameters.get("query"))
    else:
        raise ValueError(f"Unknown PSIM action: {action}")


def get_person_info(person_name: str) -> Dict[str, Any]:
    """
    Get person information from PSIM API
    """
    try:
        # Authenticate first
        if not authenticate():
            return {
                "status": "error",
                "message": "Failed to authenticate with PSIM API",
            }

        # Search for person
        search_url = f"{PSIM_API_BASE_URL}/api/person/search"
        search_params = {"query": person_name}

        print(f"Searching for person: {person_name}")

        response = session.get(search_url, params=search_params, timeout=10)

        if response.status_code == 200:
            search_results = response.json()
            print(f"PSIM search response: {search_results}")

            if search_results and len(search_results) > 0:
                # Get detailed info for first match
                person_id = search_results[0].get("id")
                return get_person_details(person_id)
            else:
                return {
                    "status": "not_found",
                    "message": f"No person found with name: {person_name}",
                }
        else:
            error_msg = f"PSIM API search returned status {response.status_code}: {response.text}"
            print(error_msg)

            return {"status": "error", "message": error_msg}

    except requests.RequestException as e:
        error_msg = f"Network error calling PSIM API: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error in PSIM call: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg}


def get_person_details(person_id: str) -> Dict[str, Any]:
    """
    Get detailed person information by ID
    """
    try:
        details_url = f"{PSIM_API_BASE_URL}/api/person/{person_id}"

        response = session.get(details_url, timeout=10)

        if response.status_code == 200:
            person_details = response.json()

            return {
                "status": "success",
                "message": f"Person details retrieved successfully",
                "person_info": person_details,
            }
        else:
            error_msg = f"PSIM API details returned status {response.status_code}: {response.text}"
            print(error_msg)

            return {"status": "error", "message": error_msg}

    except Exception as e:
        error_msg = f"Error getting person details: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg}


def search_person(query: str) -> Dict[str, Any]:
    """
    Search for people in PSIM
    """
    try:
        # Authenticate first
        if not authenticate():
            return {
                "status": "error",
                "message": "Failed to authenticate with PSIM API",
            }

        search_url = f"{PSIM_API_BASE_URL}/api/person/search"
        search_params = {"query": query}

        print(f"Searching PSIM with query: {query}")

        response = session.get(search_url, params=search_params, timeout=10)

        if response.status_code == 200:
            search_results = response.json()

            return {
                "status": "success",
                "message": f"Search completed successfully",
                "results": search_results,
                "count": len(search_results) if search_results else 0,
            }
        else:
            error_msg = f"PSIM API search returned status {response.status_code}: {response.text}"
            print(error_msg)

            return {"status": "error", "message": error_msg}

    except Exception as e:
        error_msg = f"Error in PSIM search: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg}


def authenticate() -> bool:
    """
    Authenticate with PSIM API
    """
    try:
        auth_url = f"{PSIM_API_BASE_URL}/api/auth/login"
        auth_data = {"username": PSIM_API_USERNAME, "password": PSIM_API_PASSWORD}

        response = session.post(auth_url, json=auth_data, timeout=10)

        if response.status_code == 200:
            print("PSIM authentication successful")
            return True
        else:
            print(
                f"PSIM authentication failed: {response.status_code} - {response.text}"
            )
            return False

    except Exception as e:
        print(f"Error during PSIM authentication: {str(e)}")
        return False


def publish_task_completion(
    mission_id: str, task_id: str, status: str, result: Dict[str, Any]
) -> None:
    """
    Publish task completion using appropriate architecture
    """
    try:
        completion_message = {
            "mission_id": mission_id,
            "task_id": task_id,
            "agent": "agent_psim",
            "status": status,
            "result": result,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        if USE_NEW_ARCHITECTURE:
            # Use new agent-task-result-topic
            topic_arn = AGENT_TASK_RESULT_TOPIC_ARN
            print(
                f"Publishing task completion via NEW architecture to agent-task-result-topic"
            )
        else:
            # New architecture should always be available now
            print("ERROR: New architecture topics not available")
            raise ValueError("AGENT_TASK_RESULT_TOPIC_ARN not configured")

        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(completion_message),
            Subject=f"Task {task_id} Completion",
        )

        print(f"Published task completion for {task_id}")

    except Exception as e:
        print(f"Error publishing task completion: {str(e)}")
        # Don't raise here to avoid infinite loops
