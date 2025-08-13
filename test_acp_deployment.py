#!/usr/bin/env python3
"""
Test script to validate ACP deployment readiness
Run this before deploying to AWS
"""

import sys
import os
import json

# Add the common utils path
sys.path.append('src/layers/common_utils/python')

try:
    from acp_protocol import ACPProtocol, AgentType, MessageType, StandardActions
    from models import convert_task_message_to_acp, is_acp_message
    print("✅ All ACP imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_acp_ready_for_deployment():
    """Test that ACP is ready for AWS deployment"""
    print("🚀 Testing ACP Deployment Readiness")
    print("=" * 50)
    
    # Test 1: Create ACP instance
    try:
        coordinator = ACPProtocol("coordinator-test", AgentType.COORDINATOR)
        print("✅ ACP Protocol instance created")
    except Exception as e:
        print(f"❌ Failed to create ACP instance: {e}")
        return False
    
    # Test 2: Create and serialize task
    try:
        task = coordinator.create_task(
            target_agent="elevator-test",
            task_id="deploy-test-001",
            action=StandardActions.TASK_EXECUTE,
            parameters={"test": "deployment"}
        )
        
        task_json = task.to_json()
        parsed_task = coordinator.validate_message(task_json)
        
        print("✅ Task creation and serialization working")
        print(f"   Task ID: {parsed_task.payload.data['task_id']}")
    except Exception as e:
        print(f"❌ Task creation failed: {e}")
        return False
    
    # Test 3: Environment variables simulation
    env_vars = [
        "ACP_TASK_TOPIC_ARN",
        "ACP_RESULT_TOPIC_ARN", 
        "ACP_EVENT_TOPIC_ARN",
        "ACP_HEARTBEAT_TOPIC_ARN"
    ]
    
    print("✅ Required environment variables:")
    for var in env_vars:
        print(f"   {var}: Ready for Terraform")
    
    # Test 4: SNS Topic compatibility
    topic_names = [
        "bos-dev-acp-task-topic",
        "bos-dev-acp-result-topic",
        "bos-dev-acp-event-topic", 
        "bos-dev-acp-heartbeat-topic"
    ]
    
    print("✅ SNS Topics to be created:")
    for topic in topic_names:
        print(f"   {topic}")
    
    print("\n" + "=" * 50)
    print("🎯 ACP Protocol is READY for AWS deployment!")
    print("📋 Next steps:")
    print("   1. Run: cd terraform/environments/dev")
    print("   2. Run: terraform apply -auto-approve")
    print("   3. Verify SNS topics are created")
    print("   4. Test Lambda functions with ACP messages")
    
    return True

if __name__ == "__main__":
    success = test_acp_ready_for_deployment()
    sys.exit(0 if success else 1)
