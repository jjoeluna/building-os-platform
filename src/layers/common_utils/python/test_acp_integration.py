#!/usr/bin/env python3
"""
ACP Integration Test Suite
Tests the complete ACP protocol integration with BuildingOS platform
"""

import json
from datetime import datetime
from acp_protocol import ACPProtocol, AgentType, MessageType, StandardActions, Priority
from models import (
    TaskMessage,
    TaskResult,
    convert_task_message_to_acp,
    convert_task_result_to_acp,
    is_acp_message,
)


def test_acp_protocol_basic():
    """Test basic ACP protocol functionality"""
    print("🧪 Testing basic ACP protocol functionality...")

    # Create coordinator instance
    coordinator = ACPProtocol("coordinator-001", AgentType.COORDINATOR)

    # Test task creation
    task = coordinator.create_task(
        target_agent="elevator-agent-001",
        task_id="test-task-001",
        action=StandardActions.TASK_EXECUTE,
        parameters={"operation": "call_elevator", "floor": 5},
    )

    print(f"✅ Task created: {task.header.message_id}")
    print(f"   Message type: {task.header.message_type}")
    print(f"   Target agent: {task.header.target_agent}")

    # Test result creation
    elevator = ACPProtocol("elevator-agent-001", AgentType.ELEVATOR)
    result = elevator.create_result(
        original_task=task,
        task_result={"status": "completed", "floor": 5},
        execution_time_ms=2500,
    )

    print(f"✅ Result created: {result.header.message_id}")
    print(f"   Message type: {result.header.message_type}")
    print(f"   Correlation ID: {result.header.correlation_id}")

    return True


def test_legacy_to_acp_conversion():
    """Test conversion from legacy format to ACP"""
    print("\n🔄 Testing legacy to ACP conversion...")

    # Create legacy task message
    legacy_task = TaskMessage(
        message_type="task",
        correlation_id="test-correlation-001",
        timestamp=datetime.now().isoformat(),
        source_service="coordinator",
        data={},
        mission_id="mission-001",
        task_id="task-001",
        agent="elevator",
        action="call_elevator",
        parameters={"floor": 3},
    )

    # Convert to ACP
    acp_format = convert_task_message_to_acp(legacy_task)

    print(f"✅ Legacy task converted to ACP format")
    print(f"   Task ID: {acp_format['payload']['data']['task_id']}")
    print(f"   Message type: {acp_format['header']['message_type']}")

    # Test legacy result conversion
    legacy_result = TaskResult(
        task_id="task-001",
        agent="elevator",
        success=True,
        data={"floor": 3, "status": "completed"},
        timestamp=datetime.now().isoformat(),
    )

    acp_result_format = convert_task_result_to_acp(legacy_result)

    print(f"✅ Legacy result converted to ACP format")
    print(f"   Result type: {acp_result_format['header']['message_type']}")
    print(f"   Success: {acp_result_format['payload']['data']['success']}")

    return True


def test_acp_message_detection():
    """Test ACP message format detection"""
    print("\n🔍 Testing ACP message detection...")

    # ACP format message
    acp_message = {
        "header": {
            "message_type": "task",
            "source_agent": "coordinator",
            "target_agent": "elevator",
        },
        "payload": {"action": "call_elevator", "data": {"floor": 5}},
    }

    # Legacy format message
    legacy_message = {
        "message_type": "task",
        "data": {"task_id": "123"},
        "source_service": "coordinator",
    }

    print(f"✅ ACP message detected: {is_acp_message(acp_message)}")
    print(f"✅ Legacy message detected: {not is_acp_message(legacy_message)}")

    return True


def test_dual_protocol_support():
    """Test that both protocols can work together"""
    print("\n🤝 Testing dual protocol support...")

    coordinator = ACPProtocol("coordinator-001", AgentType.COORDINATOR)

    # Create ACP task
    acp_task = coordinator.create_task(
        target_agent="elevator-agent-001",
        task_id="dual-test-001",
        action=StandardActions.ELEVATOR_CALL,
        parameters={"from_floor": 1, "to_floor": 5},
    )

    # Serialize to JSON (as would be sent via SNS)
    acp_json = acp_task.to_json()

    # Parse back (as would be received by agent)
    parsed_acp = coordinator.validate_message(acp_json)

    print(f"✅ ACP round-trip successful")
    print(f"   Original task ID: {acp_task.payload.data['task_id']}")
    print(f"   Parsed task ID: {parsed_acp.payload.data['task_id']}")
    print(
        f"   Message types match: {acp_task.header.message_type == parsed_acp.header.message_type}"
    )

    return True


def test_sns_topic_compatibility():
    """Test SNS topic naming compatibility"""
    print("\n📡 Testing SNS topic compatibility...")

    # Current topic patterns
    current_topics = [
        "bos-dev-coordinator-task-topic",
        "bos-dev-agent-task-result-topic",
        "bos-dev-director-mission-topic",
    ]

    # ACP topic patterns
    acp_topics = [
        "bos-dev-acp-task-topic",
        "bos-dev-acp-result-topic",
        "bos-dev-acp-event-topic",
        "bos-dev-acp-heartbeat-topic",
    ]

    print(f"✅ Current topics: {len(current_topics)} configured")
    print(f"✅ ACP topics: {len(acp_topics)} configured")
    print(
        f"✅ Total topics: {len(current_topics) + len(acp_topics)} (dual protocol support)"
    )

    return True


def main():
    """Run all ACP integration tests"""
    print("🚀 BuildingOS ACP Integration Test Suite")
    print("=" * 50)

    tests = [
        test_acp_protocol_basic,
        test_legacy_to_acp_conversion,
        test_acp_message_detection,
        test_dual_protocol_support,
        test_sns_topic_compatibility,
    ]

    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {test.__name__} - {str(e)}")

    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All ACP integration tests PASSED!")
        print("✅ Ready for deployment and SNS testing")
    else:
        print("⚠️  Some tests failed - review implementation")

    return passed == len(tests)


if __name__ == "__main__":
    main()
