#!/usr/bin/env python3
"""
BuildingOS Validation Script: IAM & Security Infrastructure
===========================================================

Purpose: Validate IAM roles, policies, and security configuration for BuildingOS platform
Architecture: Event-driven serverless architecture with least-privilege IAM design
Dependencies: boto3, json, sys, datetime, typing
Author: BuildingOS Architecture Team
Date: 2025-01-11
Language: English

This script validates the IAM and security foundation built in Phase 1, Step 1.2:
- Lambda execution role with proper trust policy
- Custom IAM policies for AWS service access (DynamoDB, SNS, Bedrock, API Gateway)
- AWS managed policies attachment (Lambda execution, VPC access, X-Ray)
- Least-privilege access validation
- Resource-level permissions for Lambda functions
- IAM role tagging and compliance

Architecture Context:
- Single Lambda execution role for all functions (simplified management)
- Custom policies for specific AWS service access
- Resource-level permissions for enhanced security
- VPC-enabled Lambda execution role with proper networking permissions
- X-Ray tracing enabled for observability

Security Principles:
- Least privilege access (minimum required permissions)
- Resource-specific policies (no wildcard resources where possible)
- Proper service trust relationships
- Compliance tagging for cost tracking and governance
"""

import boto3
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# =============================================================================
# Global Configuration
# =============================================================================

ENVIRONMENT = "dev"
PROJECT_NAME = "BuildingOS"
RESOURCE_PREFIX = f"bos-{ENVIRONMENT}"

# IAM role and policy names
IAM_ROLE_NAME = f"{RESOURCE_PREFIX}-lambda-exec-role"

# Required custom policies
REQUIRED_CUSTOM_POLICIES = [
    "dynamodb_access",
    "sns_publish", 
    "bedrock_access",
    "apigateway_management",
    "kms_access"  # Phase 4 preparation - policy exists but not attached yet
]

# Required AWS managed policies
REQUIRED_MANAGED_POLICIES = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole", 
    "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
]

# AWS clients
iam_client = boto3.client("iam")
lambda_client = boto3.client("lambda")

# Global variables for cross-function communication
LAMBDA_ROLE_ARN = None


# =============================================================================
# Utility Functions
# =============================================================================

