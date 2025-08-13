#!/usr/bin/env python3
# =============================================================================
# BuildingOS Platform - Lambda Functions Validation Script (Step 2.3)
# =============================================================================
#
# **Purpose:** Comprehensive validation of all Lambda functions after enhancement
# **Scope:** Tests code quality, integration, and enterprise standards compliance
# **Usage:** python validate_lambda_functions_step.py
#
# **Validation Categories:**
# 1. **Code Quality:** Syntax, imports, type annotations, docstrings
# 2. **Common Layer Integration:** AWS clients, utilities, models usage
# 3. **Error Handling:** Exception handling, logging, correlation IDs
# 4. **Function Architecture:** Event routing, helper functions, modularity
# 5. **AWS Integration:** Lambda configuration, layer attachment, permissions
# 6. **Enterprise Standards:** Documentation, security, performance
# 7. **Type Safety:** Type annotations and function signatures
# 8. **Testing Framework:** Unit test readiness and mock compatibility
#
# **Test Results:**
# - ✅ PASS: Component meets all quality standards
# - ⚠️ WARN: Component has minor issues or recommendations
# - ❌ FAIL: Component has critical issues requiring fixes
#
# **Dependencies:**
# - boto3: AWS SDK for Lambda function inspection
# - ast: Python AST parsing for code analysis
# - pathlib: File system operations
# - typing: Type checking utilities
#
# =============================================================================

import ast
import concurrent.futures
import json
import os
import sys
import time
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Test configuration
PROJECT_PREFIX = "bos"
ENVIRONMENT = "dev"
LAMBDA_FUNCTIONS_PATH = Path("src")
COMMON_LAYER_PATH = Path("src/layers/common_utils/python")

# Expected Lambda functions with their categories
EXPECTED_LAMBDA_FUNCTIONS = {
    # Agent Functions
    "agent-persona": {
        "path": "src/agents/agent_persona/app.py",
        "category": "agent",
        "description": "User interaction and conversation management",
        "expected_triggers": ["sns", "api_gateway"],
    },
    "agent-director": {
        "path": "src/agents/agent_director/app.py",
        "category": "agent",
        "description": "AI-powered mission planning and coordination",
        "expected_triggers": ["sns", "api_gateway"],
    },
    "agent-coordinator": {
        "path": "src/agents/agent_coordinator/app.py",
        "category": "agent",
        "description": "Task orchestration and management",
        "expected_triggers": ["sns"],
    },
    "agent-elevator": {
        "path": "src/agents/agent_elevator/app.py",
        "category": "agent",
        "description": "Building elevator system integration",
        "expected_triggers": ["sns", "eventbridge", "api_gateway"],
    },
    "agent-psim": {
        "path": "src/agents/agent_psim/app.py",
        "category": "agent",
        "description": "Physical Security Information Management",
        "expected_triggers": ["sns", "api_gateway"],
    },
    "agent-health-check": {
        "path": "src/agents/agent_health_check/app.py",
        "category": "agent",
        "description": "System monitoring and health validation",
        "expected_triggers": ["api_gateway", "cloudwatch"],
    },
    # WebSocket Functions
    "websocket-default": {
        "path": "src/tools/websocket_default/app.py",
        "category": "websocket",
        "description": "Entry point for user messages",
        "expected_triggers": ["websocket"],
    },
    "websocket-broadcast": {
        "path": "src/tools/websocket_broadcast/app.py",
        "category": "websocket",
        "description": "Response delivery to users",
        "expected_triggers": ["sns"],
    },
    "websocket-connect": {
        "path": "src/tools/websocket_connect/app.py",
        "category": "websocket",
        "description": "Connection establishment and storage",
        "expected_triggers": ["websocket"],
    },
    "websocket-disconnect": {
        "path": "src/tools/websocket_disconnect/app.py",
        "category": "websocket",
        "description": "Connection cleanup and lifecycle management",
        "expected_triggers": ["websocket"],
    },
}

# Expected common layer components
EXPECTED_COMMON_LAYER_COMPONENTS = [
    "aws_clients.py",
    "utils.py",
    "models.py",
    "__init__.py",
]

# Enterprise standards requirements
ENTERPRISE_STANDARDS = {
    "min_docstring_length": 50,
    "required_imports": ["typing", "json"],
    "required_common_imports": ["aws_clients", "utils", "models"],
    "required_functions": ["handler"],
    "max_function_length": 100,  # lines
    "min_helper_functions": 2,
}


class ValidationResult:
    """Container for validation test results."""

    def __init__(
        self, test_name: str, status: str, message: str, details: Optional[Dict] = None
    ):
        self.test_name = test_name
        self.status = status  # PASS, WARN, FAIL
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()


