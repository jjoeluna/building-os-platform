#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BuildingOS API Test Runner
Advanced Python-based API testing suite with comprehensive reporting
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# Set UTF-8 encoding for Windows compatibility
if sys.platform.startswith("win"):
    # Set environment variables for UTF-8 support
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"

console = Console(force_terminal=True, legacy_windows=False)


def install_dependencies():
    """Install test dependencies"""
    console.print("📦 [bold blue]Installing test dependencies...[/bold blue]")

    requirements_file = Path(__file__).parent / "requirements.txt"

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True,
            capture_output=True,
            text=True,
        )
        console.print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)


def create_reports_directory():
    """Create reports directory if it doesn't exist"""
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    return reports_dir


def run_tests(test_type="all", verbose=False, create_report=True):
    """Run API tests with specified parameters"""

    # Create reports directory
    reports_dir = create_reports_directory()

    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]

    # Add test file based on type
    if test_type == "endpoints":
        cmd.append("test_endpoints.py")
    elif test_type == "performance":
        cmd.append("test_performance.py")
    elif test_type == "smoke":
        cmd.extend(["-m", "smoke"])
    elif test_type == "quick":
        cmd.extend(["-m", "not slow and not load"])
    elif test_type == "all":
        cmd.append(".")
    else:
        console.print(f"❌ Unknown test type: {test_type}")
        return False

    # Add verbosity
    if verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")

    # Add traceback verbosity control
    cmd.extend(["--tb", "line"])

    # Add reporting options
    if create_report:
        timestamp = subprocess.run(
            ["python", "-c", "import time; print(time.strftime('%Y%m%d-%H%M%S'))"],
            capture_output=True,
            text=True,
        ).stdout.strip()

        html_report = reports_dir / f"api-test-report-{timestamp}.html"
        json_report = reports_dir / f"api-test-report-{timestamp}.json"

        cmd.extend(
            [
                "--html",
                str(html_report),
                "--self-contained-html",
                "--json-report",
                "--json-report-file",
                str(json_report),
            ]
        )

    # Change to test directory
    test_dir = Path(__file__).parent
    original_cwd = os.getcwd()

    try:
        os.chdir(test_dir)

        console.print(f"🧪 [bold blue]Running {test_type} tests...[/bold blue]")
        console.print(f"📁 Test directory: {test_dir}")

        # Run tests
        result = subprocess.run(cmd, capture_output=False, text=True)

        if create_report:
            console.print(f"\n📊 [bold green]Reports generated:[/bold green]")
            console.print(f"   📄 HTML: {html_report}")
            console.print(f"   📄 JSON: {json_report}")

        return result.returncode == 0

    except Exception as e:
        console.print(f"❌ Error running tests: {e}")
        return False
    finally:
        os.chdir(original_cwd)


def show_test_info():
    """Show information about available tests"""

    panel_content = """
🧪 [bold]Available Test Types:[/bold]

[cyan]endpoints[/cyan]    - Test all API endpoints (basic functionality)
[cyan]performance[/cyan]  - Test response times and performance metrics  
[cyan]smoke[/cyan]        - Quick smoke tests (essential functionality)
[cyan]quick[/cyan]        - Fast tests only (excludes slow/load tests)
[cyan]all[/cyan]          - Run complete test suite

🏗️ [bold]Test Structure:[/bold]

[yellow]test_endpoints.py[/yellow]    - Functional tests for all endpoints
[yellow]test_performance.py[/yellow]  - Performance and load testing
[yellow]config.py[/yellow]           - Test configuration and payloads
[yellow]client.py[/yellow]           - Advanced HTTP client with retry logic

📊 [bold]Reports Generated:[/bold]

• HTML report with detailed results and timing
• JSON report for programmatic analysis
• Console output with real-time feedback
• Request history with performance metrics
    """

    console.print(
        Panel(panel_content, title="🔍 BuildingOS API Test Suite", border_style="blue")
    )


def main():
    parser = argparse.ArgumentParser(description="BuildingOS API Test Runner")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "endpoints", "performance", "smoke", "quick"],
        help="Type of tests to run",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--no-report", action="store_true", help="Skip generating reports"
    )
    parser.add_argument(
        "--install-deps", action="store_true", help="Install dependencies first"
    )
    parser.add_argument("--info", action="store_true", help="Show test information")

    args = parser.parse_args()

    # Show header
    console.print("\n🚀 [bold blue]BuildingOS API Test Suite[/bold blue]")
    console.print("=" * 50)

    if args.info:
        show_test_info()
        return

    if args.install_deps:
        install_dependencies()

    # Run tests
    success = run_tests(
        test_type=args.test_type, verbose=args.verbose, create_report=not args.no_report
    )

    if success:
        console.print("\n🎉 [bold green]All tests completed successfully![/bold green]")
        sys.exit(0)
    else:
        console.print("\n💥 [bold red]Some tests failed![/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
