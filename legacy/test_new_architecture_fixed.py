#!/usr/bin/env python3
"""
Test script for the new SNS architecture after legacy code removal.
Validates that all agents can operate with the new standardized topic naming.
"""

import json
import boto3
import os
import sys
from datetime import datetime


def check_sns_topics():
    """Check if all new architecture SNS topics exist"""
    sns = boto3.client("sns")

    required_topics = [
        "bos-persona-intention-topic-dev",
        "bos-director-mission-topic-dev",
        "bos-director-response-topic-dev",
        "bos-coordinator-task-topic-dev",
        "bos-agent-task-result-topic-dev",
        "bos-coordinator-mission-result-topic-dev",
    ]

    print("🔍 Checking SNS Topics...")

    try:
        response = sns.list_topics()
        existing_topics = [
            topic["TopicArn"].split(":")[-1] for topic in response["Topics"]
        ]

        results = {}
        for topic in required_topics:
            if topic in existing_topics:
                results[topic] = "✅ EXISTS"
                print(f"  ✅ {topic}")
            else:
                results[topic] = "❌ MISSING"
                print(f"  ❌ {topic}")

        return results

    except Exception as e:
        print(f"❌ Error checking topics: {e}")
        return {}


def test_lambda_environment_variables():
    """Test that Lambda functions have the correct environment variables"""
    lambda_client = boto3.client("lambda")

    # Expected new architecture variables for each function
    expected_vars = {
        "bos-agent-persona-dev": [
            "PERSONA_INTENTION_TOPIC_ARN",
            "DIRECTOR_RESPONSE_TOPIC_ARN",
            "PERSONA_RESPONSE_TOPIC_ARN",
        ],
        "bos-agent-director-dev": [
            "DIRECTOR_MISSION_TOPIC_ARN",
            "DIRECTOR_RESPONSE_TOPIC_ARN",
            "COORDINATOR_MISSION_RESULT_TOPIC_ARN",
        ],
        "bos-agent-coordinator-dev": [
            "COORDINATOR_TASK_TOPIC_ARN",
            "AGENT_TASK_RESULT_TOPIC_ARN",
            "COORDINATOR_MISSION_RESULT_TOPIC_ARN",
        ],
        "bos-agent-elevator-dev": [
            "COORDINATOR_TASK_TOPIC_ARN",
            "AGENT_TASK_RESULT_TOPIC_ARN",
        ],
        "bos-agent-psim-dev": [
            "COORDINATOR_TASK_TOPIC_ARN",
            "AGENT_TASK_RESULT_TOPIC_ARN",
        ],
    }

    # Legacy variables that should not exist
    legacy_vars_list = [
        "INTENTION_RESULT_TOPIC_ARN",
        "MISSION_TOPIC_ARN",
        "SNS_TOPIC_ARN",
        "TASK_RESULT_TOPIC_ARN",
        "MISSION_RESULT_TOPIC_ARN",
    ]

    print("\n🔍 Checking Lambda Environment Variables...")

    results = {}

    for function_name in expected_vars.keys():
        try:
            response = lambda_client.get_function_configuration(
                FunctionName=function_name
            )
            env_vars = response.get("Environment", {}).get("Variables", {})

            print(f"\n📋 {function_name}:")

            # Check expected new architecture variables
            found_new_vars = []
            missing_new_vars = []

            for expected_var in expected_vars[function_name]:
                if expected_var in env_vars:
                    topic_name = (
                        env_vars[expected_var].split(":")[-1]
                        if ":" in env_vars[expected_var]
                        else env_vars[expected_var]
                    )
                    print(f"  ✅ {expected_var}: {topic_name}")
                    found_new_vars.append(expected_var)
                else:
                    print(f"  ❌ MISSING: {expected_var}")
                    missing_new_vars.append(expected_var)

            # Check for legacy variables that shouldn't exist
            found_legacy_vars = []
            for legacy_var in legacy_vars_list:
                if legacy_var in env_vars:
                    print(f"  ⚠️  LEGACY: {legacy_var}")
                    found_legacy_vars.append(legacy_var)

            # Determine status
            has_all_new = len(missing_new_vars) == 0
            has_no_legacy = len(found_legacy_vars) == 0
            status = "OK" if has_all_new and has_no_legacy else "NEEDS_UPDATE"

            results[function_name] = {
                "expected_vars": expected_vars[function_name],
                "found_new_vars": found_new_vars,
                "missing_new_vars": missing_new_vars,
                "found_legacy_vars": found_legacy_vars,
                "status": status,
            }

        except Exception as e:
            print(f"  ❌ Error checking {function_name}: {e}")
            results[function_name] = {"status": "ERROR", "error": str(e)}

    return results


def test_simple_message_flow():
    """Test a simple message flow through the new architecture"""
    sns = boto3.client("sns")

    print("\n🔍 Testing Message Flow...")

    # Test publishing to persona intention topic
    try:
        # Get the topic ARN for persona intention
        topics = sns.list_topics()["Topics"]
        persona_topic = None

        for topic in topics:
            if "bos-persona-intention-topic" in topic["TopicArn"]:
                persona_topic = topic["TopicArn"]
                break

        if not persona_topic:
            print("❌ Could not find bos-persona-intention-topic")
            return False

        # Send test message
        test_message = {
            "mission_id": f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "user_intention": "Test message for new architecture validation",
            "timestamp": datetime.now().isoformat(),
            "test_mode": True,
        }

        response = sns.publish(
            TopicArn=persona_topic,
            Message=json.dumps(test_message),
            Subject="Architecture Test Message",
        )

        print(
            f"✅ Successfully published test message to {persona_topic.split(':')[-1]}"
        )
        print(f"   Message ID: {response['MessageId']}")
        return True

    except Exception as e:
        print(f"❌ Error testing message flow: {e}")
        return False


def generate_test_report():
    """Generate a comprehensive test report"""
    print("=" * 60)
    print("🧪 NEW ARCHITECTURE VALIDATION REPORT")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Environment: Development")

    # Test SNS topics
    topic_results = check_sns_topics()

    # Test Lambda environment variables
    lambda_results = test_lambda_environment_variables()

    # Test message flow
    message_flow_result = test_simple_message_flow()

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    topics_ok = all("EXISTS" in status for status in topic_results.values())
    lambdas_ok = all(
        result.get("status") == "OK"
        for result in lambda_results.values()
        if "status" in result
    )

    print(f"SNS Topics: {'✅ PASS' if topics_ok else '❌ FAIL'}")
    print(f"Lambda Functions: {'✅ PASS' if lambdas_ok else '❌ FAIL'}")
    print(f"Message Flow: {'✅ PASS' if message_flow_result else '❌ FAIL'}")

    overall_status = (
        "✅ READY FOR PRODUCTION"
        if (topics_ok and lambdas_ok and message_flow_result)
        else "⚠️  NEEDS ATTENTION"
    )
    print(f"\nOverall Status: {overall_status}")

    if not topics_ok or not lambdas_ok or not message_flow_result:
        print("\n📋 RECOMMENDED ACTIONS:")
        if not topics_ok:
            print("  - Run 'terraform apply' to create missing SNS topics")
        if not lambdas_ok:
            print("  - Update Lambda environment variables via Terraform")
        if not message_flow_result:
            print("  - Check SNS permissions and topic configurations")


if __name__ == "__main__":
    try:
        generate_test_report()
    except Exception as e:
        print(f"❌ Test script failed: {e}")
        sys.exit(1)
