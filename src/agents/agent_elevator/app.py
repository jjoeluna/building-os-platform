import json
import os
import boto3
import requests
import jwt
import time
from datetime import datetime, timezone
from typing import Dict, Any

# AWS clients
sns = boto3.client("sns")
events = boto3.client("events")
dynamodb = boto3.resource("dynamodb")

# Environment variables
ELEVATOR_API_BASE_URL = os.environ["ELEVATOR_API_BASE_URL"]
ELEVATOR_API_SECRET = os.environ["ELEVATOR_API_SECRET"]
TASK_COMPLETION_TOPIC_ARN = os.environ["TASK_COMPLETION_TOPIC_ARN"]
MONITORING_TABLE_NAME = os.environ.get(
    "MONITORING_TABLE_NAME", "bos-elevator-monitoring-dev"
)


def handler(event, context):
    """
    Elevator Agent - Handles elevator-related tasks and monitoring

    Can be invoked by:
    1. Coordinator Agent (for tasks)
    2. EventBridge (for monitoring)
    """
    try:
        print(f"Agent Elevator received event: {json.dumps(event)}")

        # Regular task from Coordinator Agent
        mission_id = event["mission_id"]
        task_id = event["task_id"]
        action = event["action"]
        parameters = event["parameters"]

        print(f"Processing task {task_id} for mission {mission_id}: {action}")

        # Execute the elevator action
        result = execute_elevator_action(action, parameters, mission_id)

        # Publish task completion
        publish_task_completion(mission_id, task_id, "completed", result)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f"Task {task_id} completed successfully", "result": result}
            ),
        }

    except Exception as e:
        print(f"Error in elevator agent: {str(e)}")

        # Try to publish failure if we have the required info
        if "mission_id" in event and "task_id" in event:
            publish_task_completion(
                event["mission_id"], event["task_id"], "failed", {"error": str(e)}
            )

        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def execute_elevator_action(
    action: str, parameters: Dict[str, Any], mission_id: str | None = None
) -> Dict[str, Any]:
    """
    Execute elevator action based on the action type
    """
    if action == "call_elevator":
        from_floor = parameters.get("from_floor")
        to_floor = parameters.get("to_floor")
        if from_floor is None or to_floor is None:
            raise ValueError("Missing required parameters for call_elevator")
        result = call_elevator(from_floor, to_floor)

        # If successful, start monitoring
        if result.get("status") == "success" and mission_id:
            start_monitoring(mission_id, to_floor)
        elif result.get("status") == "error" and mission_id:
            # Send error notification to user
            error_message = result.get("message", "Erro desconhecido")
            if result.get("offline"):
                notify_user(mission_id, "error", f"[ERRO] {error_message}")
            else:
                notify_user(mission_id, "error", f"[ERRO] {error_message}")

        return result

    elif action == "check_elevator_status":
        return check_elevator_status()
    elif action == "list_floors":
        return list_floors()
    elif action == "monitor_elevator_arrival":
        target_floor = parameters.get("target_floor")
        mission_id_param = parameters.get("mission_id")
        if target_floor is None or mission_id_param is None:
            raise ValueError("Missing required parameters for monitor_elevator_arrival")
        return monitor_elevator_arrival(target_floor, str(mission_id_param))
    elif action == "list_active_monitoring":
        return list_active_monitoring()
    else:
        raise ValueError(f"Unknown elevator action: {action}")


