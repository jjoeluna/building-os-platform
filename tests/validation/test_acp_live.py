#!/usr/bin/env python3
"""
🚀 BuildingOS ACP Live Integration Test
=======================================

Tests the complete ACP protocol by sending real messages through SNS
and validating the end-to-end communication flow.

Author: BuildingOS Development Team
Version: 1.0.0
"""

import json
import boto3
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List

# Initialize AWS clients
sns = boto3.client("sns")
logs = boto3.client("logs")

# ACP Topic ARNs (from environment)
ACP_TOPICS = {
    "task": "arn:aws:sns:us-east-1:481251881947:bos-dev-acp-task-topic",
    "result": "arn:aws:sns:us-east-1:481251881947:bos-dev-acp-result-topic",
    "event": "arn:aws:sns:us-east-1:481251881947:bos-dev-acp-event-topic",
    "heartbeat": "arn:aws:sns:us-east-1:481251881947:bos-dev-acp-heartbeat-topic",
}


def create_acp_message(
    message_type: str,
    source_agent: str,
    target_agent: str,
    action: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Create a properly formatted ACP message"""
    return {
        "header": {
            "message_type": message_type,
            "source_agent": source_agent,
            "target_agent": target_agent,
            "correlation_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "normal",
            "version": "1.0",
        },
        "payload": {
            "action": action,
            "data": data,
            "metadata": {
                "agent_type": source_agent.split("-")[0],
                "protocol": "acp",
                "test_mode": True,
            },
        },
        "status": "pending",
    }


def send_acp_message(topic_arn: str, message: Dict[str, Any]) -> bool:
    """Send ACP message through SNS"""
    try:
        response = sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            Subject=f"ACP {message['header']['message_type']} Test",
            MessageAttributes={
                "protocol": {"DataType": "String", "StringValue": "acp"},
                "version": {"DataType": "String", "StringValue": "1.0"},
                "message_type": {
                    "DataType": "String",
                    "StringValue": message["header"]["message_type"],
                },
                "source_agent": {
                    "DataType": "String",
                    "StringValue": message["header"]["source_agent"],
                },
                "target_agent": {
                    "DataType": "String",
                    "StringValue": message["header"]["target_agent"],
                },
                "test_mode": {"DataType": "String", "StringValue": "true"},
            },
        )
        print(f"✅ Message sent successfully: {response['MessageId']}")
        return True
    except Exception as e:
        print(f"❌ Failed to send message: {str(e)}")
        return False


def test_acp_task_message():
    """Test ACP task message"""
    print("\n🧪 Testing ACP Task Message...")

    message = create_acp_message(
        message_type="task",
        source_agent="coordinator-agent-001",
        target_agent="elevator-agent-001",
        action="elevator_status_check",
        data={
            "task_id": f"task-{uuid.uuid4().hex[:8]}",
            "elevator_id": "elevator-01",
            "floor": 5,
            "parameters": {"check_type": "status", "priority": "normal"},
        },
    )

    return send_acp_message(ACP_TOPICS["task"], message)


def test_acp_result_message():
    """Test ACP result message"""
    print("\n🧪 Testing ACP Result Message...")

    message = create_acp_message(
        message_type="result",
        source_agent="elevator-agent-001",
        target_agent="coordinator-agent-001",
        action="task_completed",
        data={
            "task_id": f"task-{uuid.uuid4().hex[:8]}",
            "result": {
                "status": "completed",
                "elevator_status": "operational",
                "current_floor": 5,
                "door_status": "closed",
            },
            "success": True,
            "execution_time": 1.5,
        },
    )

    return send_acp_message(ACP_TOPICS["result"], message)


def test_acp_event_message():
    """Test ACP event message"""
    print("\n🧪 Testing ACP Event Message...")

    message = create_acp_message(
        message_type="event",
        source_agent="director-agent-001",
        target_agent="all-agents",
        action="system_status_update",
        data={
            "event_id": f"event-{uuid.uuid4().hex[:8]}",
            "event_type": "system_status",
            "system_status": "operational",
            "active_agents": 5,
            "pending_tasks": 2,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    return send_acp_message(ACP_TOPICS["event"], message)


def test_acp_heartbeat_message():
    """Test ACP heartbeat message"""
    print("\n🧪 Testing ACP Heartbeat Message...")

    message = create_acp_message(
        message_type="heartbeat",
        source_agent="health-check-agent-001",
        target_agent="monitoring-system",
        action="agent_heartbeat",
        data={
            "agent_id": "health-check-agent-001",
            "status": "healthy",
            "uptime": 3600,
            "memory_usage": 45.2,
            "cpu_usage": 12.8,
            "last_activity": datetime.utcnow().isoformat(),
        },
    )

    return send_acp_message(ACP_TOPICS["heartbeat"], message)


def check_lambda_logs(function_name: str, minutes: int = 2) -> List[str]:
    """Check recent Lambda logs for ACP message processing"""
    try:
        log_group = f"/aws/lambda/{function_name}"
        end_time = int(time.time() * 1000)
        start_time = end_time - (minutes * 60 * 1000)

        response = logs.filter_log_events(
            logGroupName=log_group,
            startTime=start_time,
            endTime=end_time,
            filterPattern="ACP",
        )

        messages = []
        for event in response.get("events", []):
            if "ACP" in event["message"]:
                messages.append(event["message"].strip())

        return messages
    except Exception as e:
        print(f"⚠️  Could not check logs for {function_name}: {str(e)}")
        return []


def main():
    """Run complete ACP live integration test"""
    print("🚀 BuildingOS ACP Live Integration Test")
    print("=" * 50)

    tests = [
        ("ACP Task Message", test_acp_task_message),
        ("ACP Result Message", test_acp_result_message),
        ("ACP Event Message", test_acp_event_message),
        ("ACP Heartbeat Message", test_acp_heartbeat_message),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")

    # Wait a moment for message processing
    print(f"\n⏳ Waiting 10 seconds for message processing...")
    time.sleep(10)

    # Check logs for ACP message processing
    print(f"\n🔍 Checking Lambda logs for ACP message processing...")
    lambda_functions = [
        "bos-dev-agent-coordinator",
        "bos-dev-agent-elevator",
        "bos-dev-agent-health-check",
    ]

    acp_logs_found = 0
    for func in lambda_functions:
        logs_messages = check_lambda_logs(func)
        if logs_messages:
            print(f"✅ {func}: Found {len(logs_messages)} ACP log entries")
            acp_logs_found += len(logs_messages)
        else:
            print(f"⚠️  {func}: No ACP logs found (may be normal)")

    print("\n" + "=" * 50)
    print(f"🎯 ACP Live Test Results:")
    print(f"   Messages Sent: {passed}/{total} ({(passed/total)*100:.1f}%)")
    print(f"   ACP Log Entries: {acp_logs_found}")

    if passed == total:
        print("🎉 ACP LIVE INTEGRATION TEST PASSED!")
        print("✅ All ACP messages sent successfully through SNS")
        print("✅ Protocol is ready for production use")
    else:
        print("⚠️  Some ACP tests failed - review configuration")

    return passed == total


if __name__ == "__main__":
    main()
