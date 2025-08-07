# API Test Utilities and Helper Functions
import json
import time
import functools
from typing import Callable, Any, Dict, List
from pathlib import Path
import requests
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function calls on failure"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        console.print(
                            f"⚠️ Attempt {attempt + 1} failed: {e}, retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        console.print(f"❌ All {max_retries} attempts failed")

            raise last_exception

        return wrapper

    return decorator


def measure_time(func: Callable) -> Callable:
    """Decorator to measure function execution time"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        execution_time = (end_time - start_time) * 1000
        console.print(f"⏱️ {func.__name__} took {execution_time:.2f}ms")

        return result

    return wrapper


class TestDataGenerator:
    """Generate test data for various scenarios"""

    @staticmethod
    def generate_user_ids(count: int = 10) -> List[str]:
        """Generate unique user IDs for testing"""
        timestamp = int(time.time())
        return [f"test-user-{timestamp}-{i}" for i in range(count)]

    @staticmethod
    def generate_mission_ids(count: int = 10) -> List[str]:
        """Generate unique mission IDs for testing"""
        timestamp = int(time.time())
        return [f"test-mission-{timestamp}-{i}" for i in range(count)]

    @staticmethod
    def generate_test_messages(count: int = 10) -> List[str]:
        """Generate test messages of varying lengths"""
        base_messages = [
            "Call elevator to floor 3",
            "Search for John Doe in the system",
            "Check building status",
            "Emergency evacuation procedure",
            "Schedule maintenance for elevator A",
        ]

        messages = []
        for i in range(count):
            base_msg = base_messages[i % len(base_messages)]
            messages.append(f"{base_msg} - Test {i+1}")

        return messages


class APITestReporter:
    """Generate comprehensive test reports"""

    def __init__(self, results_file: str = None):
        self.results_file = results_file or f"api-test-results-{int(time.time())}.json"
        self.results = []

    def add_result(
        self,
        test_name: str,
        endpoint: str,
        success: bool,
        response_time: float,
        details: Dict[str, Any] = None,
    ):
        """Add a test result"""
        result = {
            "test_name": test_name,
            "endpoint": endpoint,
            "success": success,
            "response_time_ms": response_time,
            "timestamp": time.time(),
            "details": details or {},
        }
        self.results.append(result)

    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not self.results:
            return {"error": "No test results available"}

        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - successful_tests

        response_times = [r["response_time_ms"] for r in self.results if r["success"]]

        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate_percent": (successful_tests / total_tests) * 100,
            "performance": {
                "avg_response_time_ms": (
                    sum(response_times) / len(response_times) if response_times else 0
                ),
                "min_response_time_ms": min(response_times) if response_times else 0,
                "max_response_time_ms": max(response_times) if response_times else 0,
                "total_response_time_ms": sum(response_times),
            },
            "test_duration_seconds": max(r["timestamp"] for r in self.results)
            - min(r["timestamp"] for r in self.results),
            "endpoints_tested": list(set(r["endpoint"] for r in self.results)),
        }

        return summary

    def save_results(self, filename: str = None):
        """Save results to JSON file"""
        filename = filename or self.results_file

        report_data = {
            "summary": self.generate_summary_report(),
            "results": self.results,
            "generated_at": time.time(),
            "generated_at_iso": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        console.print(f"💾 Test results saved to: [bold green]{filename}[/bold green]")
        return filename

    def print_summary_table(self):
        """Print a summary table to console"""
        if not self.results:
            console.print("📭 No test results to display")
            return

        summary = self.generate_summary_report()

        # Create summary table
        table = Table(title="🧪 API Test Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")

        table.add_row("Total Tests", str(summary["total_tests"]))
        table.add_row("Successful", f"[green]{summary['successful_tests']}[/green]")
        table.add_row("Failed", f"[red]{summary['failed_tests']}[/red]")
        table.add_row("Success Rate", f"{summary['success_rate_percent']:.1f}%")
        table.add_row(
            "Avg Response Time",
            f"{summary['performance']['avg_response_time_ms']:.2f}ms",
        )
        table.add_row(
            "Max Response Time",
            f"{summary['performance']['max_response_time_ms']:.2f}ms",
        )
        table.add_row("Total Duration", f"{summary['test_duration_seconds']:.2f}s")

        console.print(table)

        # Failed tests details
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            console.print("\n❌ [bold red]Failed Tests:[/bold red]")
            for test in failed_tests:
                console.print(f"   • {test['test_name']} ({test['endpoint']})")


class EndpointMonitor:
    """Monitor endpoint health and availability"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def check_endpoint_health(
        self,
        endpoint: str,
        method: str = "GET",
        payload: Dict = None,
        timeout: int = 10,
    ) -> Dict[str, Any]:
        """Check if an endpoint is healthy"""
        url = f"{self.base_url}{endpoint}"

        try:
            start_time = time.time()

            if method.upper() == "GET":
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=payload, timeout=timeout)
            else:
                response = self.session.request(
                    method, url, json=payload, timeout=timeout
                )

            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "healthy": 200 <= response.status_code < 400,
                "timestamp": time.time(),
            }

        except requests.exceptions.RequestException as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "error": str(e),
                "healthy": False,
                "timestamp": time.time(),
            }

    def monitor_all_endpoints(
        self, endpoints: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Monitor multiple endpoints"""
        results = []

        for endpoint_config in track(endpoints, description="Monitoring endpoints..."):
            result = self.check_endpoint_health(
                endpoint_config["endpoint"],
                endpoint_config.get("method", "GET"),
                endpoint_config.get("payload"),
            )
            results.append(result)

        return results

    def print_health_report(self, health_results: List[Dict[str, Any]]):
        """Print endpoint health report"""
        table = Table(title="🏥 Endpoint Health Report")
        table.add_column("Endpoint", style="cyan")
        table.add_column("Method", style="blue")
        table.add_column("Status", style="bold")
        table.add_column("Response Time", style="yellow")
        table.add_column("Health", style="bold")

        for result in health_results:
            status = result.get("status_code", "Error")
            response_time = f"{result.get('response_time_ms', 0):.2f}ms"
            health_emoji = "✅" if result.get("healthy", False) else "❌"

            table.add_row(
                result["endpoint"],
                result["method"],
                str(status),
                response_time,
                health_emoji,
            )

        console.print(table)


# Global instances
test_reporter = APITestReporter()
data_generator = TestDataGenerator()
