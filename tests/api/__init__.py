# API Test Package Initialization
"""
BuildingOS API Testing Suite

This package provides comprehensive testing capabilities for the BuildingOS API,
including functional tests, performance testing, load testing, and detailed reporting.

Usage:
    # Run all tests
    python run_tests.py all

    # Run only endpoint tests
    python run_tests.py endpoints

    # Run performance tests
    python run_tests.py performance

    # Quick smoke tests
    python run_tests.py smoke

Features:
- Comprehensive endpoint testing
- Performance and load testing
- Rich console output with colors and progress bars
- HTML and JSON reporting
- Retry logic for flaky network conditions
- CORS headers validation
- Error handling testing
- Boundary condition testing
"""

__version__ = "1.0.0"
__author__ = "BuildingOS Team"

from .client import APITestClient, client
from .config import APIConfig, TestPayloads, ResponseValidator, config
from .utils import TestDataGenerator, APITestReporter, EndpointMonitor

__all__ = [
    "APITestClient",
    "client",
    "APIConfig",
    "TestPayloads",
    "ResponseValidator",
    "config",
    "TestDataGenerator",
    "APITestReporter",
    "EndpointMonitor",
]
