#!/usr/bin/env python3
"""
BuildingOS API Test Runner - Windows Safe Version
Same functionality as run_tests.py but with ASCII-only output for better Windows compatibility
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def install_dependencies():
    """Install test dependencies"""
    console.print("Installing test dependencies...", style="bold blue")

    requirements_file = Path(__file__).parent / "requirements.txt"

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True,
            capture_output=True,
            text=True,
        )
        console.print("✓ Dependencies installed successfully", style="green")
    except subprocess.CalledProcessError as e:
        console.print(f"✗ Failed to install dependencies: {e}", style="red")
        return False
    return True


def run_tests_safe(test_filter=None, verbose=False, coverage=False):
    """Run tests with Windows-safe output"""
    console.print("\n=== BuildingOS API Test Suite ===", style="bold cyan")
    console.print("Running tests with ASCII-safe output...")

    # Base pytest command
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v" if verbose else "-q",
        "--tb=short",
        "--json-report",
        "--json-report-file=reports/api-test-report-safe.json",
        # Remove HTML report to avoid encoding issues
        "--disable-warnings",
    ]

    # Add test filter if provided
    if test_filter:
        cmd.append(test_filter)

    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])

    # Set environment for UTF-8
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    try:
        console.print(f"Command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=False,  # Show output in real-time
            text=True,
        )

        return result.returncode == 0

    except Exception as e:
        console.print(f"✗ Test execution failed: {e}", style="red")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run BuildingOS API tests (Windows-safe)"
    )
    parser.add_argument("--filter", "-f", help="Filter tests by pattern")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Run with coverage"
    )
    parser.add_argument(
        "--install-deps", action="store_true", help="Install dependencies first"
    )

    args = parser.parse_args()

    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            return 1

    # Run tests
    success = run_tests_safe(
        test_filter=args.filter, verbose=args.verbose, coverage=args.coverage
    )

    if success:
        console.print("\n✓ Tests completed successfully!", style="green")
        console.print(
            "✓ Check reports/api-test-report-safe.json for detailed results",
            style="green",
        )
        return 0
    else:
        console.print("\n✗ Some tests failed!", style="red")
        return 1


if __name__ == "__main__":
    sys.exit(main())
