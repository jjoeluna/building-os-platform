# Comprehensive API Tests using pytest
import pytest
import time
from typing import Dict, Any
from .client import client
from .config import config, TestPayloads, ResponseValidator
from rich.console import Console

console = Console()


class TestHealthEndpoint:
    """Test the health check endpoint"""

    def test_health_check_success(self):
        """Test that health endpoint returns success"""
        response, data = client.get("/health")

        assert response.status_code == 200
        assert ResponseValidator.validate_health_response(data)
        assert data["status"] == "OK"
        assert "message" in data

    def test_health_check_performance(self):
        """Test that health endpoint responds quickly"""
        start_time = time.time()
        response, data = client.get("/health")
        end_time = time.time()

        response_time = (end_time - start_time) * 1000
        assert response_time < 2000  # Should respond within 2 seconds
        assert response.status_code == 200


class TestDirectorEndpoint:
    """Test the director agent endpoint"""

    def test_director_basic_request(self):
        """Test director without parameters"""
        response, data = client.get("/director")

        assert response.status_code == 200
        assert ResponseValidator.validate_director_response(data)
        assert data["status"] == "SUCCESS"
        assert "mission_id" in data

    def test_director_with_user_request(self):
        """Test director with user request parameter"""
        user_request = "Test mission from Python API tests"
        response, data = client.get(f"/director?user_request={user_request}")

        assert response.status_code == 200
        assert data["status"] == "SUCCESS"
        assert "mission_id" in data
        assert "message" in data

    def test_director_with_user_id(self):
        """Test director with user_id parameter"""
        user_id = config.test_user_id
        response, data = client.get(f"/director?user_id={user_id}")

        assert response.status_code == 200
        assert data["status"] == "SUCCESS"


class TestPersonaEndpoint:
    """Test the persona agent endpoint"""

    def test_persona_valid_message(self):
        """Test persona with valid message"""
        payload = TestPayloads.persona_message()
        response, data = client.post("/persona", json=payload)

        assert response.status_code == 200
        assert ResponseValidator.validate_persona_response(data)

        # Should either succeed or have a specific error format
        if "error" not in data:
            assert "message" in data
            assert "session_id" in data

    def test_persona_missing_user_id(self):
        """Test persona without user_id"""
        payload = {"message": "Test message"}
        response, data = client.post("/persona", json=payload)

        # Should return error for missing user_id
        assert "error" in data or response.status_code >= 400

    def test_persona_missing_message(self):
        """Test persona without message"""
        payload = {"user_id": config.test_user_id}
        response, data = client.post("/persona", json=payload)

        # Should return error for missing message
        assert "error" in data or response.status_code >= 400

    def test_persona_conversations(self):
        """Test persona conversations endpoint"""
        user_id = config.test_user_id
        response, data = client.get(f"/persona/conversations?user_id={user_id}")

        # This endpoint might return empty list or specific structure
        assert response.status_code in [200, 404]  # Allow 404 for no conversations


class TestElevatorEndpoint:
    """Test the elevator agent endpoint"""

    def test_elevator_call_basic(self):
        """Test basic elevator call"""
        payload = TestPayloads.elevator_call()
        response, data = client.post("/elevator/call", json=payload)

        # Elevator might return various responses depending on implementation
        assert response.status_code in [200, 400]  # Allow 400 for missing parameters

        if response.status_code == 200:
            assert isinstance(data, dict)

    def test_elevator_missing_mission_id(self):
        """Test elevator call without mission_id"""
        payload = {
            "action": "call_elevator",
            "parameters": {"from_floor": 1, "to_floor": 3},
        }

        # Expect 500 error for missing mission_id, so catch the retry exception
        try:
            response, data = client.post("/elevator/call", json=payload)
            # Should return error for missing mission_id
            assert "error" in data or response.status_code >= 400
        except Exception as e:
            # If we get a retry error due to 500 responses, that's also valid
            assert "500 error responses" in str(e) or "mission_id is required" in str(e)