def call_elevator(from_floor, to_floor) -> Dict[str, Any]:
    """
    Call elevator using the elevator API
    Uses the correct endpoint format: /elevator/{id}/call
    Now includes retry logic for better reliability
    """
    try:
        # Retry logic for API calls
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                # Generate JWT token for authentication
                token = generate_jwt_token()

                # Prepare API request
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }

                # Correct API endpoint with elevator ID
                elevator_id = "010504"  # ID correto fornecido
                url = f"{ELEVATOR_API_BASE_URL}/elevator/{elevator_id}/call"

                # Correct payload format according to documentation
                payload = {
                    "from": from_floor,
                    "to": to_floor,
                }

                print(f"Calling elevator API (attempt {attempt + 1}): {url}")
                print(f"Payload: {payload}")

                # Make API call
                response = requests.post(url, json=payload, headers=headers, timeout=10)

                # Check if response indicates elevator is offline
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if (
                            isinstance(result, list)
                            and len(result) > 0
                            and "offline" in str(result[0]).lower()
                        ):
                            print("Elevator is offline during call")
                            return {
                                "status": "error",
                                "message": "Elevador offline - não é possível fazer a chamada",
                                "floor": from_floor,
                                "offline": True,
                            }
                    except:
                        pass  # Continue with normal processing

                if response.status_code == 204:  # Success is 204 No Content
                    print(f"Elevator API success: {response.status_code}")

                    return {
                        "status": "success",
                        "message": f"Elevator called from floor {from_floor} to floor {to_floor}",
                        "floor": from_floor,
                        "target_floor": to_floor,
                    }
                elif response.status_code == 400:
                    response_text = response.text
                    print(f"API returned 400 (attempt {attempt + 1}): {response_text}")

                    if "Elevador não permitido" in response_text:
                        # API externa não tem elevador configurado - simular sucesso para demo
                        print(
                            f"External API not configured, simulating success for demo"
                        )

                        return {
                            "status": "success",
                            "message": f"Elevator called from floor {from_floor} to floor {to_floor} (simulated)",
                            "floor": from_floor,
                            "target_floor": to_floor,
                            "note": "External API not configured - using simulation",
                        }
                    elif (
                        "Elevador offline" in response_text
                        and attempt < max_retries - 1
                    ):
                        # Retry for elevator offline errors
                        print(f"Elevator offline, retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        # Final attempt or non-retryable error
                        error_msg = f"Elevator API returned status {response.status_code}: {response_text}"
                        print(error_msg)
                        return {
                            "status": "error",
                            "message": error_msg,
                            "floor": from_floor,
                        }
                else:
                    # Non-400 errors
                    error_msg = f"Elevator API returned status {response.status_code}: {response.text}"
                    print(error_msg)

                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        return {
                            "status": "error",
                            "message": error_msg,
                            "floor": from_floor,
                        }

            except requests.RequestException as e:
                error_msg = f"Network error on attempt {attempt + 1}: {str(e)}"
                print(error_msg)

                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return {
                        "status": "error",
                        "message": f"Network error calling elevator API: {str(e)}",
                        "floor": from_floor,
                    }

        # If we reach here, all retries failed
        return {
            "status": "error",
            "message": "All API call attempts failed",
            "floor": from_floor,
        }

    except requests.RequestException as e:
        error_msg = f"Network error calling elevator API: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg, "floor": from_floor}
    except Exception as e:
        error_msg = f"Unexpected error in elevator call: {str(e)}"
        print(error_msg)

        return {"status": "error", "message": error_msg, "floor": from_floor}


def check_elevator_status() -> Dict[str, Any]:
    """
    Check current elevator status and position
    Uses the correct endpoint format: /elevator/{id}/status

    Improvements:
    - Retry logic for empty floor responses
    - Convert string floor to int
    - Validate elevator is stopped before trusting floor data
    """
    try:
        # Generate JWT token for authentication
        token = generate_jwt_token()

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Correct API endpoint with elevator ID
        elevator_id = "010504"  # ID correto fornecido
        url = f"{ELEVATOR_API_BASE_URL}/elevator/{elevator_id}/status"

        print(f"Checking elevator status: {url}")

        # Retry logic for API calls
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                # Make API call
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    result = response.json()
                    print(f"Elevator status response (attempt {attempt + 1}): {result}")

                    # Check if elevator is offline
                    if (
                        isinstance(result, list)
                        and len(result) > 0
                        and "offline" in str(result[0]).lower()
                    ):
                        print("Elevator is offline")
                        return {
                            "status": "error",
                            "message": "Elevador offline",
                            "elevator_status": "offline",
                            "offline": True,
                        }

                    # For offline response, result is a list, not a dict
                    if isinstance(result, list):
                        print(f"Unexpected list response: {result}")
                        return {
                            "status": "error",
                            "message": f"Resposta inesperada da API: {result}",
                            "elevator_status": "unknown",
                        }

                    # Extract and validate floor (only for dict responses)
                    floor_raw = result.get("floor", "")
                    elevator_status = result.get("status", "unknown")
                    direction = result.get("direction", "unknown")

                    # Handle empty floor - retry if not last attempt
                    if not floor_raw or floor_raw == "":
                        if attempt < max_retries - 1:
                            print(
                                f"Empty floor received, retrying in {retry_delay} seconds..."
                            )
                            time.sleep(retry_delay)
                            continue
                        else:
                            print("Empty floor received on final attempt")
                            return {
                                "status": "error",
                                "message": "API returned empty floor after retries",
                                "elevator_status": elevator_status,
                                "direction": direction,
                            }

                    # Convert floor to string and validate format
                    try:
                        # Validate that it's a valid number but keep as string
                        float(floor_raw)  # Test if it's a valid number
                        current_floor = str(floor_raw).strip()
                    except (ValueError, TypeError):
                        print(f"Invalid floor format: {floor_raw}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        else:
                            return {
                                "status": "error",
                                "message": f"Invalid floor format: {floor_raw}",
                                "elevator_status": elevator_status,
                            }

                    # Determine if we should trust the floor data
                    # Only trust floor when elevator is stopped
                    floor_reliable = elevator_status.lower() in [
                        "stopped",
                        "idle",
                        "stoping",
                    ]

                    return {
                        "status": "success",
                        "current_floor": current_floor,
                        "direction": direction,
                        "elevator_status": elevator_status,
                        "door_sensor": result.get("doorSensor", "unknown"),
                        "floor_reliable": floor_reliable,
                        "api_response": result,
                    }

                else:
                    error_msg = (
                        f"API returned status {response.status_code}: {response.text}"
                    )
                    print(error_msg)
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue

            except requests.RequestException as e:
                error_msg = f"Network error on attempt {attempt + 1}: {str(e)}"
                print(error_msg)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

        # If all retries failed, return error
        return {
            "status": "error",
            "message": "All API call attempts failed",
        }

    except Exception as e:
        error_msg = f"Unexpected error checking elevator status: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}


def list_floors() -> Dict[str, Any]:
    """
    List available floors in the building
    Uses the correct endpoint format: /elevator/{id}/floors
    """
    try:
        # Generate JWT token for authentication
        token = generate_jwt_token()

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Correct API endpoint with elevator ID
        elevator_id = "010504"  # ID correto fornecido
        url = f"{ELEVATOR_API_BASE_URL}/elevator/{elevator_id}/floors"

        print(f"Listing floors: {url}")

        # Make API call
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"Floors list response: {result}")

            return {
                "status": "success",
                "floors": result,
                "api_response": result,
            }
        elif response.status_code == 400 and "Elevador não permitido" in response.text:
            # API externa não tem elevador configurado - simular lista para demo
            print(f"External API not configured, simulating floors for demo")

            simulated_floors = [
                {"floor": 1, "description": "Térreo"},
                {"floor": 2, "description": "1º Andar"},
                {"floor": 3, "description": "2º Andar"},
                {"floor": 4, "description": "3º Andar"},
                {"floor": 5, "description": "4º Andar"},
            ]

            return {
                "status": "success",
                "floors": simulated_floors,
                "note": "External API not configured - using simulation",
            }
        else:
            error_msg = (
                f"Elevator API returned status {response.status_code}: {response.text}"
            )
            print(error_msg)
            return {"status": "error", "message": error_msg}

    except requests.RequestException as e:
        error_msg = f"Network error listing floors: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error listing floors: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}


def list_active_monitoring() -> Dict[str, Any]:
    """
    List all active monitoring missions from DynamoDB
    Useful for debugging and recovery
    """
    try:
        table = dynamodb.Table(MONITORING_TABLE_NAME)

        response = table.scan(
            FilterExpression="attribute_exists(mission_id) AND #status = :status",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":status": "monitoring"},
        )

        active_missions = []
        for item in response["Items"]:
            mission_info = {
                "mission_id": item["mission_id"],
                "target_floor": item.get("target_floor"),
                "start_time": item.get("start_time"),
                "last_floor": item.get("last_floor"),
                "retry_count": item.get("retry_count", 0),
                "elevator_status": item.get("elevator_status", "unknown"),
            }
            active_missions.append(mission_info)

        return {
            "status": "success",
            "active_monitoring_count": len(active_missions),
            "active_missions": active_missions,
        }

    except Exception as e:
        error_msg = f"Error listing active monitoring: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}


