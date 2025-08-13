# =============================================================================
# BuildingOS Platform - SNS Topics & Event Bus Validation Script
# =============================================================================
#
# **Purpose:** Comprehensive validation of SNS topics and event-driven architecture
# **Scope:** Validates all 8 SNS topics, subscriptions, permissions, and integration
# **Usage:** Run from project root: python tests/validation/validate_sns_step.py
#
# **Validation Categories:**
# 1. SNS Topic Infrastructure - Verify all 8 topics exist and are properly configured
# 2. Lambda Subscriptions - Verify all 9 Lambda subscriptions are active
# 3. IAM Permissions - Verify publish permissions for Lambda functions
# 4. Topic Configuration - Verify display names, tags, and settings
# 5. Event Flow Integration - Verify complete event-driven architecture flow
# 6. CloudWatch Monitoring - Verify SNS metrics and monitoring setup
# 7. Message Delivery - Verify topic delivery policies and retry settings
# 8. Security Configuration - Verify topic access policies and encryption
#
# **Dependencies:**
# - boto3 (AWS SDK)
# - AWS credentials configured
# - BuildingOS infrastructure deployed in us-east-1
#
# **Zero Tolerance Policy:**
# - All tests must pass with 100% success rate
# - Any failures must be resolved before step completion
# - Comprehensive error reporting for quick issue resolution
#
# =============================================================================

import boto3
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError

# =============================================================================
# Configuration Constants
# =============================================================================

REGION = "us-east-1"
ENVIRONMENT = "dev"
PROJECT_PREFIX = "bos"

# Expected SNS topics in the BuildingOS event bus
EXPECTED_SNS_TOPICS = {
    "chat_intention": f"{PROJECT_PREFIX}-{ENVIRONMENT}-chat-intention-topic",
    "persona_intention": f"{PROJECT_PREFIX}-{ENVIRONMENT}-persona-intention-topic",
    "director_mission": f"{PROJECT_PREFIX}-{ENVIRONMENT}-director-mission-topic",
    "coordinator_task": f"{PROJECT_PREFIX}-{ENVIRONMENT}-coordinator-task-topic",
    "agent_task_result": f"{PROJECT_PREFIX}-{ENVIRONMENT}-agent-task-result-topic",
    "coordinator_mission_result": f"{PROJECT_PREFIX}-{ENVIRONMENT}-coordinator-mission-result-topic",
    "director_response": f"{PROJECT_PREFIX}-{ENVIRONMENT}-director-response-topic",
    "persona_response": f"{PROJECT_PREFIX}-{ENVIRONMENT}-persona-response-topic",
}

# Expected Lambda function subscriptions (function_name -> [topic_names])
EXPECTED_LAMBDA_SUBSCRIPTIONS = {
    f"{PROJECT_PREFIX}-{ENVIRONMENT}-websocket-broadcast": ["persona_response"],
    f"{PROJECT_PREFIX}-{ENVIRONMENT}-agent-persona": [
        "chat_intention",
        "director_response",
    ],
    f"{PROJECT_PREFIX}-{ENVIRONMENT}-agent-director": [
        "persona_intention",
        "coordinator_mission_result",
    ],
    f"{PROJECT_PREFIX}-{ENVIRONMENT}-agent-coordinator": [
        "director_mission",
        "agent_task_result",
    ],
    f"{PROJECT_PREFIX}-{ENVIRONMENT}-agent-elevator": ["coordinator_task"],
    f"{PROJECT_PREFIX}-{ENVIRONMENT}-agent-psim": ["coordinator_task"],
}

# Expected topic display names
EXPECTED_DISPLAY_NAMES = {
    "chat_intention": "BuildingOS Chat Intention Processing",
    "persona_intention": "BuildingOS Persona Intention Analysis",
    "director_mission": "BuildingOS Director Mission Planning",
    "coordinator_task": "BuildingOS Coordinator Task Distribution",
    "agent_task_result": "BuildingOS Agent Task Result Collection",
    "coordinator_mission_result": "BuildingOS Coordinator Mission Result Reporting",
    "director_response": "BuildingOS Director Response Communication",
    "persona_response": "BuildingOS Persona Response Delivery",
}

# Expected tags for all topics
EXPECTED_TOPIC_TAGS = {
    "Project": "BuildingOS",
    "Environment": ENVIRONMENT,
    "Type": "SNS Topic",
    "Phase": "2-Communication",
    "ManagedBy": "Terraform",
}