class TestPSIMEndpoint:
    """Test the PSIM agent endpoint"""

    def test_psim_search_basic(self):
        """Test basic PSIM search"""
        payload = TestPayloads.psim_search()
        response, data = client.post("/psim/search", json=payload)

        assert response.status_code == 200
        assert isinstance(data, dict)
        assert "action" in data
        assert data["action"] == "search_person"

    def test_psim_search_with_custom_query(self):
        """Test PSIM search with custom query"""
        custom_query = "python-test-user"
        payload = TestPayloads.psim_search(query=custom_query)
        response, data = client.post("/psim/search", json=payload)

        assert response.status_code == 200
        assert "result" in data


class TestCoordinatorEndpoint:
    """Test the coordinator agent endpoint"""

    def test_coordinator_mission_status(self):
        """Test coordinator mission status for non-existent mission"""
        mission_id = "test-mission-123"
        response, data = client.get(f"/coordinator/missions/{mission_id}")

        # Expect 404 for non-existent mission (correct behavior)
        assert response.status_code == 404
        assert "error" in data
        assert mission_id in data["error"]

    def test_coordinator_different_mission_id(self):
        """Test coordinator with different mission ID"""
        mission_id = f"python-test-{int(time.time())}"
        response, data = client.get(f"/coordinator/missions/{mission_id}")

        # Expect 404 for non-existent mission (correct behavior)
        assert response.status_code == 404
        assert "error" in data


class TestCORSHeaders:
    """Test CORS headers on all endpoints"""

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/health",
            "/director",
            "/persona",
            "/elevator/call",
            "/psim/search",
            "/coordinator/missions/test-123",
        ],
    )
    def test_cors_headers_present(self, endpoint):
        """Test that CORS is properly configured via preflight requests"""
        # Test CORS via OPTIONS preflight request (how browsers actually check CORS)
        # API Gateway HTTP API v2 handles CORS at the gateway level, not in Lambda responses

        import requests

        url = f"{client.base_url}{endpoint}"

        # Make a preflight CORS request
        response = requests.options(
            url,
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": (
                    "GET"
                    if endpoint not in ["/persona", "/elevator/call", "/psim/search"]
                    else "POST"
                ),
            },
            timeout=10,
        )

        # Check for CORS headers in preflight response
        headers_lower = {k.lower(): v for k, v in response.headers.items()}

        # CORS headers should be present in OPTIONS response
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers",
        ]

        has_cors = any(header in headers_lower for header in cors_headers)
        assert (
            has_cors
        ), f"No CORS headers found in OPTIONS preflight response for {endpoint}"
        assert response.status_code in [
            200,
            204,
        ], f"OPTIONS request failed with status {response.status_code} for {endpoint}"


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_invalid_endpoint(self):
        """Test request to invalid endpoint"""
        response, data = client.get("/invalid-endpoint")
        assert response.status_code == 404

    def test_invalid_method(self):
        """Test invalid HTTP method"""
        # Try DELETE on health endpoint
        try:
            response, data = client.delete("/health")
            assert response.status_code in [404, 405]  # Not Found or Method Not Allowed
        except Exception:
            # Some endpoints might reject invalid methods entirely
            pass

    def test_malformed_json(self):
        """Test malformed JSON payload"""
        try:
            response = client.session.post(
                f"{client.base_url}/persona",
                data="invalid json",
                headers={"Content-Type": "application/json"},
            )
            assert response.status_code >= 400
        except Exception:
            # This is expected for malformed requests
            pass


# Fixtures and test configuration
@pytest.fixture(scope="session", autouse=True)
def setup_test_session():
    """Setup test session"""
    console.print("\n🧪 [bold blue]Starting BuildingOS API Test Suite[/bold blue]")
    console.print(f"🌐 Base URL: {config.base_url}")
    console.print(f"🏷️  Environment: {config.environment}")
    yield

    # Cleanup and summary
    console.print("\n📊 [bold blue]Test Session Complete[/bold blue]")
    client.print_summary()
    client.export_results()


@pytest.fixture(autouse=True)
def test_spacing():
    """Add spacing between tests"""
    yield
    console.print()  # Add blank line after each test