def monitor_elevator_arrival(target_floor, mission_id: str) -> Dict[str, Any]:
    """
    Monitor elevator arrival at target floor
    Checks if elevator stays at target floor for at least 5 seconds
    """
    try:
        import time

        print(f"Monitoring elevator arrival at floor {target_floor}")

        # Check if elevator is already at target floor
        status = check_elevator_status()
        if status["status"] != "success":
            return {"status": "error", "message": "Could not check elevator status"}

        current_floor = status.get("current_floor")

        if str(current_floor) == str(target_floor):
            # Verify elevator stays for 5 seconds
            time.sleep(5)

            # Check again
            status_after = check_elevator_status()
            if status_after["status"] == "success" and str(
                status_after.get("current_floor")
            ) == str(target_floor):

                return {
                    "status": "success",
                    "message": f"Elevator arrived at floor {target_floor}",
                    "arrived": True,
                    "floor": target_floor,
                }
            else:
                return {
                    "status": "monitoring",
                    "message": f"Elevator moved from floor {target_floor}",
                    "arrived": False,
                    "floor": current_floor,
                }
        else:
            return {
                "status": "monitoring",
                "message": f"Elevator not yet at floor {target_floor} (currently at {current_floor})",
                "arrived": False,
                "current_floor": current_floor,
                "target_floor": target_floor,
            }

    except Exception as e:
        error_msg = f"Error monitoring elevator arrival: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}


