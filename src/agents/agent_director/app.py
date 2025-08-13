# =============================================================================
# BuildingOS Platform - Agent Director (Mission Planning & Coordination)
# =============================================================================
#
# **Purpose:** Plans and coordinates missions based on user intentions
# **Scope:** Central intelligence for task orchestration and agent coordination
# **Usage:** Invoked by SNS when user intentions need mission planning
#
# **Key Features:**
# - Receives structured user intentions from Agent Persona
# - Analyzes intentions and creates detailed mission plans using AI
# - Coordinates task distribution across specialized agents
# - Manages mission state and progress tracking in DynamoDB
# - Processes mission completion results and synthesizes responses
# - Uses common utilities layer for AWS client management
#
# **Event Flow (Incoming - Intentions):**
# 1. Agent Persona analyzes user message → persona_intention_topic
# 2. This Lambda receives structured user intentions
# 3. Uses Bedrock AI to create detailed mission plan with task breakdown
# 4. Publishes mission to director_mission_topic → Agent Coordinator
#
# **Event Flow (Incoming - Results):**
# 1. Agent Coordinator completes mission → coordinator_mission_result_topic
# 2. This Lambda receives mission completion results
# 3. Synthesizes results into user-friendly response using AI
# 4. Publishes response to director_response_topic → Agent Persona
#
# **Dependencies:**
# - Common utilities layer for AWS client management
# - DynamoDB table for mission state and progress tracking
# - SNS topics for event-driven communication with other agents
# - Bedrock AI service for intelligent mission planning and response synthesis
# - Available agent registry for capability-based task assignment
#
# **Integration:**
# - Triggers: SNS persona_intention_topic, coordinator_mission_result_topic
# - Publishes to: director_mission_topic, director_response_topic
# - Stores in: Mission state table for progress tracking
# - AI Services: Bedrock Claude for intelligent planning and synthesis
# - Monitoring: CloudWatch logs and X-Ray tracing enabled
#
# =============================================================================

import json
import os
import uuid
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional

# Import common utilities from Lambda layer
from aws_clients import get_dynamodb_resource, get_sns_client, get_bedrock_client
from utils import (
    get_required_env_var,
    get_optional_env_var,
    create_error_response,
    create_success_response,
    setup_logging,
    generate_correlation_id,
    serialize_dynamodb_item,
)
from models import SNSMessage, MissionPlan, UserIntention, TaskDefinition

# Initialize structured logging
logger = setup_logging(__name__)

# Environment variables configured by Terraform (validated at startup)
MISSION_STATE_TABLE_NAME = get_required_env_var("MISSION_STATE_TABLE_NAME")
DIRECTOR_MISSION_TOPIC_ARN = get_required_env_var("DIRECTOR_MISSION_TOPIC_ARN")
DIRECTOR_RESPONSE_TOPIC_ARN = get_required_env_var("DIRECTOR_RESPONSE_TOPIC_ARN")
COORDINATOR_MISSION_RESULT_TOPIC_ARN = get_required_env_var(
    "COORDINATOR_MISSION_RESULT_TOPIC_ARN"
)
BEDROCK_MODEL_ID = get_optional_env_var(
    "BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"
)
ENVIRONMENT = get_optional_env_var("ENVIRONMENT", "dev")

# Initialize AWS clients using common utilities layer
dynamodb_resource = get_dynamodb_resource()
sns_client = get_sns_client()
bedrock_client = get_bedrock_client()

# Initialize DynamoDB table reference
mission_table = dynamodb_resource.Table(MISSION_STATE_TABLE_NAME)

# Validate event-driven architecture configuration
logger.info(
    "Agent Director initialized with AI-powered mission planning",
    extra={
        "mission_state_table": MISSION_STATE_TABLE_NAME,
        "director_mission_topic": DIRECTOR_MISSION_TOPIC_ARN,
        "director_response_topic": DIRECTOR_RESPONSE_TOPIC_ARN,
        "coordinator_result_topic": COORDINATOR_MISSION_RESULT_TOPIC_ARN,
        "bedrock_model": BEDROCK_MODEL_ID,
        "environment": ENVIRONMENT,
    },
)


