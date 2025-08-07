# API Test Configuration
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json


@dataclass
class APIConfig:
    """Configuration for API tests"""

    base_url: str = "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com"
    timeout: int = 30
    retry_count: int = 3
    environment: str = "dev"

    # Test data
    test_user_id: str = "api-test-user"
    test_mission_prefix: str = "test-mission"

    @classmethod
    def from_env(cls) -> "APIConfig":
        """Load configuration from environment variables"""
        return cls(
            base_url=os.getenv("API_BASE_URL", cls.base_url),
            timeout=int(os.getenv("API_TIMEOUT", cls.timeout)),
            retry_count=int(os.getenv("API_RETRY_COUNT", cls.retry_count)),
            environment=os.getenv("ENVIRONMENT", cls.environment),
            test_user_id=os.getenv("TEST_USER_ID", cls.test_user_id),
        )


class TestPayloads:
    """Standard test payloads for different endpoints"""

    @staticmethod
    def persona_message(user_id: str = None, message: str = None) -> Dict[str, Any]:
        return {
            "user_id": user_id or "api-test-user",
            "message": message or "Test message from Python API tests",
        }

    @staticmethod
    def elevator_call(mission_id: str = None, floor: int = 3) -> Dict[str, Any]:
        return {
            "mission_id": mission_id or "test-mission-123",
            "action": "call_elevator",
            "parameters": {"floor": floor, "direction": "up"},
        }

    @staticmethod
    def psim_search(query: str = None) -> Dict[str, Any]:
        return {
            "action": "search_person",
            "query": query or "test-user",
            "parameters": {"department": "IT", "active_only": True},
        }


class ResponseValidator:
    """Validate API responses against expected schemas"""

    @staticmethod
    def validate_health_response(response: Dict[str, Any]) -> bool:
        required_fields = ["status", "message"]
        return all(field in response for field in required_fields)

    @staticmethod
    def validate_persona_response(response: Dict[str, Any]) -> bool:
        # Should have either message+session_id or error
        has_success = "message" in response and "session_id" in response
        has_error = "error" in response
        return has_success or has_error

    @staticmethod
    def validate_director_response(response: Dict[str, Any]) -> bool:
        # Should have status and either mission_id or error
        has_status = "status" in response
        has_success = "mission_id" in response and "message" in response
        has_error = "error" in response
        return has_status and (has_success or has_error)

    @staticmethod
    def validate_coordinator_response(response: Dict[str, Any]) -> bool:
        required_fields = ["mission_id", "status", "timestamp"]
        return all(field in response for field in required_fields)


# Global configuration instance
config = APIConfig.from_env()
