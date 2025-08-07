# API Test Client with advanced features
import json
import time
from typing import Dict, Any, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from .config import config

console = Console()


class APITestClient:
    """Advanced API test client with retry logic, timing, and detailed logging"""

    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or config.base_url
        self.timeout = timeout or config.timeout
        self.session = self._create_session()
        self.request_history = []

    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy"""
        session = requests.Session()

        # Retry strategy
        retry_strategy = Retry(
            total=config.retry_count,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Tuple[requests.Response, Dict[str, Any]]:
        """Make an HTTP request with detailed timing and logging"""
        url = f"{self.base_url}{endpoint}"

        # Prepare request info
        request_info = {
            "method": method.upper(),
            "url": url,
            "timestamp": time.time(),
            "headers": kwargs.get("headers", {}),
            "payload": kwargs.get("json", kwargs.get("data")),
        }

        console.print(f"\n🚀 [bold cyan]{method.upper()}[/bold cyan] {endpoint}")

        start_time = time.time()

        try:
            response = self.session.request(
                method=method, url=url, timeout=self.timeout, **kwargs
            )

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"raw_response": response.text}

            # Log request details
            request_info.update(
                {
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                    "response_size": len(response.content),
                    "response_data": response_data,
                    "success": 200 <= response.status_code < 300,
                }
            )

            self.request_history.append(request_info)

            # Console output
            status_color = "green" if request_info["success"] else "red"
            console.print(
                f"📊 Status: [{status_color}]{response.status_code}[/{status_color}] | "
                f"⏱️  Time: {response_time:.2f}ms | "
                f"📦 Size: {len(response.content)} bytes"
            )

            return response, response_data

        except requests.exceptions.RequestException as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            request_info.update(
                {
                    "status_code": 0,
                    "response_time_ms": round(response_time, 2),
                    "error": str(e),
                    "success": False,
                }
            )

            self.request_history.append(request_info)

            console.print(f"❌ [bold red]Request failed[/bold red]: {e}")
            raise

    def get(self, endpoint: str, **kwargs) -> Tuple[requests.Response, Dict[str, Any]]:
        return self.make_request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Tuple[requests.Response, Dict[str, Any]]:
        return self.make_request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Tuple[requests.Response, Dict[str, Any]]:
        return self.make_request("PUT", endpoint, **kwargs)

    def delete(
        self, endpoint: str, **kwargs
    ) -> Tuple[requests.Response, Dict[str, Any]]:
        return self.make_request("DELETE", endpoint, **kwargs)

    def print_summary(self):
        """Print a summary of all requests made"""
        if not self.request_history:
            console.print("📭 No requests made yet")
            return

        table = Table(title="🔍 Request Summary")
        table.add_column("Method", style="cyan")
        table.add_column("Endpoint", style="blue")
        table.add_column("Status", style="bold")
        table.add_column("Time (ms)", style="yellow")
        table.add_column("Success", style="bold")

        for req in self.request_history:
            status_style = "green" if req["success"] else "red"
            success_emoji = "✅" if req["success"] else "❌"

            table.add_row(
                req["method"],
                req["url"].replace(self.base_url, ""),
                f"[{status_style}]{req['status_code']}[/{status_style}]",
                str(req["response_time_ms"]),
                success_emoji,
            )

        console.print(table)

        # Performance metrics
        successful_requests = [r for r in self.request_history if r["success"]]
        if successful_requests:
            times = [r["response_time_ms"] for r in successful_requests]
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)

            metrics_panel = Panel(
                f"📈 Avg: {avg_time:.2f}ms | ⚡ Min: {min_time:.2f}ms | 🐌 Max: {max_time:.2f}ms",
                title="Performance Metrics",
                border_style="blue",
            )
            console.print(metrics_panel)

    def export_results(self, filename: str = None):
        """Export request history to JSON file"""
        if not filename:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"api-test-results-{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.request_history, f, indent=2, ensure_ascii=False)

        console.print(f"💾 Results exported to: [bold green]{filename}[/bold green]")
        return filename


# Global client instance
client = APITestClient()