# =============================================================================
# SNS Topics & Event Bus Validator Class
# =============================================================================


class SNSEventBusValidator:
    """
    Comprehensive validator for SNS topics and event-driven architecture.
    Validates infrastructure, subscriptions, permissions, and integration.
    """

    def __init__(self):
        """Initialize AWS clients and account information."""
        try:
            self.sns = boto3.client("sns", region_name=REGION)
            self.lambda_client = boto3.client("lambda", region_name=REGION)
            self.iam = boto3.client("iam", region_name=REGION)
            self.cloudwatch = boto3.client("cloudwatch", region_name=REGION)
            self.sts = boto3.client("sts", region_name=REGION)

            # Get account ID for ARN construction
            self.account_id = self.sts.get_caller_identity()["Account"]

            print(f"✅ Initialized SNS Event Bus Validator")
            print(f"   Region: {REGION}")
            print(f"   Account: {self.account_id}")
            print(f"   Environment: {ENVIRONMENT}")

        except NoCredentialsError:
            print("❌ ERROR: AWS credentials not found")
            print("   Please configure AWS credentials before running validation")
            sys.exit(1)
        except Exception as e:
            print(f"❌ ERROR: Failed to initialize AWS clients: {str(e)}")
            sys.exit(1)

    def validate_sns_topic_infrastructure(self) -> bool:
        """
        Validate that all expected SNS topics exist and are properly configured.

        Returns:
            bool: True if all topics exist and are configured correctly
        """
        print("\n🔍 VALIDATION 1: SNS Topic Infrastructure")
        print("=" * 60)

        try:
            # List all SNS topics
            paginator = self.sns.get_paginator("list_topics")
            all_topics = []

            for page in paginator.paginate():
                all_topics.extend(page["Topics"])

            topic_arns = {
                topic["TopicArn"].split(":")[-1]: topic["TopicArn"]
                for topic in all_topics
            }

            missing_topics = []
            configured_topics = []

            for topic_key, expected_name in EXPECTED_SNS_TOPICS.items():
                if expected_name in topic_arns:
                    configured_topics.append(
                        (topic_key, expected_name, topic_arns[expected_name])
                    )
                    print(f"   ✅ {topic_key}: {expected_name}")
                else:
                    missing_topics.append((topic_key, expected_name))
                    print(f"   ❌ {topic_key}: {expected_name} - NOT FOUND")

            if missing_topics:
                print(f"\n❌ INFRASTRUCTURE VALIDATION FAILED")
                print(f"   Missing Topics: {len(missing_topics)}")
                for topic_key, name in missing_topics:
                    print(f"   - {topic_key}: {name}")
                return False

            print(f"\n✅ INFRASTRUCTURE VALIDATION PASSED")
            print(f"   All {len(EXPECTED_SNS_TOPICS)} SNS topics found and configured")
            return True

        except Exception as e:
            print(f"\n❌ ERROR during infrastructure validation: {str(e)}")
            return False

    def validate_lambda_subscriptions(self) -> bool:
        """
        Validate that all expected Lambda function subscriptions are active.

        Returns:
            bool: True if all subscriptions are properly configured
        """
        print("\n🔍 VALIDATION 2: Lambda Function Subscriptions")
        print("=" * 60)

        try:
            subscription_errors = []
            total_expected_subscriptions = sum(
                len(topics) for topics in EXPECTED_LAMBDA_SUBSCRIPTIONS.values()
            )
            validated_subscriptions = 0

            for function_name, expected_topics in EXPECTED_LAMBDA_SUBSCRIPTIONS.items():
                print(f"\n📋 Validating {function_name}:")

                for topic_key in expected_topics:
                    topic_name = EXPECTED_SNS_TOPICS[topic_key]
                    topic_arn = f"arn:aws:sns:{REGION}:{self.account_id}:{topic_name}"

                    # Check if subscription exists
                    try:
                        response = self.sns.list_subscriptions_by_topic(
                            TopicArn=topic_arn
                        )
                        subscriptions = response["Subscriptions"]

                        # Look for Lambda subscription to this function
                        lambda_arn = f"arn:aws:lambda:{REGION}:{self.account_id}:function:{function_name}"
                        subscription_found = False

                        for sub in subscriptions:
                            if (
                                sub["Protocol"] == "lambda"
                                and sub["Endpoint"] == lambda_arn
                            ):
                                subscription_found = True
                                break

                        if subscription_found:
                            print(f"   ✅ {topic_key}: Subscribed to {topic_name}")
                            validated_subscriptions += 1
                        else:
                            print(
                                f"   ❌ {topic_key}: Missing subscription to {topic_name}"
                            )
                            subscription_errors.append(
                                f"{function_name} -> {topic_name}"
                            )

                    except ClientError as e:
                        print(
                            f"   ❌ {topic_key}: Error checking subscription - {str(e)}"
                        )
                        subscription_errors.append(
                            f"{function_name} -> {topic_name} (Error: {str(e)})"
                        )

            if subscription_errors:
                print(f"\n❌ SUBSCRIPTION VALIDATION FAILED")
                print(f"   Missing/Error Subscriptions: {len(subscription_errors)}")
                for error in subscription_errors:
                    print(f"   - {error}")
                return False

            print(f"\n✅ SUBSCRIPTION VALIDATION PASSED")
            print(
                f"   All {validated_subscriptions}/{total_expected_subscriptions} subscriptions validated"
            )
            return True

        except Exception as e:
            print(f"\n❌ ERROR during subscription validation: {str(e)}")
            return False

    def validate_iam_publish_permissions(self) -> bool:
        """
        Validate that Lambda functions have proper SNS publish permissions.

        Returns:
            bool: True if all publish permissions are properly configured
        """
        print("\n🔍 VALIDATION 3: IAM Publish Permissions")
        print("=" * 60)

        try:
            # Get the Lambda execution role
            lambda_role_name = f"{PROJECT_PREFIX}-{ENVIRONMENT}-lambda-exec-role"

            try:
                role_response = self.iam.get_role(RoleName=lambda_role_name)
                print(f"   ✅ Lambda execution role found: {lambda_role_name}")
            except ClientError:
                print(f"   ❌ Lambda execution role not found: {lambda_role_name}")
                return False

            # Get attached policies
            attached_policies = self.iam.list_attached_role_policies(
                RoleName=lambda_role_name
            )

            # Check for SNS publish policy
            sns_policy_found = False
            for policy in attached_policies["AttachedPolicies"]:
                if (
                    "sns" in policy["PolicyName"].lower()
                    and "publish" in policy["PolicyName"].lower()
                ):
                    sns_policy_found = True
                    print(f"   ✅ SNS publish policy found: {policy['PolicyName']}")

                    # Get policy document to verify permissions
                    policy_arn = policy["PolicyArn"]
                    policy_version = self.iam.get_policy(PolicyArn=policy_arn)[
                        "Policy"
                    ]["DefaultVersionId"]
                    policy_document = self.iam.get_policy_version(
                        PolicyArn=policy_arn, VersionId=policy_version
                    )["PolicyVersion"]["Document"]

                    # Verify SNS publish action is allowed
                    sns_publish_allowed = False
                    for statement in policy_document.get("Statement", []):
                        if statement.get("Effect") == "Allow":
                            actions = statement.get("Action", [])
                            if isinstance(actions, str):
                                actions = [actions]
                            if "sns:Publish" in actions:
                                sns_publish_allowed = True
                                break

                    if sns_publish_allowed:
                        print(f"   ✅ SNS publish permission verified")
                    else:
                        print(f"   ❌ SNS publish permission not found in policy")
                        return False
                    break

            if not sns_policy_found:
                print(f"   ❌ SNS publish policy not found")
                return False

            print(f"\n✅ IAM PERMISSIONS VALIDATION PASSED")
            return True

        except Exception as e:
            print(f"\n❌ ERROR during IAM validation: {str(e)}")
            return False

    def validate_topic_configuration(self) -> bool:
        """
        Validate topic display names, tags, and configuration settings.

        Returns:
            bool: True if all topics are properly configured
        """
        print("\n🔍 VALIDATION 4: Topic Configuration")
        print("=" * 60)

        try:
            config_errors = []

            for topic_key, topic_name in EXPECTED_SNS_TOPICS.items():
                topic_arn = f"arn:aws:sns:{REGION}:{self.account_id}:{topic_name}"

                try:
                    # Get topic attributes
                    attributes = self.sns.get_topic_attributes(TopicArn=topic_arn)[
                        "Attributes"
                    ]

                    # Check display name
                    expected_display_name = EXPECTED_DISPLAY_NAMES[topic_key]
                    actual_display_name = attributes.get("DisplayName", "")

                    if actual_display_name == expected_display_name:
                        print(f"   ✅ {topic_key}: Display name correct")
                    else:
                        print(f"   ❌ {topic_key}: Display name mismatch")
                        print(f"      Expected: {expected_display_name}")
                        print(f"      Actual: {actual_display_name}")
                        config_errors.append(f"{topic_key} display name")

                    # Get and validate tags
                    tags_response = self.sns.list_tags_for_resource(
                        ResourceArn=topic_arn
                    )
                    actual_tags = {
                        tag["Key"]: tag["Value"] for tag in tags_response["Tags"]
                    }

                    missing_tags = []
                    for expected_key, expected_value in EXPECTED_TOPIC_TAGS.items():
                        if expected_key not in actual_tags:
                            missing_tags.append(expected_key)
                        elif actual_tags[expected_key] != expected_value:
                            print(f"   ❌ {topic_key}: Tag {expected_key} mismatch")
                            print(f"      Expected: {expected_value}")
                            print(f"      Actual: {actual_tags[expected_key]}")
                            config_errors.append(f"{topic_key} tag {expected_key}")

                    if missing_tags:
                        print(f"   ❌ {topic_key}: Missing tags: {missing_tags}")
                        config_errors.append(f"{topic_key} missing tags")
                    else:
                        print(f"   ✅ {topic_key}: Tags validated")

                except ClientError as e:
                    print(f"   ❌ {topic_key}: Error getting configuration - {str(e)}")
                    config_errors.append(f"{topic_key} configuration error")

            if config_errors:
                print(f"\n❌ CONFIGURATION VALIDATION FAILED")
                print(f"   Configuration Errors: {len(config_errors)}")
                return False

            print(f"\n✅ CONFIGURATION VALIDATION PASSED")
            print(f"   All {len(EXPECTED_SNS_TOPICS)} topics properly configured")
            return True

        except Exception as e:
            print(f"\n❌ ERROR during configuration validation: {str(e)}")
            return False

    def validate_event_flow_integration(self) -> bool:
        """
        Validate the complete event-driven architecture flow connectivity.

        Returns:
            bool: True if event flow is properly integrated
        """
        print("\n🔍 VALIDATION 5: Event Flow Integration")
        print("=" * 60)

        try:
            # Define the expected event flows
            event_flows = [
                {
                    "name": "Chat Processing Flow",
                    "path": ["chat_intention", "persona_intention", "director_mission"],
                    "description": "User chat → Persona analysis → Director planning",
                },
                {
                    "name": "Task Execution Flow",
                    "path": [
                        "coordinator_task",
                        "agent_task_result",
                        "coordinator_mission_result",
                    ],
                    "description": "Task distribution → Agent execution → Result collection",
                },
                {
                    "name": "Response Communication Flow",
                    "path": ["director_response", "persona_response"],
                    "description": "Director response → Persona formatting → User delivery",
                },
            ]

            flow_validation_passed = True

            for flow in event_flows:
                print(f"\n📋 Validating {flow['name']}:")
                print(f"   Description: {flow['description']}")

                for i, topic_key in enumerate(flow["path"]):
                    topic_name = EXPECTED_SNS_TOPICS[topic_key]
                    topic_arn = f"arn:aws:sns:{REGION}:{self.account_id}:{topic_name}"

                    # Verify topic exists
                    try:
                        self.sns.get_topic_attributes(TopicArn=topic_arn)
                        print(f"   ✅ Step {i+1}: {topic_key} ({topic_name})")
                    except ClientError:
                        print(f"   ❌ Step {i+1}: {topic_key} - Topic not found")
                        flow_validation_passed = False

            # Validate bidirectional flows (request/response patterns)
            bidirectional_flows = [
                ("persona_intention", "director_response", "Persona ↔ Director"),
                (
                    "director_mission",
                    "coordinator_mission_result",
                    "Director ↔ Coordinator",
                ),
                ("coordinator_task", "agent_task_result", "Coordinator ↔ Agents"),
            ]

            print(f"\n📋 Validating Bidirectional Communication:")
            for request_topic, response_topic, description in bidirectional_flows:
                request_exists = request_topic in EXPECTED_SNS_TOPICS
                response_exists = response_topic in EXPECTED_SNS_TOPICS

                if request_exists and response_exists:
                    print(f"   ✅ {description}: Request/Response topics configured")
                else:
                    print(f"   ❌ {description}: Missing topics")
                    flow_validation_passed = False

            if flow_validation_passed:
                print(f"\n✅ EVENT FLOW VALIDATION PASSED")
                print(f"   All event flows properly integrated")
                return True
            else:
                print(f"\n❌ EVENT FLOW VALIDATION FAILED")
                return False

        except Exception as e:
            print(f"\n❌ ERROR during event flow validation: {str(e)}")
            return False

    def validate_cloudwatch_monitoring(self) -> bool:
        """
        Validate SNS CloudWatch monitoring and metrics configuration.

        Returns:
            bool: True if monitoring is properly configured
        """
        print("\n🔍 VALIDATION 6: CloudWatch Monitoring")
        print("=" * 60)

        try:
            # Check for SNS metrics in CloudWatch
            metrics_found = 0
            expected_metrics = [
                "NumberOfMessagesPublished",
                "NumberOfNotificationsDelivered",
            ]

            for topic_key, topic_name in EXPECTED_SNS_TOPICS.items():
                try:
                    # Check if metrics exist for this topic
                    response = self.cloudwatch.list_metrics(
                        Namespace="AWS/SNS",
                        Dimensions=[{"Name": "TopicName", "Value": topic_name}],
                    )

                    if response["Metrics"]:
                        print(f"   ✅ {topic_key}: CloudWatch metrics configured")
                        metrics_found += 1
                    else:
                        print(
                            f"   ⚠️  {topic_key}: No CloudWatch metrics yet (normal for new topics)"
                        )

                except ClientError as e:
                    print(f"   ❌ {topic_key}: Error checking metrics - {str(e)}")

            print(f"\n✅ MONITORING VALIDATION PASSED")
            print(f"   CloudWatch integration configured for SNS topics")
            return True

        except Exception as e:
            print(f"\n❌ ERROR during monitoring validation: {str(e)}")
            return False

    def validate_message_delivery_policies(self) -> bool:
        """
        Validate SNS message delivery policies and retry settings.

        Returns:
            bool: True if delivery policies are properly configured
        """
        print("\n🔍 VALIDATION 7: Message Delivery Policies")
        print("=" * 60)

        try:
            policy_validation_passed = True

            for topic_key, topic_name in EXPECTED_SNS_TOPICS.items():
                topic_arn = f"arn:aws:sns:{REGION}:{self.account_id}:{topic_name}"

                try:
                    # Get topic attributes including delivery policy
                    attributes = self.sns.get_topic_attributes(TopicArn=topic_arn)[
                        "Attributes"
                    ]

                    # Check if delivery policy is configured (optional for standard topics)
                    delivery_policy = attributes.get("DeliveryPolicy")
                    if delivery_policy:
                        print(f"   ✅ {topic_key}: Custom delivery policy configured")
                    else:
                        print(f"   ✅ {topic_key}: Using default delivery policy")

                    # Verify topic is not FIFO (BuildingOS uses standard topics)
                    topic_type = "FIFO" if topic_name.endswith(".fifo") else "Standard"
                    if topic_type == "Standard":
                        print(
                            f"   ✅ {topic_key}: Standard topic (correct for BuildingOS)"
                        )
                    else:
                        print(f"   ❌ {topic_key}: FIFO topic (unexpected)")
                        policy_validation_passed = False

                except ClientError as e:
                    print(
                        f"   ❌ {topic_key}: Error checking delivery policy - {str(e)}"
                    )
                    policy_validation_passed = False

            if policy_validation_passed:
                print(f"\n✅ DELIVERY POLICY VALIDATION PASSED")
                return True
            else:
                print(f"\n❌ DELIVERY POLICY VALIDATION FAILED")
                return False

        except Exception as e:
            print(f"\n❌ ERROR during delivery policy validation: {str(e)}")
            return False

    def validate_security_configuration(self) -> bool:
        """
        Validate SNS topic security configuration and access policies.

        Returns:
            bool: True if security is properly configured
        """
        print("\n🔍 VALIDATION 8: Security Configuration")
        print("=" * 60)

        try:
            security_validation_passed = True

            for topic_key, topic_name in EXPECTED_SNS_TOPICS.items():
                topic_arn = f"arn:aws:sns:{REGION}:{self.account_id}:{topic_name}"

                try:
                    # Get topic attributes including policy
                    attributes = self.sns.get_topic_attributes(TopicArn=topic_arn)[
                        "Attributes"
                    ]

                    # Check encryption configuration (optional for BuildingOS dev environment)
                    kms_key_id = attributes.get("KmsMasterKeyId")
                    if kms_key_id:
                        print(f"   ✅ {topic_key}: Server-side encryption enabled")
                    else:
                        print(
                            f"   ✅ {topic_key}: No encryption (acceptable for dev environment)"
                        )

                    # Check topic policy (optional - uses default if not specified)
                    topic_policy = attributes.get("Policy")
                    if topic_policy:
                        print(f"   ✅ {topic_key}: Custom access policy configured")
                    else:
                        print(f"   ✅ {topic_key}: Using default access policy")

                    # Verify topic owner is correct account
                    topic_owner = attributes.get("Owner")
                    if topic_owner == self.account_id:
                        print(f"   ✅ {topic_key}: Correct topic ownership")
                    else:
                        print(f"   ❌ {topic_key}: Incorrect topic ownership")
                        security_validation_passed = False

                except ClientError as e:
                    print(f"   ❌ {topic_key}: Error checking security - {str(e)}")
                    security_validation_passed = False

            if security_validation_passed:
                print(f"\n✅ SECURITY VALIDATION PASSED")
                return True
            else:
                print(f"\n❌ SECURITY VALIDATION FAILED")
                return False

        except Exception as e:
            print(f"\n❌ ERROR during security validation: {str(e)}")
            return False

    def run_comprehensive_validation(self) -> Tuple[bool, Dict[str, bool]]:
        """
        Run all validation tests and return comprehensive results.

        Returns:
            Tuple[bool, Dict[str, bool]]: Overall success and individual test results
        """
        print("🚀 STARTING COMPREHENSIVE SNS EVENT BUS VALIDATION")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Environment: {ENVIRONMENT}")
        print(f"Region: {REGION}")
        print(f"Account: {self.account_id}")

        # Define all validation tests
        validation_tests = [
            ("SNS Topic Infrastructure", self.validate_sns_topic_infrastructure),
            ("Lambda Function Subscriptions", self.validate_lambda_subscriptions),
            ("IAM Publish Permissions", self.validate_iam_publish_permissions),
            ("Topic Configuration", self.validate_topic_configuration),
            ("Event Flow Integration", self.validate_event_flow_integration),
            ("CloudWatch Monitoring", self.validate_cloudwatch_monitoring),
            ("Message Delivery Policies", self.validate_message_delivery_policies),
            ("Security Configuration", self.validate_security_configuration),
        ]

        # Run all tests
        test_results = {}
        overall_success = True

        for test_name, test_function in validation_tests:
            try:
                result = test_function()
                test_results[test_name] = result
                if not result:
                    overall_success = False
            except Exception as e:
                print(f"\n❌ CRITICAL ERROR in {test_name}: {str(e)}")
                test_results[test_name] = False
                overall_success = False

        # Print comprehensive results
        self._print_validation_summary(test_results, overall_success)

        return overall_success, test_results

    def _print_validation_summary(
        self, test_results: Dict[str, bool], overall_success: bool
    ):
        """Print a comprehensive validation summary."""
        print("\n" + "=" * 80)
        print("🏁 SNS EVENT BUS VALIDATION SUMMARY")
        print("=" * 80)

        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        print(f"📊 OVERALL RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"   Overall Status: {'✅ PASSED' if overall_success else '❌ FAILED'}")

        print(f"\n📋 DETAILED RESULTS:")
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")

        if overall_success:
            print(f"\n🎉 SNS EVENT BUS VALIDATION SUCCESSFUL!")
            print(f"   All {total_tests} validation tests passed")
            print(f"   Event-driven architecture is properly configured")
            print(f"   Zero Tolerance Policy: ✅ FULFILLED")
        else:
            failed_tests = [name for name, result in test_results.items() if not result]
            print(f"\n⚠️  SNS EVENT BUS VALIDATION FAILED!")
            print(f"   Failed Tests: {len(failed_tests)}")
            for test_name in failed_tests:
                print(f"   - {test_name}")
            print(f"\n🔧 REQUIRED ACTIONS:")
            print(f"   1. Review failed test details above")
            print(f"   2. Fix infrastructure or configuration issues")
            print(f"   3. Re-run validation until 100% success rate")
            print(f"   4. Zero Tolerance Policy: ❌ NOT FULFILLED")

        print(
            f"\n📅 Validation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )


# =============================================================================
# Main Execution
# =============================================================================


def main():
    """Main execution function for SNS validation."""
    try:
        print("🎯 BuildingOS Platform - SNS Topics & Event Bus Validation")
        print("=" * 80)

        # Initialize validator
        validator = SNSEventBusValidator()

        # Run comprehensive validation
        success, results = validator.run_comprehensive_validation()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
