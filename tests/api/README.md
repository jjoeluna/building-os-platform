# BuildingOS API Testing Suite

Comprehensive testing suite for BuildingOS APIs with rapid diagnostic capabilities and complete validation.

## 🚀 Quick Start

```bash
# From project root directory
.\tests\api\quick_setup.ps1  # Automatic setup + rapid diagnosis
```

## 🛠️ Tools Overview

### 🔍 `diagnose_api.py` - Rapid Diagnosis
**Purpose:** Quick troubleshooting and AWS logs analysis  
**Duration:** ~30 seconds  
**Use Case:** Feedback loop during development

```bash
python diagnose_api.py
```

**Features:**
- ⚡ Quick endpoint testing
- 📋 CloudWatch logs integration  
- 🎯 Automatic problem prioritization
- 📊 Real-time performance metrics
- 🚨 Critical issue identification

### 🧪 `run_tests.py` - Comprehensive Testing
**Purpose:** Complete validation and detailed reports  
**Duration:** ~2-3 minutes  
**Use Case:** Complete validation and documentation

```bash
python run_tests.py
```

**Features:**
- 🔬 24 structured test cases with pytest
- 📈 Detailed reports in HTML and JSON
- 🔄 Retry logic and timeout handling
- 📊 Quality metrics and performance analysis
- 🎨 Rich console output with progress tracking

## ⚡ Optimized Development Workflow

### Strategy by Development Phase

| Phase | Primary Tool | Secondary Tool | Purpose |
|-------|-------------|----------------|---------|
| **Initial Diagnosis** | `diagnose_api.py` | - | Map current issues |
| **Development Loop** | `diagnose_api.py` | specific pytest | Quick feedback |
| **Post-Implementation** | `run_tests.py` | `diagnose_api.py` | Complete validation |
| **Pre-Deploy** | Both | - | Total confidence |
| **Post-Deploy** | `run_tests.py` | - | Final confirmation |

### Quick Commands

```bash
# Setup
.\.venv\Scripts\Activate.ps1 && cd tests\api

# Rapid Development Cycle
python diagnose_api.py                                    # Quick verification
python -m pytest test_endpoints.py::TestElevatorEndpoint # Specific validation

# Complete Validation
python run_tests.py                                       # Complete suite

# Focus on Specific Endpoint
python -m pytest test_endpoints.py::TestPersonaEndpoint -v
python -m pytest test_endpoints.py::TestCORSHeaders -v
```

## 📁 Structure

```
tests/api/
├── __init__.py              # Package initialization
├── requirements.txt         # Python dependencies
├── pytest.ini             # pytest configuration
├── run_tests.py           # Main execution script
├── config.py              # Test configurations and payloads
├── client.py              # Advanced HTTP client
├── utils.py               # Utilities and helpers
├── test_endpoints.py      # Functional endpoint tests
├── test_performance.py    # Performance and load tests
└── reports/               # Generated reports
```

## 🛠️ Installation

```bash
# Navigate to test directory
cd tests/api

# Install dependencies
python run_tests.py --install-deps
```

## 🧪 Execution of Tests

### Basic Commands

```bash
# Run all tests
python run_tests.py all

# Only functional tests
python run_tests.py endpoints

# Performance tests
python run_tests.py performance

# Smoke tests
python run_tests.py smoke

# Quick tests (no load/performance)
python run_tests.py quick
```

### Advanced Options

```bash
# Verbose output
python run_tests.py all -v

# Do not generate reports
python run_tests.py endpoints --no-report

# Show information about tests
python run_tests.py --info
```

### Direct Pytest

```bash
# Use direct pytest
pytest test_endpoints.py -v

# Run specific tests
pytest test_endpoints.py::TestHealthEndpoint::test_health_check_success -v

# Run only smoke tests
pytest -m "not slow and not load" -v

# Generate HTML report
pytest --html=reports/report.html --self-contained-html
```

## 📊 Types of Tests

### 1. Functional Tests (`test_endpoints.py`)

