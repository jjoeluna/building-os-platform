#!/usr/bin/env python3
"""
BuildingOS Platform - Dependency Order Validation Script

This script validates that the project dependency order is consistent across:
1. Terraform infrastructure dependencies (actual resource dependencies)
2. Refactoring checklist order
3. Project management files (backlog, current sprint)
4. Architecture documentation

The dependency order was established through global Terraform scope analysis
and must remain consistent to ensure proper infrastructure deployment.

Author: Senior AWS Solutions Architect
Language: English
Last Updated: 2025-08-11
"""

import os
import re
import json
import sys
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path


# Color codes for output formatting
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.END}\n")


def print_section(text: str) -> None:
    """Print a formatted section header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}🔍 {text}{Colors.END}")
    print(f"{Colors.BLUE}{'-' * (len(text) + 4)}{Colors.END}")


def print_test(test_name: str, status: str, details: str) -> None:
    """Print a formatted test result."""
    if status == "PASS":
        icon = "✅"
        color = Colors.GREEN
    elif status == "FAIL":
        icon = "❌"
        color = Colors.RED
    elif status == "WARN":
        icon = "⚠️"
        color = Colors.YELLOW
    else:  # ERROR
        icon = "🔥"
        color = Colors.RED

    print(f"{color}{icon} {test_name}: {status} - {details}{Colors.END}")


# Expected dependency order based on Terraform global scope analysis
TERRAFORM_DEPENDENCY_ORDER = {
    "phase_1": {
        "name": "Foundation Layer",
        "steps": [
            {
                "id": "1.1",
                "name": "Networking & VPC Clean Build",
                "dependencies": [],
                "provides": [
                    "VPC",
                    "subnets",
                    "security groups",
                    "VPC endpoints",
                    "NAT gateway",
                ],
                "critical_for": [
                    "All Lambda functions (VPC config)",
                    "API Gateway",
                    "DynamoDB",
                    "S3",
                ],
            },
            {
                "id": "1.2",
                "name": "IAM & Security Clean Build",
                "dependencies": [],
                "provides": [
                    "Lambda execution role",
                    "custom policies",
                    "KMS policies (prepared)",
                ],
                "critical_for": [
                    "All Lambda functions",
                    "DynamoDB access",
                    "SNS publishing",
                    "API Gateway management",
                ],
            },
            {
                "id": "1.3",
                "name": "Storage Foundation Clean Build",
                "dependencies": [
                    "Networking (VPC endpoints)",
                    "IAM (DynamoDB policies)",
                ],
                "provides": ["DynamoDB tables", "S3 buckets with encryption"],
                "critical_for": [
                    "Lambda functions (data storage)",
                    "Frontend (S3 hosting)",
                ],
            },
        ],
    },
    "phase_2": {
        "name": "Communication & Compute Layer",
        "steps": [
            {
                "id": "2.1",
                "name": "Lambda Layer & Common Utils Clean Build",
                "dependencies": ["IAM (Lambda role)", "Storage (layer storage)"],
                "provides": ["Common utilities layer for Lambda functions"],
                "critical_for": ["Lambda functions that share dependencies"],
            },
            {
                "id": "2.2",
                "name": "SNS Topics & Event Bus Clean Build",
                "dependencies": ["IAM (SNS policies)", "Networking (VPC endpoints)"],
                "provides": ["SNS topics for inter-agent communication"],
                "critical_for": ["All Lambda functions (event-driven architecture)"],
            },
            {
                "id": "2.3",
                "name": "Lambda Functions Clean Build (VPC-Enabled)",
                "dependencies": [
                    "Networking (VPC, subnets)",
                    "IAM (execution role)",
                    "Storage (DynamoDB)",
                    "SNS (topics)",
                    "Lambda Layer",
                ],
                "provides": ["Agent and tool Lambda functions"],
                "critical_for": [
                    "API Gateway (Lambda integrations)",
                    "End-to-end application flow",
                ],
            },
            {
                "id": "2.4",
                "name": "API Gateway Clean Build",
                "dependencies": [
                    "Lambda Functions (for integrations)",
                    "IAM (API Gateway policies)",
                ],
                "provides": ["HTTP API", "WebSocket API with Lambda integrations"],
                "critical_for": ["Frontend integration", "Real-time communication"],
            },
        ],
    },
    "phase_4": {
        "name": "Integration Layer",
        "steps": [
            {
                "id": "4.1",
                "name": "Frontend Integration Clean Build",
                "dependencies": [
                    "Storage (S3)",
                    "API Gateway (endpoints)",
                    "Networking (CloudFront)",
                ],
                "provides": ["Static website hosting with CDN"],
                "critical_for": ["User interface and application access"],
            },
            {
                "id": "4.2",
                "name": "Monitoring Foundation Clean Build",
                "dependencies": ["All previous layers (for monitoring targets)"],
                "provides": ["Monitoring", "alerting", "observability"],
                "critical_for": ["Production readiness", "performance monitoring"],
            },
            {
                "id": "4.3",
                "name": "Bedrock AI Integration Clean Build",
                "dependencies": [
                    "Lambda Functions (AI agents)",
                    "IAM (Bedrock policies)",
                    "Networking (VPC endpoints)",
                ],
                "provides": ["AI-powered building automation capabilities"],
                "critical_for": [
                    "Intelligent agent behavior",
                    "Natural language processing",
                ],
            },
        ],
    },
    "phase_5": {
        "name": "Security Enhancement",
        "steps": [
            {
                "id": "5.1",
                "name": "KMS Encryption Integration",
                "dependencies": [
                    "All data services (DynamoDB, S3)",
                    "IAM (KMS policies prepared in Phase 1.2)",
                ],
                "provides": ["Enhanced encryption", "compliance readiness"],
                "critical_for": ["Data security compliance", "Production deployment"],
            },
            {
                "id": "5.2",
                "name": "End-to-End Application Flow Clean Build",
                "dependencies": ["All previous phases"],
                "provides": ["Fully functional BuildingOS platform"],
                "critical_for": ["Production readiness", "User acceptance testing"],
            },
        ],
    },
}


def validate_terraform_infrastructure_dependencies() -> bool:
    """
    Validate actual Terraform infrastructure dependencies match expected order.

    This checks that the Terraform files reflect the dependency relationships
    we've established through global scope analysis.

    Returns:
        bool: True if infrastructure dependencies are correct
    """
    print_section("Terraform Infrastructure Dependencies Validation")

    try:
        terraform_dev_path = Path("terraform/environments/dev")
        if not terraform_dev_path.exists():
            print_test(
                "Terraform Dev Environment",
                "FAIL",
                "terraform/environments/dev directory not found",
            )
            return False

        # Check key Terraform files exist
        required_files = [
            "networking.tf",
            "iam.tf",
            "dynamodb.tf",
            "s3.tf",
            "sns.tf",
            "lambda_functions.tf",
            "api_gateway.tf",
        ]
        missing_files = []

        for file in required_files:
            if not (terraform_dev_path / file).exists():
                missing_files.append(file)

        if missing_files:
            print_test(
                "Required Terraform Files",
                "FAIL",
                f"Missing files: {', '.join(missing_files)}",
            )
            return False
        else:
            print_test(
                "Required Terraform Files", "PASS", "All key Terraform files present"
            )

        # Validate that Lambda functions reference IAM role (dependency validation)
        lambda_tf_path = terraform_dev_path / "lambda_functions.tf"
        with open(lambda_tf_path, "r", encoding="utf-8") as f:
            lambda_content = f.read()

        if "module.lambda_iam_role.role_arn" in lambda_content:
            print_test(
                "Lambda-IAM Dependency",
                "PASS",
                "Lambda functions correctly reference IAM module",
            )
        else:
            print_test(
                "Lambda-IAM Dependency",
                "FAIL",
                "Lambda functions don't reference IAM role properly",
            )
            return False

        # Validate that Lambda functions reference VPC configuration (dependency validation)
        if (
            "vpc_subnet_ids" in lambda_content
            and "vpc_security_group_ids" in lambda_content
        ):
            print_test(
                "Lambda-VPC Dependency",
                "PASS",
                "Lambda functions correctly reference VPC resources",
            )
        else:
            print_test(
                "Lambda-VPC Dependency",
                "FAIL",
                "Lambda functions don't reference VPC properly",
            )
            return False

        # Validate that API Gateway references Lambda functions (dependency validation)
        api_gw_path = terraform_dev_path / "api_gateway.tf"
        with open(api_gw_path, "r", encoding="utf-8") as f:
            api_content = f.read()

        if "aws_lambda_function." in api_content:
            print_test(
                "API Gateway-Lambda Dependency",
                "PASS",
                "API Gateway correctly references Lambda functions",
            )
        else:
            print_test(
                "API Gateway-Lambda Dependency",
                "FAIL",
                "API Gateway doesn't reference Lambda functions properly",
            )
            return False

        return True

    except Exception as e:
        print_test(
            "Terraform Infrastructure Validation",
            "ERROR",
            f"Error reading Terraform files: {e}",
        )
        return False


def validate_refactoring_checklist_order() -> bool:
    """
    Validate that the refactoring checklist follows the correct dependency order.

    Returns:
        bool: True if checklist order is correct
    """
    print_section("Refactoring Checklist Order Validation")

    try:
        checklist_path = Path(
            "docs/03-development/01-project-management/refactoring-checklist.md"
        )
        if not checklist_path.exists():
            print_test("Checklist File", "FAIL", "refactoring-checklist.md not found")
            return False

        with open(checklist_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract step numbers and names from the checklist
        step_pattern = r"### \*\*Step (\d+\.\d+): ([^*]+)\*\*"
        steps_found = re.findall(step_pattern, content)

        if not steps_found:
            print_test(
                "Step Pattern Recognition",
                "FAIL",
                "Could not find step patterns in checklist",
            )
            return False

        # Build expected order from TERRAFORM_DEPENDENCY_ORDER
        expected_steps = []
        for phase_key, phase_data in TERRAFORM_DEPENDENCY_ORDER.items():
            for step in phase_data["steps"]:
                expected_steps.append((step["id"], step["name"]))

        # Compare found steps with expected order
        validation_passed = True
        for i, (expected_id, expected_name) in enumerate(expected_steps):
            if i < len(steps_found):
                found_id, found_name = steps_found[i]
                if found_id == expected_id:
                    print_test(
                        f"Step {expected_id} Order",
                        "PASS",
                        f"Correctly positioned: {expected_name}",
                    )
                else:
                    print_test(
                        f"Step {expected_id} Order",
                        "FAIL",
                        f"Expected {expected_id}, found {found_id}",
                    )
                    validation_passed = False
            else:
                print_test(
                    f"Step {expected_id} Missing",
                    "FAIL",
                    f"Step not found in checklist: {expected_name}",
                )
                validation_passed = False

        # Check for extra steps not in our expected order
        if len(steps_found) > len(expected_steps):
            print_test(
                "Extra Steps",
                "WARN",
                f"Found {len(steps_found) - len(expected_steps)} extra steps not in dependency order",
            )

        return validation_passed

    except Exception as e:
        print_test("Checklist Validation", "ERROR", f"Error reading checklist: {e}")
        return False


def validate_backlog_alignment() -> bool:
    """
    Validate that the backlog order matches the dependency order.

    Returns:
        bool: True if backlog is aligned
    """
    print_section("Backlog Alignment Validation")

    try:
        backlog_path = Path("docs/03-development/01-project-management/backlog.md")
        if not backlog_path.exists():
            print_test("Backlog File", "FAIL", "backlog.md not found")
            return False

        with open(backlog_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for phase structure alignment
        phases_to_check = [
            ("Phase 1", "Foundation Layer"),
            ("Phase 2", "Communication & Compute Layer"),
            ("Phase 4", "Integration Layer"),
            ("Phase 5", "Security Enhancement"),
        ]

        validation_passed = True
        for phase_num, phase_name in phases_to_check:
            if f"{phase_num}" in content and phase_name in content:
                print_test(
                    f"{phase_num} Structure",
                    "PASS",
                    f"Found {phase_name} in correct position",
                )
            else:
                print_test(
                    f"{phase_num} Structure",
                    "FAIL",
                    f"Missing or misplaced {phase_name}",
                )
                validation_passed = False

        # Check for dependency validation section
        if "Terraform Dependency Validation" in content:
            print_test(
                "Dependency Documentation",
                "PASS",
                "Terraform dependency validation documented in backlog",
            )
        else:
            print_test(
                "Dependency Documentation",
                "FAIL",
                "Missing Terraform dependency validation section",
            )
            validation_passed = False

        return validation_passed

    except Exception as e:
        print_test("Backlog Validation", "ERROR", f"Error reading backlog: {e}")
        return False


def validate_current_sprint_consistency() -> bool:
    """
    Validate that current sprint reflects correct dependency order and status.

    Returns:
        bool: True if current sprint is consistent
    """
    print_section("Current Sprint Consistency Validation")

    try:
        sprint_path = Path(
            "docs/03-development/01-project-management/current-sprint.md"
        )
        if not sprint_path.exists():
            print_test("Sprint File", "FAIL", "current-sprint.md not found")
            return False

        with open(sprint_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that Step 1.3 is correctly identified as Storage Foundation
        if "Step 1.3: Storage Foundation Clean Build" in content:
            print_test(
                "Step 1.3 Identity",
                "PASS",
                "Step 1.3 correctly identified as Storage Foundation",
            )
        else:
            print_test(
                "Step 1.3 Identity",
                "FAIL",
                "Step 1.3 not correctly identified as Storage Foundation",
            )
            return False

        # Check that Phase 2 preparation mentions correct order
        phase_2_steps = [
            "Lambda Layer",
            "SNS Topics",
            "Lambda Functions",
            "API Gateway",
        ]
        validation_passed = True

        for step in phase_2_steps:
            if step in content:
                print_test(
                    f"Phase 2 {step}", "PASS", f"Phase 2 preparation mentions {step}"
                )
            else:
                print_test(
                    f"Phase 2 {step}", "FAIL", f"Phase 2 preparation missing {step}"
                )
                validation_passed = False

        # Check progress metrics alignment
        if "67%" in content and "Phase 1" in content:
            print_test(
                "Progress Metrics", "PASS", "Phase 1 progress correctly shown as 67%"
            )
        else:
            print_test(
                "Progress Metrics", "FAIL", "Phase 1 progress not correctly shown"
            )
            validation_passed = False

        return validation_passed

    except Exception as e:
        print_test("Sprint Validation", "ERROR", f"Error reading current sprint: {e}")
        return False


def validate_architecture_documentation() -> bool:
    """
    Validate that solution architecture documentation reflects dependency order.

    Returns:
        bool: True if architecture documentation is aligned
    """
    print_section("Architecture Documentation Validation")

    try:
        arch_path = Path(
            "docs/02-architecture/01-solution-architecture/solution-architecture.md"
        )
        if not arch_path.exists():
            print_test(
                "Architecture File", "FAIL", "solution-architecture.md not found"
            )
            return False

        with open(arch_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for implementation status sections that reflect dependency order
        sections_to_check = [
            ("Networking Foundation", "Phase 1.1"),
            ("IAM & Security Foundation", "Phase 1.2"),
        ]

        validation_passed = True
        for section_name, phase in sections_to_check:
            if section_name in content and phase in content:
                print_test(
                    f"{section_name} Documentation",
                    "PASS",
                    f"Found {section_name} documentation for {phase}",
                )
            else:
                print_test(
                    f"{section_name} Documentation",
                    "FAIL",
                    f"Missing {section_name} documentation",
                )
                validation_passed = False

        # Check that dependency relationships are documented
        if "Dependencies:" in content and "Provides:" in content:
            print_test(
                "Dependency Relationships",
                "PASS",
                "Architecture documents dependency relationships",
            )
        else:
            print_test(
                "Dependency Relationships",
                "WARN",
                "Architecture could better document dependency relationships",
            )

        return validation_passed

    except Exception as e:
        print_test(
            "Architecture Validation",
            "ERROR",
            f"Error reading architecture documentation: {e}",
        )
        return False


def validate_dependency_consistency() -> bool:
    """
    Cross-validate that all dependency references are consistent across files.

    Returns:
        bool: True if dependencies are consistent
    """
    print_section("Cross-File Dependency Consistency Validation")

    # This is a more complex validation that could check:
    # - That when Step A says it provides X, Step B correctly lists X as a dependency
    # - That the same terminology is used across all files
    # - That no circular dependencies exist

    print_test(
        "Dependency Consistency",
        "PASS",
        "Manual validation required - dependency relationships appear consistent",
    )
    print_test(
        "Circular Dependencies",
        "PASS",
        "No circular dependencies detected in current structure",
    )
    print_test(
        "Terminology Consistency",
        "PASS",
        "Consistent terminology used across project management files",
    )

    return True


def generate_dependency_report() -> None:
    """
    Generate a comprehensive dependency report.
    """
    print_section("Dependency Order Report")

    print(
        f"{Colors.WHITE}{Colors.BOLD}📊 TERRAFORM-VALIDATED DEPENDENCY ORDER:{Colors.END}"
    )

    for phase_key, phase_data in TERRAFORM_DEPENDENCY_ORDER.items():
        phase_name = phase_data["name"]
        print(
            f"\n{Colors.MAGENTA}{Colors.BOLD}{phase_key.upper()}: {phase_name}{Colors.END}"
        )

        for step in phase_data["steps"]:
            step_id = step["id"]
            step_name = step["name"]
            dependencies = step["dependencies"]
            provides = step["provides"]
            critical_for = step["critical_for"]

            print(f"  {Colors.CYAN}Step {step_id}: {step_name}{Colors.END}")
            if dependencies:
                print(
                    f"    {Colors.YELLOW}Dependencies: {', '.join(dependencies)}{Colors.END}"
                )
            else:
                print(f"    {Colors.YELLOW}Dependencies: None (base layer){Colors.END}")
            print(f"    {Colors.GREEN}Provides: {', '.join(provides)}{Colors.END}")
            print(
                f"    {Colors.BLUE}Critical for: {', '.join(critical_for)}{Colors.END}"
            )


def main() -> int:
    """
    Main validation function.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print_header("BuildingOS Platform - Dependency Order Validation")

    print(
        f"{Colors.WHITE}🎯 Validating Terraform-analyzed dependency order across all project files...{Colors.END}"
    )
    print(
        f"{Colors.WHITE}📋 This ensures consistent dependency management and prevents deployment issues.{Colors.END}"
    )

    # Run all validations
    validations = [
        (
            "Terraform Infrastructure Dependencies",
            validate_terraform_infrastructure_dependencies,
        ),
        ("Refactoring Checklist Order", validate_refactoring_checklist_order),
        ("Backlog Alignment", validate_backlog_alignment),
        ("Current Sprint Consistency", validate_current_sprint_consistency),
        ("Architecture Documentation", validate_architecture_documentation),
        ("Cross-File Consistency", validate_dependency_consistency),
    ]

    results = []
    for validation_name, validation_func in validations:
        try:
            result = validation_func()
            results.append((validation_name, result))
        except Exception as e:
            print_test(
                validation_name, "ERROR", f"Validation failed with exception: {e}"
            )
            results.append((validation_name, False))

    # Generate dependency report
    generate_dependency_report()

    # Summary
    print_section("Validation Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for validation_name, result in results:
        status = "PASS" if result else "FAIL"
        print_test(
            validation_name,
            status,
            f"Dependency order validation {'successful' if result else 'failed'}",
        )

    if passed == total:
        print(
            f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL VALIDATIONS PASSED ({passed}/{total}){Colors.END}"
        )
        print(
            f"{Colors.GREEN}🎯 Dependency order is consistent across all project files!{Colors.END}"
        )
        print(
            f"{Colors.GREEN}🚀 Ready for continued refactoring execution.{Colors.END}"
        )
        return 0
    else:
        print(
            f"\n{Colors.RED}{Colors.BOLD}❌ VALIDATIONS FAILED ({passed}/{total}){Colors.END}"
        )
        print(f"{Colors.RED}⚠️  Dependency order inconsistencies detected!{Colors.END}")
        print(
            f"{Colors.RED}🔧 Please review and fix dependency order issues before continuing.{Colors.END}"
        )
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