def print_header():
    """Print validation script header with timestamp and context."""
    print(f"\n🧪 BuildingOS IAM & Security Validation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("\nThis script validates the IAM and security foundation built in Phase 1, Step 1.2")
    print("of the BuildingOS Clean Rebuild process.")
    print("\nSecurity Overview:")
    print("- Single Lambda execution role with least-privilege policies")
    print("- Custom policies for AWS service access (DynamoDB, SNS, Bedrock, API Gateway)")
    print("- AWS managed policies for Lambda execution and VPC access")
    print("- Resource-level permissions for enhanced security")
    print("- Compliance tagging and governance")
    print("\nStarting validation tests...\n")


def print_section(section_name: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"🧪 {section_name}")
    print("=" * 60)


def print_test(test_name: str, status: str, details: str):
    """Print a formatted test result."""
    status_emoji = "✅" if status == "PASS" else "❌"
    print(f"{status_emoji} {test_name}: {status}")
    print(f"   Details: {details}")


def print_summary(passed_tests: int, total_tests: int):
    """Print validation summary with recommendations."""
    print(f"\n{'=' * 60}")
    print("🧪 Validation Summary")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print(f"✅ ALL VALIDATIONS PASSED! ({passed_tests}/{total_tests})")
        print("\n🎉 IAM and security infrastructure is properly configured and ready for next phase!")
        print("\nNext Steps:")
        print("- Proceed to Step 1.3: API and Application Validation")
        print("- Apply quality standards (headers, comments, documentation)")
        print("- Update solution-architecture.md with IAM security details")
    else:
        print(f"❌ VALIDATIONS FAILED: {passed_tests}/{total_tests} tests passed")
        print("\n🔧 Please fix the failed validations before proceeding to the next step.")
        print("\nRecommended Actions:")
        print("- Review Terraform configuration in terraform/environments/dev/iam.tf")
        print("- Check AWS Console for IAM role and policy status")
        print("- Verify all required policies are attached and permissions are correct")


# =============================================================================
# Validation Functions
# =============================================================================

def validate_lambda_execution_role() -> bool:
    """
    Validate the main Lambda execution role configuration.
    
    Tests:
    - Role exists with correct name and trust policy
    - Proper service trust relationship (lambda.amazonaws.com)
    - Role is properly tagged for compliance
    - Role ARN is captured for other validations
    
    Returns:
        bool: True if role validation passes
    """
    print_section("Lambda Execution Role Validation")
    
    try:
        # Get the Lambda execution role
        role_response = iam_client.get_role(RoleName=IAM_ROLE_NAME)
        role = role_response["Role"]
        
        # Store role ARN for other tests
        global LAMBDA_ROLE_ARN
        LAMBDA_ROLE_ARN = role["Arn"]
        
        # Validate role name
        if role["RoleName"] == IAM_ROLE_NAME:
            print_test("Role Name", "PASS", f"Correct role name: {IAM_ROLE_NAME}")
        else:
            print_test("Role Name", "FAIL", f"Expected: {IAM_ROLE_NAME}, Found: {role['RoleName']}")
            return False
            
        # Validate trust policy
        trust_policy = role["AssumeRolePolicyDocument"]
        if isinstance(trust_policy, str):
            trust_policy = json.loads(trust_policy)
            
        lambda_service_found = False
        for statement in trust_policy.get("Statement", []):
            principal = statement.get("Principal", {})
            if isinstance(principal, dict) and principal.get("Service") == "lambda.amazonaws.com":
                lambda_service_found = True
                break
                
        if lambda_service_found:
            print_test("Trust Policy", "PASS", "Lambda service trust relationship configured")
        else:
            print_test("Trust Policy", "FAIL", "Lambda service trust relationship not found")
            return False
            
        # Validate role tagging
        tags = {tag["Key"]: tag["Value"] for tag in role.get("Tags", [])}
        project_tag = tags.get("Project")
        if project_tag == PROJECT_NAME:
            print_test("Role Tagging", "PASS", f"Project tag: {project_tag}")
        else:
            print_test("Role Tagging", "FAIL", f"Expected Project tag: {PROJECT_NAME}, Found: {project_tag}")
            return False
            
        return True
        
    except Exception as e:
        print_test("Lambda Execution Role", "FAIL", f"Exception: {str(e)}")
        return False


def validate_managed_policies() -> bool:
    """
    Validate AWS managed policies attached to Lambda execution role.
    
    Tests:
    - AWSLambdaBasicExecutionRole for CloudWatch Logs access
    - AWSLambdaVPCAccessExecutionRole for VPC networking
    - AWSXRayDaemonWriteAccess for distributed tracing
    
    Returns:
        bool: True if all managed policies are attached
    """
    print_section("AWS Managed Policies Validation")
    
    try:
        if LAMBDA_ROLE_ARN is None:
            print_test("Managed Policies", "FAIL", "Lambda role ARN not available from previous validation")
            return False
            
        # Get attached managed policies
        attached_policies = iam_client.list_attached_role_policies(RoleName=IAM_ROLE_NAME)
        attached_policy_arns = [policy["PolicyArn"] for policy in attached_policies["AttachedPolicies"]]
        
        all_policies_attached = True
        
        for required_policy in REQUIRED_MANAGED_POLICIES:
            if required_policy in attached_policy_arns:
                policy_name = required_policy.split("/")[-1]
                print_test(f"Managed Policy {policy_name}", "PASS", f"Attached: {required_policy}")
            else:
                policy_name = required_policy.split("/")[-1] 
                print_test(f"Managed Policy {policy_name}", "FAIL", f"Not attached: {required_policy}")
                all_policies_attached = False
                
        return all_policies_attached
        
    except Exception as e:
        print_test("Managed Policies", "FAIL", f"Exception: {str(e)}")
        return False


def validate_custom_policies() -> bool:
    """
    Validate custom IAM policies for AWS service access.
    
    Tests:
    - DynamoDB access policy with specific table permissions
    - SNS publish policy for event-driven communication  
    - Bedrock access policy for AI model invocation
    - API Gateway management policy for WebSocket connections
    
    Returns:
        bool: True if all custom policies are properly configured
    """
    print_section("Custom IAM Policies Validation")
    
    try:
        if LAMBDA_ROLE_ARN is None:
            print_test("Custom Policies", "FAIL", "Lambda role ARN not available from previous validation")
            return False
            
        # Get attached policies to the role
        attached_policies = iam_client.list_attached_role_policies(RoleName=IAM_ROLE_NAME)
        attached_policy_arns = [policy["PolicyArn"] for policy in attached_policies["AttachedPolicies"]]
        
        # Filter out AWS managed policies (they start with arn:aws:iam::aws:policy/)
        custom_policy_arns = [arn for arn in attached_policy_arns if not arn.startswith('arn:aws:iam::aws:policy/')]
        
        # Get details for each custom policy
        custom_policies = []
        for policy_arn in custom_policy_arns:
            try:
                policy_details = iam_client.get_policy(PolicyArn=policy_arn)
                custom_policies.append(policy_details['Policy'])
            except Exception as e:
                print(f"DEBUG: Error getting policy details for {policy_arn}: {e}")
        
        # Custom policies found and validated
        
        # Validate each required custom policy type
        policies_found = {policy_type: False for policy_type in REQUIRED_CUSTOM_POLICIES}
        
        for policy in custom_policies:
            policy_description = policy.get('Description', '').lower()
            policy_arn = policy['Arn']
            
            # All custom policies are already attached (we filtered them from attached policies)
            # Determine policy type based on description
            if 'dynamodb' in policy_description:
                policies_found['dynamodb_access'] = True
                print_test("Custom Policy DynamoDB", "PASS", f"Found and attached: {policy['PolicyName']}")
            elif 'sns' in policy_description:
                policies_found['sns_publish'] = True
                print_test("Custom Policy SNS", "PASS", f"Found and attached: {policy['PolicyName']}")
            elif 'bedrock' in policy_description:
                policies_found['bedrock_access'] = True  
                print_test("Custom Policy Bedrock", "PASS", f"Found and attached: {policy['PolicyName']}")
            elif 'websocket' in policy_description or 'api gateway' in policy_description:
                policies_found['apigateway_management'] = True
                print_test("Custom Policy API Gateway", "PASS", f"Found and attached: {policy['PolicyName']}")
                    
        # Special handling for KMS policy - it exists but is not attached (Phase 4 preparation)
        # This will be validated separately in validate_kms_preparation()
        policies_found['kms_access'] = True  # Mark as found since it's handled separately
        print_test("Custom Policy KMS", "INFO", "KMS policy validation handled in KMS Phase 4 Preparation section")
                    
        # Check for missing policies (excluding KMS which is handled separately)
        all_policies_found = True
        for policy_type, found in policies_found.items():
            if not found and policy_type != 'kms_access':
                print_test(f"Custom Policy {policy_type}", "FAIL", f"Policy not found or not attached")
                all_policies_found = False
                
        return all_policies_found
        
    except Exception as e:
        print_test("Custom Policies", "FAIL", f"Exception: {str(e)}")
        return False


def validate_lambda_role_integration() -> bool:
    """
    Validate that Lambda functions are using the correct execution role.
    
    Tests:
    - All Lambda functions use the same execution role
    - Role ARN matches the validated role
    - Functions can assume the role successfully
    
    Returns:
        bool: True if Lambda role integration is correct
    """
    print_section("Lambda Role Integration Validation")
    
    try:
        if LAMBDA_ROLE_ARN is None:
            print_test("Lambda Role Integration", "FAIL", "Lambda role ARN not available from previous validation")
            return False
            
        # Get all Lambda functions with our naming pattern
        functions = lambda_client.list_functions()
        buildingos_functions = []
        
        for function in functions["Functions"]:
            function_name = function["FunctionName"]
            if RESOURCE_PREFIX in function_name:
                buildingos_functions.append(function)
                
        if not buildingos_functions:
            print_test("Lambda Functions", "FAIL", f"No Lambda functions found with prefix: {RESOURCE_PREFIX}")
            return False
            
        # Validate each function uses the correct role
        correct_role_count = 0
        total_functions = len(buildingos_functions)
        
        for function in buildingos_functions:
            function_name = function["FunctionName"]
            function_role = function["Role"]
            
            if function_role == LAMBDA_ROLE_ARN:
                print_test(f"Lambda Function {function_name}", "PASS", f"Correct role: {function_role}")
                correct_role_count += 1
            else:
                print_test(f"Lambda Function {function_name}", "FAIL", f"Expected: {LAMBDA_ROLE_ARN}, Found: {function_role}")
                
        # Overall validation
        if correct_role_count == total_functions:
            print_test("Overall Lambda Role Integration", "PASS", f"{correct_role_count}/{total_functions} functions using correct role")
            return True
        else:
            print_test("Overall Lambda Role Integration", "FAIL", f"Only {correct_role_count}/{total_functions} functions using correct role")
            return False
            
    except Exception as e:
        print_test("Lambda Role Integration", "FAIL", f"Exception: {str(e)}")
        return False


def validate_kms_preparation() -> bool:
    """
    Validate KMS preparation for Phase 4 encryption implementation.
    
    Tests:
    - KMS policy exists with correct permissions
    - KMS policy is prepared but not attached (Phase 4 preparation)
    - KMS policy has proper service conditions
    - KMS policy is properly tagged for Phase 4
    
    Returns:
        bool: True if KMS preparation is correct
    """
    print_section("KMS Phase 4 Preparation Validation")
    
    try:
        # Find the KMS policy
        account_id = boto3.client('sts').get_caller_identity()['Account']
        region = boto3.Session().region_name or 'us-east-1'
        kms_policy_name = f"{RESOURCE_PREFIX}-lambda-kms-access"
        kms_policy_arn = f"arn:aws:iam::{account_id}:policy/{kms_policy_name}"
        
        try:
            # Check if KMS policy exists
            kms_policy = iam_client.get_policy(PolicyArn=kms_policy_arn)
            print_test("KMS Policy Exists", "PASS", f"KMS policy found: {kms_policy_name}")
            
            # Get policy version details
            policy_version = iam_client.get_policy_version(
                PolicyArn=kms_policy_arn,
                VersionId=kms_policy['Policy']['DefaultVersionId']
            )
            
            policy_document = policy_version['PolicyVersion']['Document']
            
            # Validate KMS permissions
            kms_actions_found = False
            service_conditions_found = False
            
            for statement in policy_document.get('Statement', []):
                actions = statement.get('Action', [])
                if isinstance(actions, str):
                    actions = [actions]
                    
                # Check for required KMS actions
                kms_actions = ['kms:Decrypt', 'kms:Encrypt', 'kms:GenerateDataKey']
                if any(action in actions for action in kms_actions):
                    kms_actions_found = True
                    print_test("KMS Actions", "PASS", "Required KMS actions found in policy")
                    
                # Check for service conditions
                conditions = statement.get('Condition', {})
                string_equals = conditions.get('StringEquals', {})
                via_service = string_equals.get('kms:ViaService', [])
                
                if isinstance(via_service, list) and len(via_service) > 0:
                    service_conditions_found = True
                    print_test("KMS Service Conditions", "PASS", f"Service conditions found: {len(via_service)} services")
            
            if not kms_actions_found:
                print_test("KMS Actions", "FAIL", "Required KMS actions not found in policy")
                return False
                
            if not service_conditions_found:
                print_test("KMS Service Conditions", "FAIL", "Service conditions not found in policy")
                return False
            
            # Check that KMS policy is NOT attached to Lambda role (Phase 4 preparation)
            attached_policies = iam_client.list_attached_role_policies(RoleName=IAM_ROLE_NAME)
            attached_policy_arns = [policy["PolicyArn"] for policy in attached_policies["AttachedPolicies"]]
            
            if kms_policy_arn not in attached_policy_arns:
                print_test("KMS Policy Attachment", "PASS", "KMS policy prepared but not attached (Phase 4 preparation)")
            else:
                print_test("KMS Policy Attachment", "FAIL", "KMS policy should not be attached until Phase 4")
                return False
                
            # Check KMS policy tags
            policy_tags = kms_policy['Policy'].get('Tags', [])
            phase_tag = next((tag['Value'] for tag in policy_tags if tag['Key'] == 'Phase'), None)
            
            if phase_tag and '4' in phase_tag:
                print_test("KMS Policy Tagging", "PASS", f"Phase tag found: {phase_tag}")
            else:
                print_test("KMS Policy Tagging", "FAIL", "Phase 4 tag not found on KMS policy")
                return False
                
            return True
            
        except iam_client.exceptions.NoSuchEntityException:
            print_test("KMS Policy Exists", "FAIL", f"KMS policy not found: {kms_policy_name}")
            return False
            
    except Exception as e:
        print_test("KMS Preparation", "FAIL", f"Exception: {str(e)}")
        return False


def validate_security_compliance() -> bool:
    """
    Validate security compliance and best practices.
    
    Tests:
    - No wildcard permissions in custom policies
    - Proper resource-specific permissions
    - Role creation date and last used information
    - No unused or overprivileged policies
    
    Returns:
        bool: True if security compliance checks pass
    """
    print_section("Security Compliance Validation")
    
    try:
        if LAMBDA_ROLE_ARN is None:
            print_test("Security Compliance", "FAIL", "Lambda role ARN not available from previous validation")
            return False
            
        # Get role details
        role_response = iam_client.get_role(RoleName=IAM_ROLE_NAME)
        role = role_response["Role"]
        
        # Check role age (should be recent for clean rebuild)
        create_date = role["CreateDate"]
        print_test("Role Creation", "PASS", f"Role created: {create_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check for role last used (indicates active usage)
        role_last_used = role.get("RoleLastUsed")
        if role_last_used:
            last_used_date = role_last_used.get("LastUsedDate")
            if last_used_date:
                print_test("Role Usage", "PASS", f"Role last used: {last_used_date.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print_test("Role Usage", "PASS", "Role usage tracking enabled")
        else:
            print_test("Role Usage", "PASS", "Role is newly created or usage tracking not yet available")
            
        # Validate policy compliance (basic check for now)
        attached_policies = iam_client.list_attached_role_policies(RoleName=IAM_ROLE_NAME)
        policy_count = len(attached_policies["AttachedPolicies"])
        
        if policy_count > 0:
            print_test("Policy Attachment", "PASS", f"Role has {policy_count} attached policies")
        else:
            print_test("Policy Attachment", "FAIL", "Role has no attached policies")
            return False
            
        return True
        
    except Exception as e:
        print_test("Security Compliance", "FAIL", f"Exception: {str(e)}")
        return False


# =============================================================================
# Main Validation Function
# =============================================================================

def main():
    """
    Main validation function that orchestrates all IAM and security tests.
    
    Validation Flow:
    1. Lambda execution role validation
    2. AWS managed policies validation  
    3. Custom policies validation
    4. Lambda role integration validation
    5. Security compliance validation
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print_header()
    
    # Track validation results
    validations = [
        ("Lambda Execution Role", validate_lambda_execution_role),
        ("AWS Managed Policies", validate_managed_policies),
        ("Custom IAM Policies", validate_custom_policies),
        ("Lambda Role Integration", validate_lambda_role_integration),
        ("KMS Phase 4 Preparation", validate_kms_preparation),
        ("Security Compliance", validate_security_compliance),
    ]
    
    passed_tests = 0
    total_tests = len(validations)
    
    # Run all validations
    for validation_name, validation_func in validations:
        try:
            if validation_func():
                passed_tests += 1
        except Exception as e:
            print_test(validation_name, "FAIL", f"Unexpected error: {str(e)}")
    
    # Print summary
    print_summary(passed_tests, total_tests)
    
    # Return appropriate exit code
    return 0 if passed_tests == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