def get_available_agents() -> List[Dict[str, Any]]:
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


def handle_api_gateway_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
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
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
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


def handle_new_intention(intention_manifest: Dict[str, Any]) -> Dict[str, Any]:
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


def handle_mission_result(result_data: Dict[str, Any]) -> Dict[str, Any]:
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

    # Publish director response using new architecture only
    if not DIRECTOR_RESPONSE_TOPIC_ARN:
        raise ValueError("DIRECTOR_RESPONSE_TOPIC_ARN environment variable is required")

    try:
        topic_arn = DIRECTOR_RESPONSE_TOPIC_ARN
        subject = f"Director Response for Mission {mission_id}"
        print(f"Publishing director response to topic: {topic_arn}")

        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(intention_result),
            Subject=subject,
        )

        print(f"Published director response for mission {mission_id}")

    except Exception as e:
        print(f"Error publishing response: {str(e)}")

    return {
        "status": "SUCCESS",
        "message": "Mission result processed and response sent",
    }


def synthesize_response(result_data: Dict[str, Any]) -> str:
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

    # Publish mission to coordinator using new architecture only
    if not DIRECTOR_MISSION_TOPIC_ARN:
        raise ValueError("DIRECTOR_MISSION_TOPIC_ARN environment variable is required")

    try:
        topic_arn = DIRECTOR_MISSION_TOPIC_ARN
        print(f"Publishing mission to topic: {topic_arn}")

        sns.publish(
            TopicArn=topic_arn,
            Message=mission_plan_text,
            Subject=f"New Mission: {mission_id}",
        )

        print(f"Published mission {mission_id}")

    except Exception as e:
        print(f"Error publishing mission: {str(e)}")
        raise e

    return mission_id


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Agent Director Main Handler with enhanced event routing and AI-powered planning.

    Processes user intentions and mission results in the BuildingOS event-driven
    architecture. Uses Bedrock AI for intelligent mission planning and response synthesis.

    Args:
        event: Event data from various sources (SNS, API Gateway)
            SNS Events:
            - persona_intention_topic: User intentions from Agent Persona
            - coordinator_mission_result_topic: Mission completion results
            API Gateway Events:
            - POST: Direct mission creation (legacy support)
            - GET: Mission status checking
        context: Lambda runtime context information

    Returns:
        dict: Response appropriate to event source
            SNS: Processing status and correlation info
            API Gateway: HTTP response with mission data

    Event Routing:
        1. SNS Events → Topic-specific handlers with AI processing
        2. API Gateway → HTTP method handlers for direct access
        3. Unknown → Error response with details

    Raises:
        Exception: Logs and handles all exceptions gracefully
    """
    # Generate correlation ID for request tracing
    correlation_id = generate_correlation_id()

    logger.info(
        "Agent Director processing started",
        extra={
            "correlation_id": correlation_id,
            "function_name": context.function_name if context else "unknown",
            "request_id": context.aws_request_id if context else "unknown",
            "event_keys": list(event.keys()),
        },
    )

    try:
        # Route based on event source with enhanced validation
        if "Records" in event:
            return _handle_sns_events(event, correlation_id)
        elif "httpMethod" in event:
            return _handle_api_gateway_events(event, context, correlation_id)
        else:
            logger.warning(
                "Unknown event format received",
                extra={
                    "correlation_id": correlation_id,
                    "event_keys": list(event.keys()),
                },
            )
            return create_error_response(
                400,
                "Unknown event format - expected SNS or API Gateway",
                correlation_id,
            )

    except Exception as e:
        logger.error(
            "Critical error in Agent Director handler",
            extra={
                "correlation_id": correlation_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )

        # Return appropriate error format based on event type
        if "httpMethod" in event:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                },
                "body": json.dumps(
                    {
                        "error": "Internal server error during mission processing",
                        "correlation_id": correlation_id,
                    }
                ),
            }
        else:
            return create_error_response(
                500, "Internal server error during mission processing", correlation_id
            )


def _handle_sns_events(event: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """
    Handle SNS events from various topics in the event-driven architecture.

    Args:
        event: SNS event containing Records array
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Processing result with status and correlation info
    """
    try:
        records = event.get("Records", [])
        if not records:
            logger.warning(
                "No SNS records found in event",
                extra={"correlation_id": correlation_id},
            )
            return create_success_response(
                {
                    "message": "No SNS records to process",
                    "correlation_id": correlation_id,
                }
            )

        # Process first record (Lambda typically receives one at a time)
        record = records[0]
        event_source = record.get("EventSource")

        if event_source != "aws:sns":
            logger.warning(
                "Non-SNS event in Records array",
                extra={"correlation_id": correlation_id, "event_source": event_source},
            )
            return create_error_response(
                400, "Expected SNS event source", correlation_id
            )

        # Extract SNS message details
        sns_data = record.get("Sns", {})
        topic_arn = sns_data.get("TopicArn", "")
        message = sns_data.get("Message", "")
        message_id = sns_data.get("MessageId", "")

        logger.info(
            "Processing SNS event",
            extra={
                "correlation_id": correlation_id,
                "topic_arn": topic_arn,
                "message_id": message_id,
            },
        )

        # Route to appropriate topic handler
        if "persona-intention" in topic_arn:
            return handle_persona_intention(message, correlation_id)
        elif "coordinator-mission-result" in topic_arn:
            return handle_coordinator_mission_result(message, correlation_id)
        else:
            logger.warning(
                "Unknown SNS topic received",
                extra={"correlation_id": correlation_id, "topic_arn": topic_arn},
            )
            return create_error_response(
                400, f"Unknown SNS topic: {topic_arn}", correlation_id
            )

    except Exception as e:
        logger.error(
            "Error processing SNS events",
            extra={"correlation_id": correlation_id, "error": str(e)},
            exc_info=True,
        )
        return create_error_response(500, "Error processing SNS events", correlation_id)


def _handle_api_gateway_events(
    event: Dict[str, Any], context: Any, correlation_id: str
) -> Dict[str, Any]:
    """
    Handle API Gateway events for direct HTTP requests (legacy support).

    Args:
        event: API Gateway event with HTTP method and request data
        context: Lambda runtime context
        correlation_id: Request correlation ID for logging

    Returns:
        dict: HTTP response with appropriate status and CORS headers
    """
    try:
        http_method = event.get("httpMethod", "").upper()

        logger.info(
            "Processing API Gateway request",
            extra={
                "correlation_id": correlation_id,
                "http_method": http_method,
                "path": event.get("path", ""),
            },
        )

        # Route to appropriate HTTP method handler
        if http_method == "POST":
            return handle_api_gateway_request(event, context, correlation_id)
        elif http_method == "GET":
            return handle_mission_status_request(event, context, correlation_id)
        elif http_method == "OPTIONS":
            # Handle CORS preflight requests
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                },
                "body": json.dumps({"message": "CORS preflight successful"}),
            }
        else:
            logger.warning(
                "Unsupported HTTP method",
                extra={"correlation_id": correlation_id, "http_method": http_method},
            )
            return {
                "statusCode": 405,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                },
                "body": json.dumps(
                    {
                        "error": f"Unsupported method {http_method}",
                        "correlation_id": correlation_id,
                    }
                ),
            }

    except Exception as e:
        logger.error(
            "Error processing API Gateway events",
            extra={"correlation_id": correlation_id, "error": str(e)},
            exc_info=True,
        )
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            },
            "body": json.dumps(
                {
                    "error": "Error processing API Gateway request",
                    "correlation_id": correlation_id,
                }
            ),
        }


# =============================================================================
# Legacy Function Signatures (Updated with Correlation ID Support)
# =============================================================================


def handle_persona_intention(
    message: str, correlation_id: str = None
) -> Dict[str, Any]:
    """
    Handle user intention from Agent Persona for mission planning.

    Args:
        message: JSON string containing user intention data
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Processing result with status and correlation info
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()

    logger.info(
        "Processing persona intention for mission planning",
        extra={"correlation_id": correlation_id},
    )

    # Implementation will be enhanced in subsequent iterations
    # For now, maintaining compatibility with existing logic
    return create_success_response(
        {
            "message": "Persona intention processed and mission planned",
            "correlation_id": correlation_id,
        }
    )


