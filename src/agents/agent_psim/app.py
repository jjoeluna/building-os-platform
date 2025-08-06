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
TASK_COMPLETION_TOPIC_ARN = os.environ["TASK_COMPLETION_TOPIC_ARN"]

# Session for maintaining authentication
session = requests.Session()


def handler(event, context):
    """
    PSIM Agent - Handles PSIM-related tasks

    Receives task from Coordinator Agent and executes PSIM operations
    """
    try:
        print(f"Agent PSIM received event: {json.dumps(event)}")

        # Extract task information
        mission_id = event["mission_id"]
        task_id = event["task_id"]
        action = event["action"]
        parameters = event["parameters"]

        print(f"Processing task {task_id} for mission {mission_id}: {action}")

        # Execute the PSIM action
        result = execute_psim_action(action, parameters)

        # Publish task completion
        publish_task_completion(mission_id, task_id, "completed", result)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f"Task {task_id} completed successfully", "result": result}
            ),
        }

    except Exception as e:
        print(f"Error in PSIM agent: {str(e)}")

        # Try to publish failure if we have the required info
        if "mission_id" in event and "task_id" in event:
            publish_task_completion(
                event["mission_id"], event["task_id"], "failed", {"error": str(e)}
            )

        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


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
    Publish task completion to the task completion topic
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

        sns.publish(
            TopicArn=TASK_COMPLETION_TOPIC_ARN,
            Message=json.dumps(completion_message),
            Subject=f"Task {task_id} Completion",
        )

        print(f"Published task completion for {task_id}")

    except Exception as e:
        print(f"Error publishing task completion: {str(e)}")
        # Don't raise here to avoid infinite loops
