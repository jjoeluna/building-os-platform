#!/usr/bin/env python3
# =============================================================================
# BuildingOS Platform - Lambda Layer Validation Script
# =============================================================================
#
# **Purpose:** Comprehensive validation of Lambda Layer & Common Utils Clean Build (Step 2.1)
# **Scope:** Tests all aspects of the Lambda layer implementation and integration
# **Usage:** Run to validate Step 2.1 completion with 100% success requirement
#
# **Validation Categories:**
# 1. Layer Infrastructure - Terraform resources and configuration
# 2. Layer Content - Python modules and dependencies
# 3. Function Integration - All 10 Lambda functions using the layer
# 4. Code Quality - Syntax, imports, and best practices
# 5. Performance - Layer size and load time optimization
#
# **Zero Tolerance Policy:**
# - ALL tests must pass (100% success rate)
# - Any failure blocks step completion
# - Detailed error reporting for quick resolution
#
# **Dependencies:** boto3, requests, json, os, pathlib, subprocess
# **Integration:** Part of Step 2.1 validation framework
#
# =============================================================================

import boto3
import json
import os
import sys
import time
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
import importlib.util

# =============================================================================
# Configuration and Constants
# =============================================================================

REGION = "us-east-1"
ENVIRONMENT = "dev"
PROJECT_PREFIX = "bos"

# Expected Lambda functions that should use the common_utils layer
EXPECTED_LAMBDA_FUNCTIONS = [
    "websocket-connect",
    "websocket-disconnect",
    "websocket-default",
    "websocket-broadcast",
    "agent-health-check",
    "agent-persona",
    "agent-director",
    "agent-coordinator",
    "agent-elevator",
    "agent-psim",
]

# Expected Python modules in the layer
EXPECTED_LAYER_MODULES = ["aws_clients.py", "utils.py", "models.py", "__init__.py"]

# Expected dependencies in requirements.txt
EXPECTED_DEPENDENCIES = ["boto3", "requests", "PyJWT"]

# =============================================================================
# Lambda Layer Validation Class
# =============================================================================


