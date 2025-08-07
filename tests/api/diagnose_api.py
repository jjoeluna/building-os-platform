#!/usr/bin/env python3
"""
API Diagnostics Tool
Automated diagnosis of BuildingOS API issues based on test results
"""

import json
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()


class APIDiagnostics:
    def __init__(
        self, base_url: str = "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com"
    ):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
        # Capture start time for log filtering - only check logs from test execution
        self.start_time = datetime.now()

        # Test results from our pytest run
        self.known_issues = {
            "elevator": {"status": "CRITICAL", "error": "500 errors", "priority": 1},
            "persona_conversations": {
                "status": "CRITICAL",
                "error": "500 errors",
                "priority": 1,
            },
            "persona_status": {
                "status": "WARNING",
                "error": "202 vs 200",
                "priority": 2,
            },
            "cors": {"status": "WARNING", "error": "Missing headers", "priority": 2},
            "coordinator_404": {
                "status": "EXPECTED",
                "error": "404 for non-existent",
                "priority": 3,
            },
        }

    def diagnose_endpoint(
        self, endpoint: str, method: str = "GET", payload: Dict = None
    ) -> Dict[str, Any]:
        """Diagnose a specific endpoint"""
        url = f"{self.base_url}{endpoint}"

        try:
            start_time = time.time()

            # Add Origin header to trigger CORS response
            cors_headers = {"Origin": "http://localhost:3000"}

            if method == "POST":
                headers = {**cors_headers, "Content-Type": "application/json"}
                response = self.session.post(url, json=payload, headers=headers)
            else:
                response = self.session.get(url, headers=cors_headers)

            elapsed = (time.time() - start_time) * 1000

            return {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "response_time_ms": round(elapsed, 2),
                "headers": dict(response.headers),
                "has_cors": self._check_cors_headers(response.headers),
                "content_length": len(response.content),
                "success": response.status_code < 400,
                "error": (
                    None
                    if response.status_code < 400
                    else f"HTTP {response.status_code}"
                ),
            }

        except Exception as e:
            return {
                "endpoint": endpoint,
                "status_code": None,
                "response_time_ms": None,
                "headers": {},
                "has_cors": False,
                "content_length": 0,
                "success": False,
                "error": str(e),
            }

    def _check_cors_headers(self, headers: Dict) -> bool:
        """Check if CORS headers are present"""
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers",
        ]
        headers_lower = {k.lower(): v for k, v in headers.items()}
        return any(header in headers_lower for header in cors_headers)

    def check_aws_logs(self, function_name: str, hours_back: int = 1) -> Dict[str, Any]:
        """Check AWS CloudWatch logs for a Lambda function from test start time"""
        try:
            # Use start time of test execution instead of fixed hours back
            since_timestamp = int(self.start_time.timestamp() * 1000)

            cmd = [
                "aws",
                "logs",
                "filter-log-events",
                "--log-group-name",
                f"/aws/lambda/{function_name}",
                "--start-time",
                str(since_timestamp),
                "--output",
                "json",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                log_data = json.loads(result.stdout)
                events = log_data.get("events", [])

                # Look for actual ERROR level logs, not just messages containing "Error"
                error_events = [
                    e
                    for e in events
                    if e.get("message", "").strip().startswith(("[ERROR]", "ERROR"))
                ]

                # Filter recent errors (since test started)
                start_timestamp_ms = int(self.start_time.timestamp() * 1000)

                recent_error_events = []
                for e in error_events:
                    event_timestamp = e.get("timestamp", 0)
                    if event_timestamp >= start_timestamp_ms:
                        recent_error_events.append(e)

                duration_events = [
                    e for e in events if "Duration:" in e.get("message", "")
                ]

                return {
                    "function_name": function_name,
                    "total_events": len(events),
                    "error_events": len(error_events),
                    "recent_errors": len(recent_error_events),
                    "avg_duration": self._calculate_avg_duration(duration_events),
                    "accessible": True,
                }
            else:
                return {
                    "function_name": function_name,
                    "accessible": False,
                    "error": result.stderr,
                }

        except Exception as e:
            return {
                "function_name": function_name,
                "accessible": False,
                "error": str(e),
            }

    def _calculate_avg_duration(self, duration_events: List[Dict]) -> float:
        """Calculate average duration from CloudWatch events"""
        if not duration_events:
            return 0.0

        durations = []
        for event in duration_events[-10:]:  # Last 10 executions
            message = event.get("message", "")
            try:
                # Extract duration from "Duration: 1234.56 ms"
                duration_str = message.split("Duration: ")[1].split(" ms")[0]
                durations.append(float(duration_str))
            except:
                continue

        return sum(durations) / len(durations) if durations else 0.0

    def run_full_diagnosis(self) -> Dict[str, Any]:
        """Run complete API diagnosis"""
        console.print("\n🔍 [bold cyan]Starting API Diagnosis...[/bold cyan]")

        # Test endpoints
        endpoints_to_test = [
            ("/health", "GET", None),
            ("/director", "GET", None),
            ("/persona", "POST", {"user_id": "diag-user", "message": "test"}),
            ("/persona/conversations?user_id=diag-user", "GET", None),
            ("/elevator/call", "POST", {"mission_id": "diag-123", "action": "test"}),
            ("/psim/search", "POST", {"action": "search_person", "query": "test"}),
            ("/coordinator/status", "GET", None),
        ]

        results = {}

        # Test each endpoint
        for endpoint, method, payload in endpoints_to_test:
            console.print(f"Testing {method} {endpoint}...")
            results[endpoint] = self.diagnose_endpoint(endpoint, method, payload)
            time.sleep(0.5)  # Be nice to the API

        # Check AWS logs for problematic functions
        lambda_functions = [
            "bos-agent-elevator-dev",
            "bos-agent-persona-dev",
            "bos-agent-director-dev",
            "bos-agent-coordinator-dev",
            "bos-agent-psim-dev",
            "bos-health-check-dev",
        ]

        log_results = {}
        console.print("\n📋 [bold cyan]Checking AWS CloudWatch logs...[/bold cyan]")
        for func in lambda_functions:
            console.print(f"Checking logs for {func}...")
            log_results[func] = self.check_aws_logs(func)

        return {
            "timestamp": datetime.now().isoformat(),
            "endpoint_results": results,
            "log_analysis": log_results,
            "summary": self._generate_summary(results, log_results),
        }

    def _generate_summary(
        self, endpoint_results: Dict, log_results: Dict
    ) -> Dict[str, Any]:
        """Generate diagnosis summary"""
        total_endpoints = len(endpoint_results)
        working_endpoints = sum(1 for r in endpoint_results.values() if r["success"])

        critical_issues = []
        warnings = []

        # Analyze endpoint results
        for endpoint, result in endpoint_results.items():
            if not result["success"]:
                if result["status_code"] and result["status_code"] >= 500:
                    critical_issues.append(f"{endpoint}: {result['error']}")
                else:
                    warnings.append(f"{endpoint}: {result['error']}")

            if not result["has_cors"]:
                warnings.append(f"{endpoint}: Missing CORS headers")

        # Analyze log results - only consider errors from test execution period
        for func, logs in log_results.items():
            if logs.get("accessible") and logs.get("error_events", 0) > 0:
                # Only report as critical if errors occurred during test execution
                if logs.get("recent_errors", 0) > 0:
                    critical_issues.append(
                        f"{func}: {logs['recent_errors']} recent errors in logs"
                    )
                else:
                    warnings.append(
                        f"{func}: {logs['error_events']} older errors found (not from current test)"
                    )

        return {
            "total_endpoints": total_endpoints,
            "working_endpoints": working_endpoints,
            "success_rate": round((working_endpoints / total_endpoints) * 100, 1),
            "critical_issues": critical_issues,
            "warnings": warnings,
            "priority_actions": self._get_priority_actions(critical_issues, warnings),
        }

    def _get_priority_actions(
        self, critical_issues: List[str], warnings: List[str]
    ) -> List[str]:
        """Generate priority action list"""
        actions = []

        if any("elevator" in issue.lower() for issue in critical_issues):
            actions.append("🚨 URGENT: Fix Elevator API 500 errors")

        if any("persona" in issue.lower() for issue in critical_issues):
            actions.append("🚨 URGENT: Fix Persona Conversations 500 errors")

        if any("cors" in warning.lower() for warning in warnings):
            actions.append("⚠️  Add CORS headers to all endpoints")

        if any("director" in issue.lower() for issue in critical_issues + warnings):
            actions.append("⚠️  Optimize Director performance")

        return actions

    def print_report(self, diagnosis: Dict[str, Any]):
        """Print formatted diagnosis report"""
        console.print("\n" + "=" * 80)
        console.print("[bold green]🏥 API HEALTH DIAGNOSIS REPORT[/bold green]")
        console.print("=" * 80)

        summary = diagnosis["summary"]

        # Summary table
        summary_table = Table(title="📊 Overall Health")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total Endpoints", str(summary["total_endpoints"]))
        summary_table.add_row("Working Endpoints", str(summary["working_endpoints"]))
        summary_table.add_row("Success Rate", f"{summary['success_rate']}%")
        summary_table.add_row("Critical Issues", str(len(summary["critical_issues"])))
        summary_table.add_row("Warnings", str(len(summary["warnings"])))

        console.print(summary_table)

        # Endpoint details
        endpoint_table = Table(title="🔗 Endpoint Status")
        endpoint_table.add_column("Endpoint", style="cyan")
        endpoint_table.add_column("Status", style="white")
        endpoint_table.add_column("Response Time", style="yellow")
        endpoint_table.add_column("CORS", style="blue")
        endpoint_table.add_column("Issues", style="red")

        for endpoint, result in diagnosis["endpoint_results"].items():
            status = "✅ OK" if result["success"] else "❌ FAIL"
            response_time = (
                f"{result['response_time_ms']}ms"
                if result["response_time_ms"]
                else "N/A"
            )
            cors = "✅" if result["has_cors"] else "❌"
            issues = result["error"] or "None"

            endpoint_table.add_row(endpoint, status, response_time, cors, issues)

        console.print(endpoint_table)

        # Priority actions
        if summary["priority_actions"]:
            console.print("\n[bold red]🎯 PRIORITY ACTIONS:[/bold red]")
            for i, action in enumerate(summary["priority_actions"], 1):
                console.print(f"{i}. {action}")

        # Critical issues detail
        if summary["critical_issues"]:
            console.print("\n[bold red]🚨 CRITICAL ISSUES:[/bold red]")
            for issue in summary["critical_issues"]:
                console.print(f"  • {issue}")

        # Warnings detail
        if summary["warnings"]:
            console.print("\n[bold yellow]⚠️  WARNINGS:[/bold yellow]")
            for warning in summary["warnings"]:
                console.print(f"  • {warning}")


def main():
    diagnostics = APIDiagnostics()

    try:
        # Run full diagnosis
        results = diagnostics.run_full_diagnosis()

        # Print report
        diagnostics.print_report(results)

        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/api_diagnosis_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)

        console.print(f"\n💾 [green]Diagnosis saved to: {filename}[/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Diagnosis interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during diagnosis: {e}[/red]")


if __name__ == "__main__":
    main()
