# Performance and Load Testing
import pytest
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from .client import client
from .config import config
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

console = Console()


class TestPerformance:
    """Performance testing for API endpoints"""

    def test_response_time_under_threshold(self):
        """Test that all endpoints respond within acceptable time"""
        endpoints = [
            ("/health", "GET", None),
            ("/director", "GET", None),
            ("/persona", "POST", {"user_id": "perf-test", "message": "test"}),
            ("/psim/search", "POST", {"action": "search_person", "query": "test"}),
            ("/coordinator/missions/perf-test-123", "GET", None),
        ]

        threshold_ms = 3000  # 3 seconds

        for endpoint, method, payload in endpoints:
            start_time = time.time()

            if method == "GET":
                response, data = client.get(endpoint)
            else:
                response, data = client.post(endpoint, json=payload)

            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            assert (
                response_time < threshold_ms
            ), f"{endpoint} took {response_time:.2f}ms (threshold: {threshold_ms}ms)"

    def test_concurrent_health_checks(self):
        """Test multiple concurrent health check requests"""

        def make_health_request():
            response, data = client.get("/health")
            return response.status_code == 200, response.elapsed.total_seconds() * 1000

        concurrent_requests = 5

        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [
                executor.submit(make_health_request) for _ in range(concurrent_requests)
            ]
            results = [future.result() for future in as_completed(futures)]

        # All requests should succeed
        success_count = sum(1 for success, _ in results if success)
        assert success_count == concurrent_requests

        # Average response time should be reasonable
        avg_time = sum(time for _, time in results) / len(results)
        assert avg_time < 5000  # 5 seconds average


class TestLoadTesting:
    """Load testing scenarios"""

    @pytest.mark.slow
    def test_sustained_load_health_endpoint(self):
        """Test sustained load on health endpoint"""
        console.print("\n🔥 [bold yellow]Running sustained load test...[/bold yellow]")

        requests_per_second = 2
        duration_seconds = 10
        total_requests = requests_per_second * duration_seconds

        results = []

        with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Making {total_requests} requests...", total=total_requests
            )

            for i in range(total_requests):
                start_time = time.time()

                try:
                    response, data = client.get("/health")
                    end_time = time.time()

                    results.append(
                        {
                            "success": response.status_code == 200,
                            "response_time": (end_time - start_time) * 1000,
                            "request_number": i + 1,
                        }
                    )

                except Exception as e:
                    results.append(
                        {"success": False, "error": str(e), "request_number": i + 1}
                    )

                progress.update(task, advance=1)

                # Rate limiting
                if i < total_requests - 1:
                    time.sleep(1 / requests_per_second)

        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        success_rate = len(successful_requests) / len(results) * 100

        console.print(
            f"✅ Success rate: {success_rate:.1f}% ({len(successful_requests)}/{len(results)})"
        )

        if successful_requests:
            times = [r["response_time"] for r in successful_requests]
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)

            console.print(f"⏱️  Avg response: {avg_time:.2f}ms")
            console.print(f"🐌 Max response: {max_time:.2f}ms")
            console.print(f"⚡ Min response: {min_time:.2f}ms")

        # Assertions
        assert success_rate >= 95, f"Success rate too low: {success_rate:.1f}%"
        if successful_requests:
            avg_time = sum(r["response_time"] for r in successful_requests) / len(
                successful_requests
            )
            assert avg_time < 2000, f"Average response time too high: {avg_time:.2f}ms"


class TestStressScenarios:
    """Stress testing with edge cases"""

    def test_large_payload_persona(self):
        """Test persona endpoint with large message"""
        large_message = "x" * 10000  # 10KB message
        payload = {"user_id": "stress-test-user", "message": large_message}

        response, data = client.post("/persona", json=payload)

        # Should handle large payloads gracefully
        assert response.status_code in [
            200,
            413,
            400,
        ]  # Success, Payload Too Large, or Bad Request

    def test_rapid_successive_requests(self):
        """Test rapid successive requests to same endpoint"""
        rapid_requests = 10
        results = []

        start_time = time.time()

        for i in range(rapid_requests):
            try:
                response, data = client.get("/health")
                results.append(response.status_code == 200)
            except Exception:
                results.append(False)

        end_time = time.time()
        total_time = end_time - start_time

        success_count = sum(results)
        success_rate = success_count / rapid_requests * 100

        console.print(f"🚀 Rapid requests: {rapid_requests} in {total_time:.2f}s")
        console.print(f"✅ Success rate: {success_rate:.1f}%")

        # At least 80% should succeed
        assert success_rate >= 80

    def test_special_characters_in_requests(self):
        """Test endpoints with special characters"""
        special_chars_tests = [
            {
                "user_id": "test-user",
                "message": "Hello! 🚀 Testing with émojis and açcents",
            },
            {"user_id": "test-中文-user", "message": "Testing with 中文 characters"},
            {
                "user_id": "test'quote",
                "message": "Testing with 'quotes' and \"double quotes\"",
            },
        ]

        for payload in special_chars_tests:
            response, data = client.post("/persona", json=payload)

            # Should handle special characters without crashing
            assert response.status_code < 500  # No server errors


class TestBoundaryConditions:
    """Test boundary conditions and edge cases"""

    def test_empty_payloads(self):
        """Test endpoints with empty payloads"""
        endpoints_requiring_payload = ["/persona", "/elevator/call", "/psim/search"]

        for endpoint in endpoints_requiring_payload:
            response, data = client.post(endpoint, json={})

            # Should return 4xx for empty payloads, not crash
            assert response.status_code < 500
            assert "error" in data or response.status_code >= 400

    def test_null_values_in_payload(self):
        """Test endpoints with null values"""
        payload = {"user_id": None, "message": None}

        response, data = client.post("/persona", json=payload)

        # Should handle null values gracefully
        assert response.status_code < 500

    def test_extremely_long_mission_id(self):
        """Test coordinator with very long mission ID"""
        long_mission_id = "x" * 1000  # 1000 character mission ID

        response, data = client.get(f"/coordinator/missions/{long_mission_id}")

        # Should handle long IDs without crashing
        assert response.status_code < 500


# Custom markers for different test types
pytest.mark.slow = pytest.mark.slow
pytest.mark.load = pytest.mark.load