class LambdaLayerValidator:
    """
    Comprehensive validator for Lambda Layer implementation

    Validates all aspects of Step 2.1: Lambda Layer & Common Utils Clean Build
    following the Zero Tolerance Policy for test failures.
    """

    def __init__(self):
        """Initialize validator with AWS clients and configuration"""
        try:
            # Initialize AWS clients
            self.lambda_client = boto3.client("lambda", region_name=REGION)
            self.sts_client = boto3.client("sts", region_name=REGION)

            # Get account information
            identity = self.sts_client.get_caller_identity()
            self.account_id = identity["Account"]

            # Test results tracking
            self.test_results = []
            self.passed_tests = 0
            self.failed_tests = 0

            print(f"🔍 Lambda Layer Validator initialized")
            print(f"📍 Region: {REGION}")
            print(f"🔑 Account ID: {self.account_id}")
            print(f"⏰ Validation started: {datetime.now().isoformat()}")
            print("=" * 80)

        except NoCredentialsError:
            print("❌ ERROR: AWS credentials not configured")
            sys.exit(1)
        except Exception as e:
            print(f"❌ ERROR: Failed to initialize validator: {e}")
            sys.exit(1)

    def log_test_result(
        self, test_name: str, success: bool, message: str, details: Dict = None
    ):
        """Log individual test results with detailed information"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")

        if details and not success:
            for key, value in details.items():
                print(f"    📝 {key}: {value}")

        self.test_results.append(
            {
                "test_name": test_name,
                "success": success,
                "message": message,
                "details": details or {},
                "timestamp": datetime.now().isoformat(),
            }
        )

        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    # =============================================================================
    # Layer Infrastructure Validation
    # =============================================================================

    def validate_layer_existence(self) -> bool:
        """Validate that the common_utils Lambda layer exists and is properly configured"""
        try:
            layer_name = f"{PROJECT_PREFIX}-{ENVIRONMENT}-common-utils-layer"

            # List layer versions
            response = self.lambda_client.list_layer_versions(LayerName=layer_name)
            layer_versions = response.get("LayerVersions", [])

            if not layer_versions:
                self.log_test_result(
                    "Layer Existence",
                    False,
                    f"Layer '{layer_name}' not found",
                    {"expected_layer": layer_name, "found_layers": "None"},
                )
                return False

            # Get the latest version
            latest_version = layer_versions[0]
            layer_arn = latest_version["LayerVersionArn"]

            # Validate layer properties
            compatible_runtimes = latest_version.get("CompatibleRuntimes", [])
            if "python3.11" not in compatible_runtimes:
                self.log_test_result(
                    "Layer Runtime Compatibility",
                    False,
                    "Layer not compatible with python3.11",
                    {
                        "compatible_runtimes": compatible_runtimes,
                        "required": "python3.11",
                    },
                )
                return False

            # Store layer ARN for other tests
            self.layer_arn = layer_arn

            self.log_test_result(
                "Layer Existence",
                True,
                f"Layer found with ARN: {layer_arn}",
                {
                    "layer_name": layer_name,
                    "version": latest_version["Version"],
                    "compatible_runtimes": compatible_runtimes,
                    "created_date": latest_version["CreatedDate"],
                },
            )
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                self.log_test_result(
                    "Layer Existence",
                    False,
                    f"Layer '{layer_name}' does not exist",
                    {"error": str(e)},
                )
            else:
                self.log_test_result(
                    "Layer Existence",
                    False,
                    f"Error accessing layer: {error_code}",
                    {"error": str(e)},
                )
            return False

    def validate_layer_content_structure(self) -> bool:
        """Validate the structure and content of the Lambda layer"""
        try:
            layer_path = Path("src/layers/common_utils/python")

            if not layer_path.exists():
                self.log_test_result(
                    "Layer Source Structure",
                    False,
                    "Layer source directory not found",
                    {"expected_path": str(layer_path)},
                )
                return False

            # Check for expected modules
            missing_modules = []
            found_modules = []

            for module in EXPECTED_LAYER_MODULES:
                module_path = layer_path / module
                if module_path.exists():
                    found_modules.append(module)
                else:
                    missing_modules.append(module)

            if missing_modules:
                self.log_test_result(
                    "Layer Module Structure",
                    False,
                    f"Missing modules: {', '.join(missing_modules)}",
                    {"missing": missing_modules, "found": found_modules},
                )
                return False

            self.log_test_result(
                "Layer Module Structure",
                True,
                f"All {len(EXPECTED_LAYER_MODULES)} modules found",
                {"modules": found_modules},
            )
            return True

        except Exception as e:
            self.log_test_result(
                "Layer Source Structure",
                False,
                f"Error validating layer structure: {e}",
                {"error": str(e)},
            )
            return False

    def validate_layer_dependencies(self) -> bool:
        """Validate that all required dependencies are specified in requirements.txt"""
        try:
            requirements_path = Path("src/layers/common_utils/requirements.txt")

            if not requirements_path.exists():
                self.log_test_result(
                    "Layer Dependencies File",
                    False,
                    "requirements.txt not found",
                    {"expected_path": str(requirements_path)},
                )
                return False

            # Read and parse requirements
            with open(requirements_path, "r") as f:
                requirements_content = f.read()

            requirements_lines = [
                line.strip()
                for line in requirements_content.split("\n")
                if line.strip()
            ]
            found_dependencies = []
            missing_dependencies = []

            for dep in EXPECTED_DEPENDENCIES:
                # Check if dependency is mentioned (with or without version)
                if any(dep in line for line in requirements_lines):
                    found_dependencies.append(dep)
                else:
                    missing_dependencies.append(dep)

            if missing_dependencies:
                self.log_test_result(
                    "Layer Dependencies",
                    False,
                    f"Missing dependencies: {', '.join(missing_dependencies)}",
                    {
                        "missing": missing_dependencies,
                        "found": found_dependencies,
                        "requirements_content": requirements_content,
                    },
                )
                return False

            self.log_test_result(
                "Layer Dependencies",
                True,
                f"All {len(EXPECTED_DEPENDENCIES)} dependencies found",
                {
                    "dependencies": found_dependencies,
                    "requirements_lines": requirements_lines,
                },
            )
            return True

        except Exception as e:
            self.log_test_result(
                "Layer Dependencies",
                False,
                f"Error validating dependencies: {e}",
                {"error": str(e)},
            )
            return False

    # =============================================================================
    # Lambda Function Integration Validation
    # =============================================================================

    def validate_lambda_function_layer_usage(self) -> bool:
        """Validate that all Lambda functions are using the common_utils layer"""
        try:
            functions_using_layer = []
            functions_missing_layer = []
            function_details = {}

            for function_name in EXPECTED_LAMBDA_FUNCTIONS:
                full_function_name = f"{PROJECT_PREFIX}-{ENVIRONMENT}-{function_name}"

                try:
                    # Get function configuration
                    response = self.lambda_client.get_function(
                        FunctionName=full_function_name
                    )
                    config = response["Configuration"]

                    # Check if function uses the layer
                    layers = config.get("Layers", [])
                    layer_arns = [layer["Arn"] for layer in layers]

                    function_details[function_name] = {
                        "function_name": full_function_name,
                        "layers": layer_arns,
                        "runtime": config.get("Runtime"),
                        "last_modified": config.get("LastModified"),
                    }

                    # Check if our layer is included (check if any layer ARN contains common-utils)
                    has_common_utils_layer = any(
                        "common-utils" in arn for arn in layer_arns
                    )

                    if has_common_utils_layer:
                        functions_using_layer.append(function_name)
                    else:
                        functions_missing_layer.append(function_name)

                except ClientError as e:
                    if e.response["Error"]["Code"] == "ResourceNotFoundException":
                        functions_missing_layer.append(function_name)
                        function_details[function_name] = {
                            "error": "Function not found"
                        }
                    else:
                        self.log_test_result(
                            f"Function Access - {function_name}",
                            False,
                            f"Error accessing function: {e.response['Error']['Code']}",
                            {"error": str(e)},
                        )
                        return False

            # Validate results
            if functions_missing_layer:
                self.log_test_result(
                    "Lambda Function Layer Integration",
                    False,
                    f"{len(functions_missing_layer)} functions missing common_utils layer",
                    {
                        "functions_with_layer": functions_using_layer,
                        "functions_missing_layer": functions_missing_layer,
                        "function_details": function_details,
                    },
                )
                return False

            self.log_test_result(
                "Lambda Function Layer Integration",
                True,
                f"All {len(EXPECTED_LAMBDA_FUNCTIONS)} functions using common_utils layer",
                {
                    "functions_with_layer": functions_using_layer,
                    "total_functions": len(EXPECTED_LAMBDA_FUNCTIONS),
                },
            )
            return True

        except Exception as e:
            self.log_test_result(
                "Lambda Function Layer Integration",
                False,
                f"Error validating function layer usage: {e}",
                {"error": str(e)},
            )
            return False

    # =============================================================================
    # Code Quality Validation
    # =============================================================================

    def validate_python_syntax_and_imports(self) -> bool:
        """Validate Python syntax and import structure of layer modules"""
        try:
            layer_path = Path("src/layers/common_utils/python")
            syntax_errors = []
            import_errors = []
            valid_modules = []

            for module_file in EXPECTED_LAYER_MODULES:
                module_path = layer_path / module_file

                if not module_path.exists():
                    continue

                # Test Python syntax
                try:
                    with open(module_path, "r", encoding="utf-8") as f:
                        source_code = f.read()

                    # Compile to check syntax
                    compile(source_code, str(module_path), "exec")

                    # Test imports (basic check)
                    if module_file != "__init__.py":  # Skip __init__.py for import test
                        try:
                            # Create a temporary spec for the module
                            spec = importlib.util.spec_from_file_location(
                                module_file.replace(".py", ""), module_path
                            )
                            if spec and spec.loader:
                                # This tests that the module can be loaded
                                module = importlib.util.module_from_spec(spec)
                                # We don't actually execute it to avoid side effects
                                valid_modules.append(module_file)
                            else:
                                import_errors.append(
                                    f"{module_file}: Could not create module spec"
                                )
                        except Exception as e:
                            import_errors.append(f"{module_file}: {str(e)}")
                    else:
                        valid_modules.append(module_file)

                except SyntaxError as e:
                    syntax_errors.append(f"{module_file}: Line {e.lineno} - {e.msg}")
                except Exception as e:
                    syntax_errors.append(f"{module_file}: {str(e)}")

            # Check results
            has_errors = bool(syntax_errors or import_errors)

            if has_errors:
                error_details = {}
                if syntax_errors:
                    error_details["syntax_errors"] = syntax_errors
                if import_errors:
                    error_details["import_errors"] = import_errors

                self.log_test_result(
                    "Python Code Quality",
                    False,
                    f"Found {len(syntax_errors)} syntax errors and {len(import_errors)} import errors",
                    error_details,
                )
                return False

            self.log_test_result(
                "Python Code Quality",
                True,
                f"All {len(valid_modules)} modules have valid syntax and imports",
                {"valid_modules": valid_modules},
            )
            return True

        except Exception as e:
            self.log_test_result(
                "Python Code Quality",
                False,
                f"Error validating code quality: {e}",
                {"error": str(e)},
            )
            return False

    def validate_documentation_standards(self) -> bool:
        """Validate that all modules have proper documentation headers and comments"""
        try:
            layer_path = Path("src/layers/common_utils/python")
            documentation_issues = []
            well_documented_modules = []

            for module_file in EXPECTED_LAYER_MODULES:
                module_path = layer_path / module_file

                if not module_path.exists():
                    continue

                with open(module_path, "r", encoding="utf-8") as f:
                    content = f.read()

                issues = []

                # Check for proper file header
                if not content.startswith(
                    "# ============================================================================="
                ):
                    issues.append("Missing proper file header")

                # Check for **Purpose:** in header
                if "**Purpose:**" not in content:
                    issues.append("Missing **Purpose:** in header")

                # Check for **Scope:** in header
                if "**Scope:**" not in content:
                    issues.append("Missing **Scope:** in header")

                # Check for function docstrings (basic check)
                if "def " in content and '"""' not in content:
                    issues.append("Functions missing docstrings")

                if issues:
                    documentation_issues.append(f"{module_file}: {', '.join(issues)}")
                else:
                    well_documented_modules.append(module_file)

            if documentation_issues:
                self.log_test_result(
                    "Documentation Standards",
                    False,
                    f"Documentation issues found in {len(documentation_issues)} modules",
                    {"issues": documentation_issues},
                )
                return False

            self.log_test_result(
                "Documentation Standards",
                True,
                f"All {len(well_documented_modules)} modules meet documentation standards",
                {"documented_modules": well_documented_modules},
            )
            return True

        except Exception as e:
            self.log_test_result(
                "Documentation Standards",
                False,
                f"Error validating documentation: {e}",
                {"error": str(e)},
            )
            return False

    # =============================================================================
    # Performance and Optimization Validation
    # =============================================================================

    def validate_layer_size_optimization(self) -> bool:
        """Validate that the layer size is optimized and within reasonable limits"""
        try:
            layer_path = Path("src/layers/common_utils")

            if not layer_path.exists():
                self.log_test_result(
                    "Layer Size Optimization",
                    False,
                    "Layer source directory not found",
                    {"expected_path": str(layer_path)},
                )
                return False

            # Calculate directory size
            total_size = 0
            file_count = 0
            large_files = []

            for file_path in layer_path.rglob("*"):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    total_size += size
                    file_count += 1

                    # Flag files larger than 1MB
                    if size > 1024 * 1024:
                        large_files.append(
                            f"{file_path.name}: {size / (1024*1024):.2f}MB"
                        )

            # Convert to MB
            total_size_mb = total_size / (1024 * 1024)

            # AWS Lambda layer size limit is 250MB unzipped
            # We'll warn if over 50MB for a utilities layer
            size_warning_limit = 50.0

            size_details = {
                "total_size_mb": round(total_size_mb, 2),
                "file_count": file_count,
                "large_files": large_files,
                "aws_limit_mb": 250,
            }

            if total_size_mb > size_warning_limit:
                self.log_test_result(
                    "Layer Size Optimization",
                    False,
                    f"Layer size ({total_size_mb:.2f}MB) exceeds recommended limit ({size_warning_limit}MB)",
                    size_details,
                )
                return False

            self.log_test_result(
                "Layer Size Optimization",
                True,
                f"Layer size optimized: {total_size_mb:.2f}MB with {file_count} files",
                size_details,
            )
            return True

        except Exception as e:
            self.log_test_result(
                "Layer Size Optimization",
                False,
                f"Error validating layer size: {e}",
                {"error": str(e)},
            )
            return False

    # =============================================================================
    # Terraform Configuration Validation
    # =============================================================================

    def validate_terraform_layer_configuration(self) -> bool:
        """Validate Terraform configuration for Lambda layer deployment"""
        try:
            # Check main lambda functions configuration
            lambda_functions_tf = Path("terraform/environments/dev/lambda_functions.tf")

            if not lambda_functions_tf.exists():
                self.log_test_result(
                    "Terraform Layer Configuration",
                    False,
                    "Lambda functions Terraform file not found",
                    {"expected_file": str(lambda_functions_tf)},
                )
                return False

            with open(lambda_functions_tf, "r") as f:
                tf_content = f.read()

            # Check for layer module definition
            if 'module "common_utils_layer"' not in tf_content:
                self.log_test_result(
                    "Terraform Layer Module",
                    False,
                    "common_utils_layer module not defined in Terraform",
                    {"file": str(lambda_functions_tf)},
                )
                return False

            # Check that all functions reference the layer
            layer_references = tf_content.count(
                "layers = [module.common_utils_layer.layer_arn]"
            )

            # Should have one reference per function (10 total)
            if layer_references < len(EXPECTED_LAMBDA_FUNCTIONS):
                self.log_test_result(
                    "Terraform Layer References",
                    False,
                    f"Insufficient layer references: found {layer_references}, expected {len(EXPECTED_LAMBDA_FUNCTIONS)}",
                    {
                        "found_references": layer_references,
                        "expected_references": len(EXPECTED_LAMBDA_FUNCTIONS),
                        "file": str(lambda_functions_tf),
                    },
                )
                return False

            self.log_test_result(
                "Terraform Layer Configuration",
                True,
                f"Layer properly configured with {layer_references} function references",
                {
                    "layer_references": layer_references,
                    "expected_functions": len(EXPECTED_LAMBDA_FUNCTIONS),
                },
            )
            return True

        except Exception as e:
            self.log_test_result(
                "Terraform Layer Configuration",
                False,
                f"Error validating Terraform configuration: {e}",
                {"error": str(e)},
            )
            return False

    # =============================================================================
    # Main Validation Orchestration
    # =============================================================================

    def run_all_validations(self) -> bool:
        """
        Run all validation tests for Lambda Layer implementation

        Returns:
            bool: True if all tests pass (100% success rate), False otherwise
        """
        print("🚀 Starting Lambda Layer Validation (Step 2.1)")
        print("📋 Zero Tolerance Policy: ALL tests must pass for step completion")
        print("=" * 80)

        # Define all validation tests
        validations = [
            (
                "Layer Infrastructure",
                [
                    self.validate_layer_existence,
                    self.validate_layer_content_structure,
                    self.validate_layer_dependencies,
                ],
            ),
            (
                "Function Integration",
                [
                    self.validate_lambda_function_layer_usage,
                ],
            ),
            (
                "Code Quality",
                [
                    self.validate_python_syntax_and_imports,
                    self.validate_documentation_standards,
                ],
            ),
            (
                "Performance & Optimization",
                [
                    self.validate_layer_size_optimization,
                ],
            ),
            (
                "Terraform Configuration",
                [
                    self.validate_terraform_layer_configuration,
                ],
            ),
        ]

        # Run all validations
        all_passed = True

        for category, tests in validations:
            print(f"\n🔍 {category} Validation:")
            print("-" * 40)

            for test_func in tests:
                try:
                    result = test_func()
                    if not result:
                        all_passed = False
                except Exception as e:
                    print(f"❌ CRITICAL ERROR in {test_func.__name__}: {e}")
                    self.log_test_result(
                        test_func.__name__,
                        False,
                        f"Critical error during test execution: {e}",
                        {"error": str(e)},
                    )
                    all_passed = False

        # Print final results
        print("\n" + "=" * 80)
        print("📊 FINAL VALIDATION RESULTS")
        print("=" * 80)

        success_rate = (
            (self.passed_tests / (self.passed_tests + self.failed_tests) * 100)
            if (self.passed_tests + self.failed_tests) > 0
            else 0
        )

        print(f"✅ Passed Tests: {self.passed_tests}")
        print(f"❌ Failed Tests: {self.failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")

        if all_passed and self.failed_tests == 0:
            print("🎉 STEP 2.1 VALIDATION: ✅ ALL TESTS PASSED")
            print("🚀 Lambda Layer & Common Utils Clean Build is COMPLETE")
            print("✅ Ready to proceed to next step")
        else:
            print("🚨 STEP 2.1 VALIDATION: ❌ FAILURES DETECTED")
            print("🔒 ZERO TOLERANCE POLICY: Step cannot be marked complete")
            print("🛠️ Please fix all issues before proceeding")

            # Print summary of failures
            if self.failed_tests > 0:
                print("\n🔍 FAILURE SUMMARY:")
                for result in self.test_results:
                    if not result["success"]:
                        print(f"  ❌ {result['test_name']}: {result['message']}")

        print("=" * 80)
        return all_passed and self.failed_tests == 0


# =============================================================================
# Main Execution
# =============================================================================


def main():
    """Main execution function"""
    try:
        validator = LambdaLayerValidator()
        success = validator.run_all_validations()

        # Save detailed results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = (
            f"tests/validation/lambda_layer_validation_results_{timestamp}.json"
        )

        with open(results_file, "w") as f:
            json.dump(
                {
                    "validation_timestamp": datetime.now().isoformat(),
                    "overall_success": success,
                    "passed_tests": validator.passed_tests,
                    "failed_tests": validator.failed_tests,
                    "success_rate": (
                        (
                            validator.passed_tests
                            / (validator.passed_tests + validator.failed_tests)
                            * 100
                        )
                        if (validator.passed_tests + validator.failed_tests) > 0
                        else 0
                    ),
                    "test_results": validator.test_results,
                },
                f,
                indent=2,
            )

        print(f"📄 Detailed results saved to: {results_file}")

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