- **Health Check**: Basic system verification
- **Director**: Mission creation and orchestration
- **Persona**: User messages and conversations
- **Elevator**: Elevator control
- **PSIM**: Search and authentication operations
- **Coordinator**: Mission status
- **CORS**: CORS header validation
- **Error Handling**: Error handling

### 2. Performance Tests (`test_performance.py`)

- **Response Time**: Individual response time
- **Concurrent Requests**: Concurrent requests
- **Sustained Load**: Sustained load
- **Stress Testing**: Stress scenarios
- **Boundary Conditions**: Boundary conditions

## 🎯 Examples of Usage

### Simple Client Test

```python
from tests.api import client, config

# Make a request
response, data = client.get("/health")
print(f"Status: {response.status_code}")
print(f"Data: {data}")

# Show summary
client.print_summary()
```

### Custom Test

```python
import pytest
from tests.api import client, TestPayloads

def test_custom_persona():
    payload = TestPayloads.persona_message(
        user_id="custom-user",
        message="Custom test message"
    )
    
    response, data = client.post("/persona", json=payload)
    assert response.status_code == 200
    assert "session_id" in data
```

### Endpoint Monitoring

```python
from tests.api import EndpointMonitor

monitor = EndpointMonitor("https://api.example.com")

endpoints = [
    {"endpoint": "/health", "method": "GET"},
    {"endpoint": "/persona", "method": "POST", "payload": {"user_id": "test", "message": "test"}}
]

results = monitor.monitor_all_endpoints(endpoints)
monitor.print_health_report(results)
```

## 📈 Reports

### HTML Report
- Visual interface with graphs
- Detailed test results
- Performance metrics
- Screenshots of failures

### JSON Report
- Structured data for programmatic analysis
- Detailed metrics
- Historical requests
- Integration with CI/CD tools

### Console Output
- Real-time feedback
- Colors and emojis for clarity
- Progress bars
- Automatic summaries

## 🔧 Configuration

### Environment Variables

```bash
# Base API URL
export API_BASE_URL="https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com"

# Request timeout (seconds)
export API_TIMEOUT=30

# Number of retries on failure
export API_RETRY_COUNT=3

# Test environment
export ENVIRONMENT=dev

# User ID for tests
export TEST_USER_ID=api-test-user
```

### Code Configuration

```python
from tests.api.config import APIConfig

# Custom configuration
config = APIConfig(
    base_url="https://custom-api.example.com",
    timeout=60,
    retry_count=5
)
```

## 🚨 Troubleshooting

### Failing Tests

1. **Check connectivity**:
   ```bash
   curl -X GET "https://pj4vlvxrg7.execute-api.us-east-1.amazonaws.com/health"
   ```

2. **Check logs**:
   - Logs appear in console during execution
   - Check HTML/JSON reports for details

3. **Run individual test**:
   ```bash
   pytest test_endpoints.py::TestHealthEndpoint::test_health_check_success -v -s
   ```

### Performance Issues

1. **Run only performance tests**:
   ```bash
   python run_tests.py performance
   ```

2. **Check metrics in report**:
   - Average response time
   - Latency percentiles
   - Success rate

### Dependency Issues

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Update pip
python -m pip install --upgrade pip
```

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
- name: Run API Tests
  run: |
    cd tests/api
    python run_tests.py quick --no-report
    
- name: Upload Test Reports
  uses: actions/upload-artifact@v3
  with:
    name: api-test-reports
    path: tests/api/reports/
```

### Azure DevOps

```yaml
- script: |
    cd tests/api
    python run_tests.py all
  displayName: 'Run API Tests'
  
- task: PublishTestResults@2
  inputs:
    testResultsFiles: 'tests/api/reports/*.xml'
```

## 📚 References

- [pytest Documentation](https://docs.pytest.org/)
- [requests Documentation](https://docs.python-requests.org/)
- [rich Documentation](https://rich.readthedocs.io/)
- [BuildingOS API Documentation](../../docs/02-architecture/02-api-contract.md)