def generate_jwt_token() -> str:
    """
    Generate JWT token for elevator API authentication
    """
    try:
        payload = {
            "iss": "building-os",
            "aud": "elevator-api",
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": datetime.now(timezone.utc).timestamp() + 300,  # 5 minutes
        }

        token = jwt.encode(payload, ELEVATOR_API_SECRET, algorithm="HS256")
        return token

    except Exception as e:
        print(f"Error generating JWT token: {str(e)}")
        raise


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
            "agent": "agent_elevator",
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


def start_monitoring(mission_id: str, target_floor) -> None:
    """
    Start monitoring elevator arrival with continuous polling
    This function will:
    1. Save monitoring state to DynamoDB for persistence
    2. Block and poll every 1 second until elevator arrives
    3. Update DynamoDB with progress
    4. Clean up DynamoDB when done
    """
    try:
        # Save initial monitoring state to DynamoDB
        table = dynamodb.Table(MONITORING_TABLE_NAME)

        monitoring_state = {
            "mission_id": mission_id,
            "target_floor": target_floor,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "monitoring",
            "last_floor": None,
            "retry_count": 0,
            "ttl": int(
                (datetime.now(timezone.utc).timestamp() + 600)
            ),  # 10 minutes TTL
        }

        table.put_item(Item=monitoring_state)
        print(f"Saved monitoring state for mission {mission_id} to DynamoDB")

        print(
            f"Starting continuous monitoring for mission {mission_id} to floor {target_floor}"
        )

        start_time = datetime.now(timezone.utc)
        retry_count = 0
        max_retries = 5
        timeout_seconds = 300  # 5 minutes

        while True:
            # Check timeout
            elapsed_time = datetime.now(timezone.utc) - start_time
            if elapsed_time.total_seconds() > timeout_seconds:
                notify_user(
                    mission_id,
                    "timeout",
                    "[TIMEOUT] Elevador demorou mais de 5 minutos",
                )
                cleanup_monitoring_state(mission_id)
                print(f"Monitoring timeout for mission {mission_id}")
                return

            # Check elevator status
            status_result = check_elevator_status()

            if status_result.get("status") != "success":
                retry_count += 1
                print(
                    f"Error checking elevator status (attempt {retry_count}/{max_retries}): {status_result.get('message', 'Unknown error')}"
                )

                # Update retry count in DynamoDB
                table.update_item(
                    Key={"mission_id": mission_id},
                    UpdateExpression="SET retry_count = :retry",
                    ExpressionAttributeValues={":retry": retry_count},
                )

                if retry_count >= max_retries:
                    notify_user(
                        mission_id,
                        "error",
                        "[ERRO] Nao foi possivel monitorar o elevador apos 5 tentativas",
                    )
                    cleanup_monitoring_state(mission_id)
                    print(f"Max retries reached for mission {mission_id}")
                    return

                time.sleep(1)  # Wait before retry
                continue

            # Reset retry count on successful API call
            retry_count = 0

            current_floor = status_result.get("current_floor")
            floor_reliable = status_result.get("floor_reliable", False)
            elevator_status = status_result.get("elevator_status", "unknown")

            print(
                f"Mission {mission_id}: Floor {current_floor}, Status: {elevator_status}, Reliable: {floor_reliable}, Target: {target_floor}"
            )

            # Update DynamoDB with current status
            table.update_item(
                Key={"mission_id": mission_id},
                UpdateExpression="SET last_floor = :floor, retry_count = :retry, elevator_status = :status",
                ExpressionAttributeValues={
                    ":floor": current_floor,
                    ":retry": 0,
                    ":status": elevator_status,
                },
            )

            # Only process floor comparison when elevator is stopped and floor data is reliable
            if not floor_reliable:
                print(
                    f"Elevator not stopped ({elevator_status}) - continuing monitoring"
                )
                time.sleep(1)
                continue

            # Check if elevator arrived at target floor (elevator is stopped and at correct floor)
            if current_floor == str(target_floor):
                print(
                    f"Elevator arrived at target floor {target_floor} (status: {elevator_status})"
                )

                notify_user(
                    mission_id,
                    "arrived",
                    f"[CHEGOU] Elevador chegou no andar {target_floor}!",
                )
                cleanup_monitoring_state(mission_id)
                print(
                    f"Elevator arrived at target floor {target_floor} for mission {mission_id}"
                )
                return
            else:
                print(
                    f"Elevator at floor {current_floor}, target is {target_floor} - continuing monitoring"
                )

            # Wait 1 second before next check
            time.sleep(1)

    except Exception as e:
        print(f"Error in monitoring: {str(e)}")
        notify_user(mission_id, "error", f"[ERRO] Erro no monitoramento: {str(e)}")
        cleanup_monitoring_state(mission_id)
        raise


def cleanup_monitoring_state(mission_id: str) -> None:
    """
    Remove monitoring state from DynamoDB when done
    """
    try:
        table = dynamodb.Table(MONITORING_TABLE_NAME)
        table.delete_item(Key={"mission_id": mission_id})
        print(f"Removed monitoring state for mission {mission_id}")
    except Exception as e:
        print(f"Error cleaning up monitoring state for mission {mission_id}: {str(e)}")
        # Don't raise - cleanup is best effort


def notify_user(mission_id: str, notification_type: str, message: str) -> None:
    """
    Notify user about monitoring status via SNS
    """
    try:
        notification_message = {
            "mission_id": mission_id,
            "notification_type": notification_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "agent_elevator",
        }

        sns.publish(
            TopicArn=TASK_COMPLETION_TOPIC_ARN,
            Message=json.dumps(notification_message),
            Subject=f"Elevator Monitoring Update - {mission_id}",
        )

        print(f"Sent notification for mission {mission_id}: {message}")

    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        # Don't raise - notification failure shouldn't break monitoring