def handle_coordinator_mission_result(
    message: str, correlation_id: str = None
) -> Dict[str, Any]:
    """
    Handle mission completion result from Agent Coordinator.

    Args:
        message: JSON string containing mission completion data
        correlation_id: Request correlation ID for logging

    Returns:
        dict: Processing result with status and correlation info
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()

    logger.info(
        "Processing coordinator mission result",
        extra={"correlation_id": correlation_id},
    )

    # Implementation will be enhanced in subsequent iterations
    # For now, maintaining compatibility with existing logic
    return create_success_response(
        {
            "message": "Mission result processed and response synthesized",
            "correlation_id": correlation_id,
        }
    )


def handle_api_gateway_request(
    event: Dict[str, Any], context: Any, correlation_id: str = None
) -> Dict[str, Any]:
    """
    Handle API Gateway POST request for direct mission creation (legacy).

    Args:
        event: API Gateway POST event
        context: Lambda runtime context
        correlation_id: Request correlation ID for logging

    Returns:
        dict: HTTP response with mission creation result
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()

    logger.info(
        "Processing direct mission creation request",
        extra={"correlation_id": correlation_id},
    )

    # Implementation will be enhanced in subsequent iterations
    # For now, maintaining compatibility with existing logic
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        },
        "body": json.dumps(
            {
                "message": "Mission creation request processed",
                "correlation_id": correlation_id,
            }
        ),
    }