class LambdaFunctionValidator:
    """Comprehensive Lambda function validation framework."""

    def __init__(self):
        """Initialize the validator with AWS clients and test configuration."""
        self.results: List[ValidationResult] = []
        self.aws_available = False

        # Initialize AWS clients with error handling
        try:
            self.lambda_client = boto3.client("lambda")
            self.sts_client = boto3.client("sts")
            self.account_id = self._aws_call_with_timeout(
                lambda: self.sts_client.get_caller_identity()["Account"],
                timeout_seconds=10,
                operation_name="get_caller_identity",
            )
            self.aws_available = True
            print("✅ AWS clients initialized successfully")
        except (ClientError, NoCredentialsError) as e:
            print(f"⚠️ AWS clients unavailable: {e}")
            print(
                "   Local code analysis will proceed, AWS integration tests will be skipped"
            )

        # Validate project structure
        if not LAMBDA_FUNCTIONS_PATH.exists():
            raise FileNotFoundError(
                f"Lambda functions directory not found: {LAMBDA_FUNCTIONS_PATH}"
            )

        if not COMMON_LAYER_PATH.exists():
            raise FileNotFoundError(
                f"Common layer directory not found: {COMMON_LAYER_PATH}"
            )

        print(f"🔍 Validating {len(EXPECTED_LAMBDA_FUNCTIONS)} Lambda functions...")
        print(f"📁 Project path: {LAMBDA_FUNCTIONS_PATH.absolute()}")
        print(f"🧰 Common layer path: {COMMON_LAYER_PATH.absolute()}")

    def _aws_call_with_timeout(
        self,
        aws_operation,
        timeout_seconds: int = 15,
        operation_name: str = "AWS operation",
    ):
        """Execute AWS API call with timeout protection."""

        def execute_operation():
            return aws_operation()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(execute_operation)
            try:
                return future.result(timeout=timeout_seconds)
            except concurrent.futures.TimeoutError:
                raise Exception(f"{operation_name} timed out after {timeout_seconds}s")

    def run_all_validations(
        self,
        include_functional_tests: bool = True,
        functional_test_timeout: int = 30,
        functional_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Run comprehensive validation suite for all Lambda functions.

        Args:
            include_functional_tests: Whether to run functional tests (default: True)
            functional_test_timeout: Timeout for functional tests in seconds (default: 30)
            functional_only: Whether to run only functional tests, skipping static analysis (default: False)

        Returns:
            dict: Complete validation results with summary
        """
        start_time = time.time()
        self.functional_test_timeout = functional_test_timeout

        print("\n" + "=" * 80)
        print("🧪 BUILDINGOS LAMBDA FUNCTIONS VALIDATION SUITE")
        print("=" * 80)

        if not include_functional_tests:
            print("⚠️ Functional tests disabled - running static analysis only")
        else:
            print(
                f"🚀 Functional tests enabled with {functional_test_timeout}s timeout"
            )

        if not functional_only:
            # Category 1: Code Quality Analysis
            print("\n📝 CATEGORY 1: CODE QUALITY ANALYSIS")
            print("-" * 50)
            self._validate_code_quality()

            # Category 2: Common Layer Integration
            print("\n🧰 CATEGORY 2: COMMON LAYER INTEGRATION")
            print("-" * 50)
            self._validate_common_layer_integration()

            # Category 3: Error Handling & Logging
            print("\n🛡️ CATEGORY 3: ERROR HANDLING & LOGGING")
            print("-" * 50)
            self._validate_error_handling()

            # Category 4: Function Architecture
            print("\n🏗️ CATEGORY 4: FUNCTION ARCHITECTURE")
            print("-" * 50)
            self._validate_function_architecture()

            # Category 5: AWS Integration (if available)
            if self.aws_available:
                print("\n☁️ CATEGORY 5: AWS INTEGRATION")
                print("-" * 50)
                self._validate_aws_integration()
            else:
                print("\n☁️ CATEGORY 5: AWS INTEGRATION - SKIPPED (AWS unavailable)")
                print("-" * 50)

            # Category 6: Enterprise Standards
            print("\n🏢 CATEGORY 6: ENTERPRISE STANDARDS")
            print("-" * 50)
            self._validate_enterprise_standards()

            # Category 7: Type Safety
            print("\n🔒 CATEGORY 7: TYPE SAFETY")
            print("-" * 50)
            self._validate_type_safety()

            # Category 8: Testing Framework Readiness
            print("\n🧪 CATEGORY 8: TESTING FRAMEWORK READINESS")
            print("-" * 50)
            self._validate_testing_readiness()
        else:
            print(
                "\n⚡ FUNCTIONAL-ONLY MODE: Skipping static analysis (Categories 1-8)"
            )
            print("-" * 50)

        # Category 9: Functional Testing (if AWS available and enabled)
        if self.aws_available and include_functional_tests:
            print("\n🚀 CATEGORY 9: FUNCTIONAL TESTING")
            print("-" * 50)
            self._validate_functional_testing(functional_test_timeout)
        elif not self.aws_available:
            print("\n🚀 CATEGORY 9: FUNCTIONAL TESTING - SKIPPED (AWS unavailable)")
            print("-" * 50)
        else:
            print("\n🚀 CATEGORY 9: FUNCTIONAL TESTING - SKIPPED (disabled)")
            print("-" * 50)

        # Generate summary
        end_time = time.time()
        summary = self._generate_summary(end_time - start_time)

        return {
            "summary": summary,
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp,
                }
                for r in self.results
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _validate_code_quality(self) -> None:
        """Validate code quality across all Lambda functions."""

        for func_name, func_info in EXPECTED_LAMBDA_FUNCTIONS.items():
            func_path = Path(func_info["path"])

            if not func_path.exists():
                self._add_result(
                    f"Code Quality - {func_name} - File Existence",
                    "FAIL",
                    f"Function file not found: {func_path}",
                )
                continue

            # Parse Python AST for code analysis
            try:
                with open(func_path, "r", encoding="utf-8") as f:
                    source_code = f.read()

                tree = ast.parse(source_code)

                # Check syntax (successful parsing means valid syntax)
                self._add_result(
                    f"Code Quality - {func_name} - Syntax",
                    "PASS",
                    "Python syntax is valid",
                )

                # Analyze imports
                self._validate_function_imports(func_name, tree)

                # Analyze functions
                self._validate_function_definitions(func_name, tree, source_code)

                # Check file header documentation
                self._validate_file_header(func_name, source_code)

            except SyntaxError as e:
                self._add_result(
                    f"Code Quality - {func_name} - Syntax", "FAIL", f"Syntax error: {e}"
                )
            except Exception as e:
                self._add_result(
                    f"Code Quality - {func_name} - Analysis",
                    "FAIL",
                    f"Code analysis failed: {e}",
                )

    def _validate_function_imports(self, func_name: str, tree: ast.AST) -> None:
        """Validate imports in a function."""
        imports = []
        from_imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    from_imports.append(node.module)

        # Check required imports
        has_typing = any("typing" in imp for imp in imports + from_imports)
        has_json = "json" in imports

        if has_typing and has_json:
            self._add_result(
                f"Code Quality - {func_name} - Required Imports",
                "PASS",
                "Required imports (typing, json) present",
            )
        else:
            missing = []
            if not has_typing:
                missing.append("typing")
            if not has_json:
                missing.append("json")

            self._add_result(
                f"Code Quality - {func_name} - Required Imports",
                "WARN",
                f"Missing recommended imports: {', '.join(missing)}",
            )

    def _validate_function_definitions(
        self, func_name: str, tree: ast.AST, source_code: str
    ) -> None:
        """Validate function definitions and structure."""
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]

        # Check for handler function
        handler_functions = [f for f in functions if f.name == "handler"]
        if handler_functions:
            handler = handler_functions[0]

            # Check handler function signature
            if len(handler.args.args) >= 2:
                self._add_result(
                    f"Code Quality - {func_name} - Handler Signature",
                    "PASS",
                    "Handler function has correct signature (event, context)",
                )
            else:
                self._add_result(
                    f"Code Quality - {func_name} - Handler Signature",
                    "FAIL",
                    "Handler function missing required parameters (event, context)",
                )

            # Check handler docstring
            docstring = ast.get_docstring(handler)
            if (
                docstring
                and len(docstring) >= ENTERPRISE_STANDARDS["min_docstring_length"]
            ):
                self._add_result(
                    f"Code Quality - {func_name} - Handler Documentation",
                    "PASS",
                    f"Handler has comprehensive docstring ({len(docstring)} chars)",
                )
            else:
                self._add_result(
                    f"Code Quality - {func_name} - Handler Documentation",
                    "WARN",
                    "Handler docstring is missing or too brief",
                )
        else:
            self._add_result(
                f"Code Quality - {func_name} - Handler Function",
                "FAIL",
                "Handler function not found",
            )

        # Check for helper functions (modularity)
        helper_functions = [
            f for f in functions if f.name != "handler" and not f.name.startswith("_")
        ]
        private_functions = [f for f in functions if f.name.startswith("_")]

        total_helpers = len(helper_functions) + len(private_functions)
        if total_helpers >= ENTERPRISE_STANDARDS["min_helper_functions"]:
            self._add_result(
                f"Code Quality - {func_name} - Modularity",
                "PASS",
                f"Good modularity with {total_helpers} helper functions",
            )
        else:
            self._add_result(
                f"Code Quality - {func_name} - Modularity",
                "WARN",
                f"Consider adding more helper functions for better modularity (found {total_helpers})",
            )

    def _validate_file_header(self, func_name: str, source_code: str) -> None:
        """Validate file header documentation."""
        lines = source_code.split("\n")

        # Look for comprehensive header (should start within first 10 lines)
        header_found = False
        for i, line in enumerate(lines[:10]):
            if "BuildingOS Platform" in line:
                header_found = True
                break

        if header_found:
            # Check for key sections in header
            header_text = "\n".join(
                lines[:50]
            )  # Check first 50 lines for header content
            required_sections = [
                "Purpose:",
                "Scope:",
                "Usage:",
                "Key Features:",
                "Dependencies:",
                "Integration:",
            ]
            missing_sections = [
                section for section in required_sections if section not in header_text
            ]

            if not missing_sections:
                self._add_result(
                    f"Code Quality - {func_name} - File Header",
                    "PASS",
                    "Comprehensive file header with all required sections",
                )
            else:
                self._add_result(
                    f"Code Quality - {func_name} - File Header",
                    "WARN",
                    f"File header missing sections: {', '.join(missing_sections)}",
                )
        else:
            self._add_result(
                f"Code Quality - {func_name} - File Header",
                "FAIL",
                "Missing comprehensive file header documentation",
            )

    def _validate_common_layer_integration(self) -> None:
        """Validate integration with common utilities layer."""

        # First, validate common layer structure
        self._validate_common_layer_structure()

        # Then validate each function's integration
        for func_name, func_info in EXPECTED_LAMBDA_FUNCTIONS.items():
            func_path = Path(func_info["path"])

            if not func_path.exists():
                continue

            try:
                with open(func_path, "r", encoding="utf-8") as f:
                    source_code = f.read()

                # Check for common layer imports
                common_imports = []
                for component in ENTERPRISE_STANDARDS["required_common_imports"]:
                    if f"from {component} import" in source_code:
                        common_imports.append(component)

                if len(common_imports) >= 2:  # At least aws_clients and utils
                    self._add_result(
                        f"Common Layer - {func_name} - Integration",
                        "PASS",
                        f"Properly integrates common layer components: {', '.join(common_imports)}",
                    )
                else:
                    self._add_result(
                        f"Common Layer - {func_name} - Integration",
                        "WARN",
                        f"Limited common layer integration: {', '.join(common_imports)}",
                    )

                # Check for direct boto3 usage (should be minimal)
                boto3_usage = source_code.count("boto3.client") + source_code.count(
                    "boto3.resource"
                )
                if boto3_usage == 0:
                    self._add_result(
                        f"Common Layer - {func_name} - Client Management",
                        "PASS",
                        "Uses common layer for AWS client management",
                    )
                elif boto3_usage <= 2:
                    self._add_result(
                        f"Common Layer - {func_name} - Client Management",
                        "WARN",
                        f"Some direct boto3 usage found ({boto3_usage} instances)",
                    )
                else:
                    self._add_result(
                        f"Common Layer - {func_name} - Client Management",
                        "FAIL",
                        f"Excessive direct boto3 usage ({boto3_usage} instances) - should use common layer",
                    )

            except Exception as e:
                self._add_result(
                    f"Common Layer - {func_name} - Analysis",
                    "FAIL",
                    f"Failed to analyze common layer integration: {e}",
                )

    def _validate_common_layer_structure(self) -> None:
        """Validate common layer structure and components."""

        missing_components = []
        for component in EXPECTED_COMMON_LAYER_COMPONENTS:
            component_path = COMMON_LAYER_PATH / component
            if not component_path.exists():
                missing_components.append(component)

        if not missing_components:
            self._add_result(
                "Common Layer - Structure",
                "PASS",
                f"All required components present: {', '.join(EXPECTED_COMMON_LAYER_COMPONENTS)}",
            )
        else:
            self._add_result(
                "Common Layer - Structure",
                "FAIL",
                f"Missing components: {', '.join(missing_components)}",
            )

        # Validate key components have content
        for component in ["aws_clients.py", "utils.py", "models.py"]:
            component_path = COMMON_LAYER_PATH / component
            if component_path.exists():
                try:
                    with open(component_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if len(content.strip()) > 100:  # Non-trivial content
                        self._add_result(
                            f"Common Layer - {component} Content",
                            "PASS",
                            f"Component has substantial implementation ({len(content)} chars)",
                        )
                    else:
                        self._add_result(
                            f"Common Layer - {component} Content",
                            "WARN",
                            "Component exists but has minimal content",
                        )
                except Exception as e:
                    self._add_result(
                        f"Common Layer - {component} Content",
                        "FAIL",
                        f"Failed to read component: {e}",
                    )

    def _validate_error_handling(self) -> None:
        """Validate error handling and logging patterns."""

        for func_name, func_info in EXPECTED_LAMBDA_FUNCTIONS.items():
            func_path = Path(func_info["path"])

            if not func_path.exists():
                continue

            try:
                with open(func_path, "r", encoding="utf-8") as f:
                    source_code = f.read()

                # Check for structured logging
                logging_patterns = [
                    "setup_logging",
                    "logger.info",
                    "logger.error",
                    "logger.warning",
                ]

                logging_score = sum(
                    1 for pattern in logging_patterns if pattern in source_code
                )

                if logging_score >= 3:
                    self._add_result(
                        f"Error Handling - {func_name} - Logging",
                        "PASS",
                        f"Comprehensive structured logging implemented ({logging_score}/4 patterns)",
                    )
                elif logging_score >= 2:
                    self._add_result(
                        f"Error Handling - {func_name} - Logging",
                        "WARN",
                        f"Basic logging implemented ({logging_score}/4 patterns)",
                    )
                else:
                    self._add_result(
                        f"Error Handling - {func_name} - Logging",
                        "FAIL",
                        f"Insufficient logging ({logging_score}/4 patterns)",
                    )

                # Check for correlation ID usage
                if (
                    "correlation_id" in source_code
                    and "generate_correlation_id" in source_code
                ):
                    self._add_result(
                        f"Error Handling - {func_name} - Correlation IDs",
                        "PASS",
                        "Implements correlation ID tracking",
                    )
                else:
                    self._add_result(
                        f"Error Handling - {func_name} - Correlation IDs",
                        "WARN",
                        "Missing correlation ID implementation",
                    )

                # Check for exception handling
                exception_patterns = [
                    "try:",
                    "except",
                    "Exception",
                    "exc_info=True",
                ]

                exception_score = sum(
                    1 for pattern in exception_patterns if pattern in source_code
                )

                if exception_score >= 3:
                    self._add_result(
                        f"Error Handling - {func_name} - Exception Handling",
                        "PASS",
                        "Comprehensive exception handling implemented",
                    )
                elif exception_score >= 2:
                    self._add_result(
                        f"Error Handling - {func_name} - Exception Handling",
                        "WARN",
                        "Basic exception handling implemented",
                    )
                else:
                    self._add_result(
                        f"Error Handling - {func_name} - Exception Handling",
                        "FAIL",
                        "Insufficient exception handling",
                    )

            except Exception as e:
                self._add_result(
                    f"Error Handling - {func_name} - Analysis",
                    "FAIL",
                    f"Failed to analyze error handling: {e}",
                )

    def _validate_function_architecture(self) -> None:
        """Validate function architecture and design patterns."""

        for func_name, func_info in EXPECTED_LAMBDA_FUNCTIONS.items():
            func_path = Path(func_info["path"])

            if not func_path.exists():
                continue

            try:
                with open(func_path, "r", encoding="utf-8") as f:
                    source_code = f.read()

                tree = ast.parse(source_code)

                # Check for event routing patterns
                routing_patterns = [
                    "httpMethod",
                    "Records",
                    "requestContext",
                    "event.get",
                ]

                routing_score = sum(
                    1 for pattern in routing_patterns if pattern in source_code
                )

                if routing_score >= 2:
                    self._add_result(
                        f"Architecture - {func_name} - Event Routing",
                        "PASS",
                        "Implements proper event routing patterns",
                    )
                else:
                    self._add_result(
                        f"Architecture - {func_name} - Event Routing",
                        "WARN",
                        "Limited event routing implementation",
                    )

                # Check for helper function organization
                functions = [
                    node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                ]
                helper_functions = [f for f in functions if f.name.startswith("_")]

                if len(helper_functions) >= 2:
                    self._add_result(
                        f"Architecture - {func_name} - Function Organization",
                        "PASS",
                        f"Good function organization with {len(helper_functions)} helper functions",
                    )
                else:
                    self._add_result(
                        f"Architecture - {func_name} - Function Organization",
                        "WARN",
                        "Consider more helper functions for better organization",
                    )

                # Check for response standardization
                response_patterns = [
                    "statusCode",
                    "headers",
                    "body",
                    "create_error_response",
                    "create_success_response",
                ]

                response_score = sum(
                    1 for pattern in response_patterns if pattern in source_code
                )

                if response_score >= 3:
                    self._add_result(
                        f"Architecture - {func_name} - Response Standards",
                        "PASS",
                        "Implements standardized response patterns",
                    )
                else:
                    self._add_result(
                        f"Architecture - {func_name} - Response Standards",
                        "WARN",
                        "Limited response standardization",
                    )

            except Exception as e:
                self._add_result(
                    f"Architecture - {func_name} - Analysis",
                    "FAIL",
                    f"Failed to analyze function architecture: {e}",
                )

    def _validate_aws_integration(self) -> None:
        """Validate AWS integration and Lambda configuration."""

        for func_name, func_info in EXPECTED_LAMBDA_FUNCTIONS.items():
            aws_function_name = f"{PROJECT_PREFIX}-{ENVIRONMENT}-{func_name}"

            try:
                # Get Lambda function configuration (with timeout)
                response = self._aws_call_with_timeout(
                    lambda: self.lambda_client.get_function(
                        FunctionName=aws_function_name
                    ),
                    timeout_seconds=10,
                    operation_name=f"get_function({aws_function_name})",
                )
                config = response["Configuration"]

                # Check runtime
                if config["Runtime"].startswith("python3"):
                    self._add_result(
                        f"AWS Integration - {func_name} - Runtime",
                        "PASS",
                        f"Using {config['Runtime']} runtime",
                    )
                else:
                    self._add_result(
                        f"AWS Integration - {func_name} - Runtime",
                        "WARN",
                        f"Unexpected runtime: {config['Runtime']}",
                    )

                # Check layer attachment
                layers = config.get("Layers", [])
                common_layer_attached = any(
                    "common-utils" in layer["Arn"] for layer in layers
                )

                if common_layer_attached:
                    self._add_result(
                        f"AWS Integration - {func_name} - Layer Attachment",
                        "PASS",
                        "Common utilities layer attached",
                    )
                else:
                    self._add_result(
                        f"AWS Integration - {func_name} - Layer Attachment",
                        "FAIL",
                        "Common utilities layer not attached",
                    )

                # Check memory and timeout configuration
                memory_mb = config["MemorySize"]
                timeout_sec = config["Timeout"]

                if 128 <= memory_mb <= 1024 and 10 <= timeout_sec <= 300:
                    self._add_result(
                        f"AWS Integration - {func_name} - Resource Configuration",
                        "PASS",
                        f"Appropriate resources: {memory_mb}MB, {timeout_sec}s timeout",
                    )
                else:
                    self._add_result(
                        f"AWS Integration - {func_name} - Resource Configuration",
                        "WARN",
                        f"Review resource settings: {memory_mb}MB, {timeout_sec}s timeout",
                    )

                # Check environment variables
                env_vars = config.get("Environment", {}).get("Variables", {})
                if env_vars:
                    self._add_result(
                        f"AWS Integration - {func_name} - Environment Variables",
                        "PASS",
                        f"Has {len(env_vars)} environment variables configured",
                    )
                else:
                    self._add_result(
                        f"AWS Integration - {func_name} - Environment Variables",
                        "WARN",
                        "No environment variables configured",
                    )

            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    self._add_result(
                        f"AWS Integration - {func_name} - Function Existence",
                        "FAIL",
                        f"Lambda function not found: {aws_function_name}",
                    )
                else:
                    self._add_result(
                        f"AWS Integration - {func_name} - Configuration",
                        "FAIL",
                        f"Failed to get function configuration: {e}",
                    )
            except Exception as e:
                self._add_result(
                    f"AWS Integration - {func_name} - Analysis",
                    "FAIL",
                    f"Failed to analyze AWS integration: {e}",
                )

    def _validate_enterprise_standards(self) -> None:
        """Validate enterprise standards compliance."""

        # Overall standards validation
        total_functions = len(EXPECTED_LAMBDA_FUNCTIONS)
        functions_with_headers = 0
        functions_with_typing = 0
        functions_with_logging = 0

        for func_name, func_info in EXPECTED_LAMBDA_FUNCTIONS.items():
            func_path = Path(func_info["path"])

            if not func_path.exists():
                continue

            try:
                with open(func_path, "r", encoding="utf-8") as f:
                    source_code = f.read()

                # Check for comprehensive header
                if "BuildingOS Platform" in source_code and "Purpose:" in source_code:
                    functions_with_headers += 1

                # Check for typing usage
                if "from typing import" in source_code and ": Dict[" in source_code:
                    functions_with_typing += 1

                # Check for structured logging
                if "setup_logging" in source_code and "logger." in source_code:
                    functions_with_logging += 1

            except Exception:
                continue

        # Calculate compliance percentages
        header_compliance = (functions_with_headers / total_functions) * 100
        typing_compliance = (functions_with_typing / total_functions) * 100
        logging_compliance = (functions_with_logging / total_functions) * 100

        # Overall enterprise standards score
        overall_compliance = (
            header_compliance + typing_compliance + logging_compliance
        ) / 3

        if overall_compliance >= 90:
            self._add_result(
                "Enterprise Standards - Overall Compliance",
                "PASS",
                f"Excellent compliance: {overall_compliance:.1f}% average across standards",
            )
        elif overall_compliance >= 75:
            self._add_result(
                "Enterprise Standards - Overall Compliance",
                "WARN",
                f"Good compliance: {overall_compliance:.1f}% average across standards",
            )
        else:
            self._add_result(
                "Enterprise Standards - Overall Compliance",
                "FAIL",
                f"Poor compliance: {overall_compliance:.1f}% average across standards",
            )

        # Detailed compliance reporting
        self._add_result(
            "Enterprise Standards - Documentation Headers",
            (
                "PASS"
                if header_compliance >= 90
                else "WARN" if header_compliance >= 75 else "FAIL"
            ),
            f"{header_compliance:.1f}% functions have comprehensive headers ({functions_with_headers}/{total_functions})",
        )

        self._add_result(
            "Enterprise Standards - Type Annotations",
            (
                "PASS"
                if typing_compliance >= 90
                else "WARN" if typing_compliance >= 75 else "FAIL"
            ),
            f"{typing_compliance:.1f}% functions use type annotations ({functions_with_typing}/{total_functions})",
        )

        self._add_result(
            "Enterprise Standards - Structured Logging",
            (
                "PASS"
                if logging_compliance >= 90
                else "WARN" if logging_compliance >= 75 else "FAIL"
            ),
            f"{logging_compliance:.1f}% functions use structured logging ({functions_with_logging}/{total_functions})",
        )

    def _validate_type_safety(self) -> None:
        """Validate type safety and annotations."""

        for func_name, func_info in EXPECTED_LAMBDA_FUNCTIONS.items():
            func_path = Path(func_info["path"])

            if not func_path.exists():
                continue

            try:
                with open(func_path, "r", encoding="utf-8") as f:
                    source_code = f.read()

                tree = ast.parse(source_code)

                # Analyze function annotations
                functions = [
                    node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                ]

                annotated_functions = 0
                total_functions = len(functions)

                for func in functions:
                    # Check if function has parameter annotations
                    has_param_annotations = any(
                        arg.annotation for arg in func.args.args
                    )
                    has_return_annotation = func.returns is not None

                    if has_param_annotations and has_return_annotation:
                        annotated_functions += 1

                if total_functions > 0:
                    annotation_percentage = (
                        annotated_functions / total_functions
                    ) * 100

                    if annotation_percentage >= 80:
                        self._add_result(
                            f"Type Safety - {func_name} - Function Annotations",
                            "PASS",
                            f"{annotation_percentage:.1f}% functions have type annotations ({annotated_functions}/{total_functions})",
                        )
                    elif annotation_percentage >= 50:
                        self._add_result(
                            f"Type Safety - {func_name} - Function Annotations",
                            "WARN",
                            f"{annotation_percentage:.1f}% functions have type annotations ({annotated_functions}/{total_functions})",
                        )
                    else:
                        self._add_result(
                            f"Type Safety - {func_name} - Function Annotations",
                            "FAIL",
                            f"{annotation_percentage:.1f}% functions have type annotations ({annotated_functions}/{total_functions})",
                        )

                # Check for type imports
                type_imports = ["Dict", "List", "Any", "Optional", "Tuple", "Union"]

                found_type_imports = sum(
                    1 for type_import in type_imports if type_import in source_code
                )

                if found_type_imports >= 3:
                    self._add_result(
                        f"Type Safety - {func_name} - Type Imports",
                        "PASS",
                        f"Uses diverse type annotations ({found_type_imports}/6 types)",
                    )
                elif found_type_imports >= 1:
                    self._add_result(
                        f"Type Safety - {func_name} - Type Imports",
                        "WARN",
                        f"Limited type annotations ({found_type_imports}/6 types)",
                    )
                else:
                    self._add_result(
                        f"Type Safety - {func_name} - Type Imports",
                        "FAIL",
                        "No type annotations found",
                    )

            except Exception as e:
                self._add_result(
                    f"Type Safety - {func_name} - Analysis",
                    "FAIL",
                    f"Failed to analyze type safety: {e}",
                )

    def _validate_testing_readiness(self) -> None:
        """Validate readiness for unit testing framework."""

        for func_name, func_info in EXPECTED_LAMBDA_FUNCTIONS.items():
            func_path = Path(func_info["path"])

            if not func_path.exists():
                continue

            try:
                with open(func_path, "r", encoding="utf-8") as f:
                    source_code = f.read()

                # Check for testable patterns
                testable_patterns = [
                    "def _",  # Private helper functions
                    "return {",  # Structured returns
                    "Dict[str, Any]",  # Type annotations
                    "correlation_id",  # Tracing
                ]

                testability_score = sum(
                    1 for pattern in testable_patterns if pattern in source_code
                )

                if testability_score >= 3:
                    self._add_result(
                        f"Testing Readiness - {func_name} - Testability",
                        "PASS",
                        f"High testability score ({testability_score}/4 patterns)",
                    )
                elif testability_score >= 2:
                    self._add_result(
                        f"Testing Readiness - {func_name} - Testability",
                        "WARN",
                        f"Moderate testability score ({testability_score}/4 patterns)",
                    )
                else:
                    self._add_result(
                        f"Testing Readiness - {func_name} - Testability",
                        "FAIL",
                        f"Low testability score ({testability_score}/4 patterns)",
                    )

                # Check for dependency injection readiness
                di_patterns = [
                    "get_",  # Client getters
                    "aws_clients",  # Client abstraction
                    "correlation_id",  # Testable tracing
                ]

                di_score = sum(1 for pattern in di_patterns if pattern in source_code)

                if di_score >= 2:
                    self._add_result(
                        f"Testing Readiness - {func_name} - Dependency Injection",
                        "PASS",
                        "Ready for dependency injection in tests",
                    )
                else:
                    self._add_result(
                        f"Testing Readiness - {func_name} - Dependency Injection",
                        "WARN",
                        "Limited dependency injection readiness",
                    )

            except Exception as e:
                self._add_result(
                    f"Testing Readiness - {func_name} - Analysis",
                    "FAIL",
                    f"Failed to analyze testing readiness: {e}",
                )

    def _validate_functional_testing(self, timeout_seconds: int = 15) -> None:
        """Validate Lambda functions through actual invocation with test payloads."""

        # Test payloads for different function types
        test_payloads = self._get_test_payloads()

        for func_name, func_info in EXPECTED_LAMBDA_FUNCTIONS.items():
            aws_function_name = f"{PROJECT_PREFIX}-{ENVIRONMENT}-{func_name}"

            # Check if function timeout is longer than our test timeout
            try:
                func_config = self._aws_call_with_timeout(
                    lambda: self.lambda_client.get_function(
                        FunctionName=aws_function_name
                    ),
                    timeout_seconds=5,
                    operation_name=f"get_function_config({aws_function_name})",
                )
                lambda_timeout = func_config["Configuration"]["Timeout"]

                if lambda_timeout > timeout_seconds + 5:  # Add 5s buffer
                    print(
                        f"  ⏭️  Skipping {func_name}: Lambda timeout ({lambda_timeout}s) > test timeout ({timeout_seconds}s)"
                    )
                    self._add_result(
                        f"Functional Test - {func_name} - Timeout Check",
                        "WARN",
                        f"Skipped: Lambda timeout ({lambda_timeout}s) exceeds test timeout ({timeout_seconds}s)",
                    )
                    continue

            except Exception as config_error:
                print(f"  ⚠️  Could not check timeout for {func_name}: {config_error}")

            print(f"  🔍 Testing function: {func_name} ({aws_function_name})")

            try:
                # Get appropriate test payload for this function category
                category = func_info["category"]
                test_payload = test_payloads.get(category, {}).get(func_name)

                if not test_payload:
                    self._add_result(
                        f"Functional Test - {func_name} - Test Payload",
                        "WARN",
                        f"No test payload defined for {func_name}",
                    )
                    continue

                # Invoke Lambda function with test payload (with timeout)
                start_time = time.time()
                try:
                    # Invoke Lambda function with timeout protection
                    response = self._aws_call_with_timeout(
                        lambda: self.lambda_client.invoke(
                            FunctionName=aws_function_name,
                            InvocationType="RequestResponse",
                            Payload=json.dumps(test_payload),
                        ),
                        timeout_seconds=timeout_seconds,
                        operation_name=f"invoke({aws_function_name})",
                    )
                    end_time = time.time()

                except Exception as invoke_error:
                    end_time = time.time()
                    execution_time_ms = round((end_time - start_time) * 1000, 2)
                    self._add_result(
                        f"Functional Test - {func_name} - Execution",
                        "FAIL",
                        f"Function invocation failed after {execution_time_ms}ms: {str(invoke_error)}",
                    )
                    continue

                # Parse response (with timeout protection)
                try:
                    payload_data = self._aws_call_with_timeout(
                        lambda: response["Payload"].read(),
                        timeout_seconds=2,
                        operation_name=f"read_payload({aws_function_name})",
                    )
                    response_payload = json.loads(payload_data)
                    status_code = response.get("StatusCode", 0)
                except Exception as payload_error:
                    end_time = time.time()
                    execution_time_ms = round((end_time - start_time) * 1000, 2)
                    self._add_result(
                        f"Functional Test - {func_name} - Response",
                        "FAIL",
                        f"Failed to read response payload after {execution_time_ms}ms: {str(payload_error)}",
                    )
                    continue

                # Validate execution success
                if status_code == 200:
                    execution_time_ms = round((end_time - start_time) * 1000, 2)

                    # Check for function errors
                    if "errorMessage" in response_payload:
                        self._add_result(
                            f"Functional Test - {func_name} - Execution",
                            "FAIL",
                            f"Function returned error: {response_payload['errorMessage']}",
                            {
                                "execution_time_ms": execution_time_ms,
                                "payload": test_payload,
                            },
                        )
                    else:
                        # Validate response structure
                        response_valid = self._validate_response_structure(
                            func_name, func_info, response_payload
                        )

                        if response_valid:
                            self._add_result(
                                f"Functional Test - {func_name} - Execution",
                                "PASS",
                                f"Function executed successfully in {execution_time_ms}ms",
                                {
                                    "execution_time_ms": execution_time_ms,
                                    "response_keys": (
                                        list(response_payload.keys())
                                        if isinstance(response_payload, dict)
                                        else "non-dict"
                                    ),
                                },
                            )
                        else:
                            self._add_result(
                                f"Functional Test - {func_name} - Execution",
                                "WARN",
                                f"Function executed but response structure unexpected ({execution_time_ms}ms)",
                                {
                                    "execution_time_ms": execution_time_ms,
                                    "response": str(response_payload)[:200],
                                },
                            )
                else:
                    self._add_result(
                        f"Functional Test - {func_name} - Execution",
                        "FAIL",
                        f"Lambda invocation failed with status code: {status_code}",
                    )

                # Performance validation (based on timeout setting)
                execution_time_ms = round((end_time - start_time) * 1000, 2)
                timeout_ms = timeout_seconds * 1000

                if execution_time_ms < timeout_ms * 0.2:  # Under 20% of timeout
                    self._add_result(
                        f"Functional Test - {func_name} - Performance",
                        "PASS",
                        f"Excellent performance: {execution_time_ms}ms execution time",
                    )
                elif execution_time_ms < timeout_ms * 0.5:  # Under 50% of timeout
                    self._add_result(
                        f"Functional Test - {func_name} - Performance",
                        "PASS",
                        f"Good performance: {execution_time_ms}ms execution time",
                    )
                elif execution_time_ms < timeout_ms * 0.8:  # Under 80% of timeout
                    self._add_result(
                        f"Functional Test - {func_name} - Performance",
                        "WARN",
                        f"Acceptable performance: {execution_time_ms}ms execution time",
                    )
                else:
                    self._add_result(
                        f"Functional Test - {func_name} - Performance",
                        "FAIL",
                        f"Poor performance: {execution_time_ms}ms execution time (near timeout)",
                    )

            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    self._add_result(
                        f"Functional Test - {func_name} - Availability",
                        "FAIL",
                        f"Lambda function not found: {aws_function_name}",
                    )
                else:
                    self._add_result(
                        f"Functional Test - {func_name} - Invocation",
                        "FAIL",
                        f"Failed to invoke function: {e}",
                    )
            except Exception as e:
                self._add_result(
                    f"Functional Test - {func_name} - Analysis",
                    "FAIL",
                    f"Failed to analyze functional test: {e}",
                )

    def _get_test_payloads(self) -> Dict[str, Dict[str, Any]]:
        """Generate test payloads for different Lambda function categories."""

        return {
            "agent": {
                "agent-persona": {
                    "httpMethod": "GET",
                    "path": "/health",
                    "headers": {"Content-Type": "application/json"},
                    "queryStringParameters": None,
                    "body": None,
                },
                "agent-director": {
                    "httpMethod": "GET",
                    "path": "/health",
                    "headers": {"Content-Type": "application/json"},
                    "queryStringParameters": None,
                    "body": None,
                },
                "agent-coordinator": {
                    "Records": [
                        {
                            "EventSource": "aws:sns",
                            "Sns": {
                                "TopicArn": "arn:aws:sns:us-east-1:123456789012:test-topic",
                                "Message": json.dumps(
                                    {
                                        "agent": "agent_coordinator",
                                        "mission_id": "test-mission-123",
                                        "task_id": "test-task-456",
                                        "action": "health_check",
                                        "parameters": {},
                                    }
                                ),
                                "MessageId": "test-message-id",
                            },
                        }
                    ]
                },
                "agent-elevator": {
                    "Records": [
                        {
                            "EventSource": "aws:sns",
                            "Sns": {
                                "TopicArn": "arn:aws:sns:us-east-1:123456789012:test-topic",
                                "Message": json.dumps(
                                    {
                                        "agent": "agent_elevator",
                                        "mission_id": "test-mission-123",
                                        "task_id": "test-task-456",
                                        "action": "health_check",
                                        "parameters": {},
                                    }
                                ),
                                "MessageId": "test-message-id",
                            },
                        }
                    ]
                },
                "agent-psim": {
                    "Records": [
                        {
                            "EventSource": "aws:sns",
                            "Sns": {
                                "TopicArn": "arn:aws:sns:us-east-1:123456789012:test-topic",
                                "Message": json.dumps(
                                    {
                                        "agent": "agent_psim",
                                        "mission_id": "test-mission-123",
                                        "task_id": "test-task-456",
                                        "action": "health_check",
                                        "parameters": {},
                                    }
                                ),
                                "MessageId": "test-message-id",
                            },
                        }
                    ]
                },
                "agent-health-check": {
                    "httpMethod": "GET",
                    "path": "/health",
                    "headers": {"Content-Type": "application/json"},
                    "queryStringParameters": None,
                    "body": None,
                },
            },
            "websocket": {
                "websocket-default": {
                    "requestContext": {
                        "connectionId": "test-connection-123",
                        "routeKey": "$default",
                        "eventType": "MESSAGE",
                    },
                    "body": json.dumps({"message": "Hello, test message"}),
                },
                "websocket-broadcast": {
                    "Records": [
                        {
                            "EventSource": "aws:sns",
                            "Sns": {
                                "TopicArn": "arn:aws:sns:us-east-1:123456789012:test-topic",
                                "Message": json.dumps(
                                    {
                                        "type": "broadcast",
                                        "connectionId": "test-connection-123",
                                        "message": "Test broadcast message",
                                    }
                                ),
                                "MessageId": "test-message-id",
                            },
                        }
                    ]
                },
                "websocket-connect": {
                    "requestContext": {
                        "connectionId": "test-connection-123",
                        "routeKey": "$connect",
                        "eventType": "CONNECT",
                    },
                    "headers": {
                        "User-Agent": "Test-Agent/1.0",
                        "Origin": "https://test.example.com",
                    },
                },
                "websocket-disconnect": {
                    "requestContext": {
                        "connectionId": "test-connection-123",
                        "routeKey": "$disconnect",
                        "eventType": "DISCONNECT",
                    }
                },
            },
        }

    def _validate_response_structure(
        self, func_name: str, func_info: Dict[str, Any], response: Any
    ) -> bool:
        """Validate the structure of Lambda function response."""

        category = func_info["category"]
        expected_triggers = func_info.get("expected_triggers", [])

        # For HTTP/API Gateway responses
        if "api_gateway" in expected_triggers:
            if isinstance(response, dict):
                # Should have statusCode and body for API Gateway
                has_status_code = "statusCode" in response
                has_body = "body" in response

                if has_status_code and has_body:
                    return True
                else:
                    self._add_result(
                        f"Functional Test - {func_name} - Response Structure",
                        "WARN",
                        f"API Gateway response missing required fields (statusCode: {has_status_code}, body: {has_body})",
                    )
                    return False

        # For SNS/Event responses
        elif "sns" in expected_triggers or "websocket" in expected_triggers:
            if isinstance(response, dict):
                # Should be a structured response
                return True
            else:
                self._add_result(
                    f"Functional Test - {func_name} - Response Structure",
                    "WARN",
                    f"SNS/WebSocket response should be a dictionary, got {type(response).__name__}",
                )
                return False

        # Default case - accept any structured response
        return isinstance(response, dict)

    def _add_result(
        self, test_name: str, status: str, message: str, details: Optional[Dict] = None
    ) -> None:
        """Add a validation result."""
        result = ValidationResult(test_name, status, message, details)
        self.results.append(result)

        # Print result with appropriate emoji
        emoji = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
        print(f"  {emoji} {test_name}: {message}")

    def _generate_summary(self, execution_time: float) -> Dict[str, Any]:
        """Generate validation summary."""

        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        warned_tests = len([r for r in self.results if r.status == "WARN"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "=" * 80)
        print("📊 VALIDATION SUMMARY")
        print("=" * 80)
        print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
        print(f"🧪 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"⚠️  Warnings: {warned_tests} ({warned_tests/total_tests*100:.1f}%)")
        print(f"❌ Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        print(f"🎯 Success Rate: {success_rate:.1f}%")

        # Overall status
        if failed_tests == 0:
            overall_status = (
                "PASS" if warned_tests <= total_tests * 0.2 else "PASS_WITH_WARNINGS"
            )
            print(
                f"🏆 Overall Status: {'EXCELLENT' if overall_status == 'PASS' else 'GOOD'}"
            )
        else:
            overall_status = "FAIL"
            print(f"💥 Overall Status: NEEDS_ATTENTION")

        print("=" * 80)

        return {
            "overall_status": overall_status,
            "execution_time_seconds": execution_time,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "warned_tests": warned_tests,
            "failed_tests": failed_tests,
            "success_rate_percentage": success_rate,
            "functions_analyzed": len(EXPECTED_LAMBDA_FUNCTIONS),
            "aws_integration_tested": self.aws_available,
        }


def main():
    """Main execution function."""
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Validate BuildingOS Lambda Functions")
    parser.add_argument(
        "--no-functional",
        action="store_true",
        help="Skip functional tests (faster execution)",
    )
    parser.add_argument(
        "--functional-only",
        action="store_true",
        help="Run only functional tests (skip static analysis)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Timeout for functional tests in seconds (default: 15)",
    )
    args = parser.parse_args()

    try:
        # Initialize validator
        validator = LambdaFunctionValidator()

        # Run all validations
        include_functional = not args.no_functional
        results = validator.run_all_validations(
            include_functional_tests=include_functional,
            functional_test_timeout=args.timeout,
            functional_only=args.functional_only,
        )

        # Save results to file
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        results_file = f"lambda-functions-validation-{timestamp}.json"

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Results saved to: {results_file}")

        # Exit with appropriate code
        if results["summary"]["overall_status"] in ["PASS", "PASS_WITH_WARNINGS"]:
            print("🎉 Lambda Functions Validation: SUCCESS")
            sys.exit(0)
        else:
            print("💥 Lambda Functions Validation: FAILED")
            sys.exit(1)

    except Exception as e:
        print(f"💥 Critical error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