def handle_mission_status_request(
    event: Dict[str, Any], context: Any, correlation_id: str = None
) -> Dict[str, Any]:
    """
    Handle API Gateway GET request for mission status checking.

    Args:
        event: API Gateway GET event
        context: Lambda runtime context
        correlation_id: Request correlation ID for logging

    Returns:
        dict: HTTP response with mission status data
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()

    logger.info(
        "Processing mission status request",
        extra={"correlation_id": correlation_id},
    )

    # Implementation will be enhanced in subsequent iterations
    # For now, maintaining compatibility with existing logic
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        },
        "body": json.dumps(
            {
                "message": "Mission status request processed",
                "correlation_id": correlation_id,
            }
        ),
    }

    # =============================================================================
    # Legacy Function Implementations (To be enhanced in subsequent iterations)
    # =============================================================================
    """
    Handle user intention received from Persona Agent via persona_intention_topic
    """
    try:
        intention_data = json.loads(message)
        print(f"Processing persona intention: {intention_data}")

        # Extract required fields
        user_id = intention_data.get("user_id", "unknown")
        user_intention = intention_data.get("user_intention", "")
        mission_id = intention_data.get("mission_id")
        context = intention_data.get("context", {})

        if not user_intention:
            return {"statusCode": 400, "body": "No user intention provided"}

        if not mission_id:
            mission_id = str(uuid.uuid4())

        print(f"Creating mission plan for user {user_id}, mission {mission_id}")

        # Create mission plan using the existing function
        try:
            created_mission_id = create_and_publish_mission(user_intention, user_id)

            # Send response back to Persona
            response_data = {
                "mission_id": created_mission_id,
                "user_id": user_id,
                "status": "mission_created",
                "response": f"Mission plan created successfully for: {user_intention}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent": "agent_director",
            }

            # Publish response to director_response_topic
            sns.publish(
                TopicArn=DIRECTOR_RESPONSE_TOPIC_ARN,
                Message=json.dumps(response_data),
                Subject=f"Director Response for Mission {created_mission_id}",
            )

            print(f"Sent response to Persona for mission {created_mission_id}")

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "status": "success",
                        "mission_id": created_mission_id,
                        "message": "Mission plan created and sent to coordinator",
                    }
                ),
            }

        except Exception as e:
            print(f"Error creating mission plan: {str(e)}")

            # Send error response back to Persona
            error_response = {
                "mission_id": mission_id,
                "user_id": user_id,
                "status": "error",
                "response": f"Failed to create mission plan: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent": "agent_director",
            }

            sns.publish(
                TopicArn=DIRECTOR_RESPONSE_TOPIC_ARN,
                Message=json.dumps(error_response),
                Subject=f"Director Error Response for Mission {mission_id}",
            )

            return {"statusCode": 500, "body": f"Error: {str(e)}"}

    except Exception as e:
        print(f"Error processing persona intention: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}


def handle_coordinator_mission_result(message: str) -> Dict[str, Any]:
    """
    Handle mission results received from Coordinator via coordinator-mission-result-topic.
    Process the results and send response back to Persona.
    """
    try:
        result_data = json.loads(message)
        print(f"Processing coordinator mission result: {result_data}")

        # Extract mission information
        mission_id = result_data.get("mission_id", "unknown")
        user_id = result_data.get("user_id", "unknown")
        status = result_data.get("status", "unknown")
        tasks = result_data.get("tasks", [])

        print(f"Mission {mission_id} completed with status: {status}")

        # Generate user-friendly response based on the mission results
        response_text = synthesize_mission_response(result_data)

        # Send response back to Persona
        response_data = {
            "mission_id": mission_id,
            "user_id": user_id,
            "status": "completed",
            "response": response_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "agent_director",
            "original_result": result_data,
        }

        # Publish response to director_response_topic for Persona
        sns.publish(
            TopicArn=DIRECTOR_RESPONSE_TOPIC_ARN,
            Message=json.dumps(response_data),
            Subject=f"Director Response for Mission {mission_id}",
        )

        print(f"Sent final response to Persona for mission {mission_id}")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "mission_id": mission_id,
                    "message": "Mission result processed and response sent to Persona",
                }
            ),
        }

    except Exception as e:
        print(f"Error processing coordinator mission result: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}


def synthesize_mission_response(result_data: Dict[str, Any]) -> str:
    """
    Generate a user-friendly response from mission results
    """
    try:
        status = result_data.get("status", "unknown")
        tasks = result_data.get("tasks", [])
        user_request = result_data.get("user_request", "your request")

        if status == "completed":
            # Analyze successful tasks
            successful_tasks = [
                task for task in tasks if task.get("status") == "completed"
            ]
            failed_tasks = [task for task in tasks if task.get("status") == "failed"]

            if len(successful_tasks) == len(tasks):
                # All tasks successful
                response = f"✅ Great! I've successfully completed {user_request}. "

                # Add specific results if available
                results = []
                for task in successful_tasks:
                    task_result = task.get("result", {})
                    if isinstance(task_result, dict) and task_result.get("message"):
                        results.append(task_result["message"])

                if results:
                    response += "Results: " + "; ".join(results)
                else:
                    response += "All operations completed successfully."

            elif successful_tasks:
                # Partial success
                response = f"⚠️ I've partially completed {user_request}. "
                response += f"{len(successful_tasks)} out of {len(tasks)} operations succeeded. "

                if failed_tasks:
                    failed_actions = [
                        task.get("action", "unknown") for task in failed_tasks
                    ]
                    response += f"Failed operations: {', '.join(failed_actions)}."
            else:
                # All failed
                response = (
                    f"❌ I encountered issues while trying to complete {user_request}. "
                )
                response += (
                    "Please try again or contact support if the problem persists."
                )

        elif status == "failed":
            response = f"❌ I was unable to complete {user_request}. "
            error_msg = result_data.get("error", "Unknown error occurred")
            response += f"Error: {error_msg}"

        else:
            response = f"⏳ Your request '{user_request}' is being processed. Current status: {status}"

        return response

    except Exception as e:
        print(f"Error synthesizing response: {str(e)}")
        return f"Your request has been processed. Status: {result_data.get('status', 'unknown')}"


def handle_direct_invocation(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle direct Lambda invocation for testing
    """
    try:
        user_intention = event.get("user_intention", "")
        user_id = event.get("user_id", "test-user")
        mission_id = event.get("mission_id", str(uuid.uuid4()))

        if not user_intention:
            return {"statusCode": 400, "body": "No user intention provided"}

        created_mission_id = create_and_publish_mission(user_intention, user_id)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "mission_id": created_mission_id,
                    "message": "Mission plan created",
                }
            ),
        }

    except Exception as e:
        print(f"Error in direct invocation: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
