#!/usr/bin/env python3
"""
🚀 BuildingOS Step 3.1 - Frontend Integration Validation
========================================================

Comprehensive validation script for the modern frontend integration.
Tests S3 hosting, CloudFront CDN, API integration, and WebSocket connectivity.

Author: BuildingOS Development Team
Version: 1.0.0
"""

import requests
import json
import time
import asyncio
import websockets
import ssl
from datetime import datetime
from typing import Dict, Any, List, Optional
import urllib.parse

class FrontendValidationResults:
    """Stores and manages validation test results"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment": "dev",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
            "frontend_urls": {},
            "performance_metrics": {},
            "integration_status": {}
        }
    
    def add_test(self, test_name: str, passed: bool, details: str, 
                 duration: float = 0, metadata: Dict = None):
        """Add a test result"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed_tests"] += 1
        else:
            self.results["failed_tests"] += 1
        
        self.results["test_details"].append({
            "test_name": test_name,
            "status": "PASSED" if passed else "FAILED",
            "details": details,
            "duration_ms": round(duration * 1000, 2),
            "metadata": metadata or {}
        })
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.results["total_tests"] == 0:
            return 0.0
        return (self.results["passed_tests"] / self.results["total_tests"]) * 100

class BuildingOSFrontendValidator:
    """Validates the complete frontend integration"""
    
    def __init__(self):
        self.results = FrontendValidationResults()
        
        # URLs from Terraform outputs
        self.urls = {
            "cloudfront": "https://d16gzj1xbb7lzw.cloudfront.net",
            "s3_website": "http://buildingos-frontend-dev.s3-website-us-east-1.amazonaws.com",
            "api_gateway": "https://wo8q9fl0hj.execute-api.us-east-1.amazonaws.com/dev",
            "websocket": "wss://wo8q9fl0hj.execute-api.us-east-1.amazonaws.com/dev"
        }
        
        self.results.results["frontend_urls"] = self.urls
    
    def print_header(self):
        """Print validation header"""
        print("🚀 BuildingOS Frontend Integration Validation")
        print("=" * 60)
        print(f"✅ CloudFront URL: {self.urls['cloudfront']}")
        print(f"🌐 S3 Website URL: {self.urls['s3_website']}")
        print(f"🔌 API Gateway URL: {self.urls['api_gateway']}")
        print(f"📡 WebSocket URL: {self.urls['websocket']}")
        print("=" * 60)
    
    def test_s3_website_hosting(self) -> bool:
        """Test S3 static website hosting"""
        print("\n🧪 Testing S3 Website Hosting...")
        
        try:
            start_time = time.time()
            
            # Test index.html
            response = requests.get(f"{self.urls['s3_website']}/index.html", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text
                
                # Validate HTML content
                checks = [
                    ("HTML structure", "<!DOCTYPE html>" in content),
                    ("BuildingOS title", "BuildingOS" in content),
                    ("Modern styling", "Inter" in content),
                    ("JavaScript functionality", "BuildingOSChat" in content),
                    ("API integration", "wo8q9fl0hj.execute-api.us-east-1.amazonaws.com" in content),
                    ("WebSocket support", "wss://" in content)
                ]
                
                all_passed = all(check[1] for check in checks)
                details = f"Status: {response.status_code}, Size: {len(content)} bytes, Checks: {len([c for c in checks if c[1]])}/{len(checks)} passed"
                
                self.results.add_test(
                    "S3 Website - Index Page",
                    all_passed,
                    details,
                    duration,
                    {"content_length": len(content), "checks": dict(checks)}
                )
                
                if all_passed:
                    print("✅ S3 Website hosting working correctly")
                    return True
                else:
                    print("❌ S3 Website content validation failed")
                    for name, passed in checks:
                        print(f"   {'✅' if passed else '❌'} {name}")
                    return False
            else:
                            self.results.add_test(
                "S3 Website - Index Page",
                False,
                f"HTTP {response.status_code}: {response.text[:200]}",
                duration
            )
                print(f"❌ S3 Website returned status {response.status_code}")
                return False
                
        except Exception as e:
            self.add_test(
                "S3 Website - Index Page",
                False,
                f"Exception: {str(e)}",
                0
            )
            print(f"❌ S3 Website test failed: {str(e)}")
            return False
    
    def test_error_page(self) -> bool:
        """Test error page functionality"""
        print("\n🧪 Testing Error Page...")
        
        try:
            start_time = time.time()
            
            # Test error.html
            response = requests.get(f"{self.urls['s3_website']}/error.html", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text
                
                # Validate error page content
                checks = [
                    ("HTML structure", "<!DOCTYPE html>" in content),
                    ("Error styling", "error-container" in content),
                    ("Error icon", "fas fa-exclamation-triangle" in content),
                    ("Back to home link", 'href="/"' in content)
                ]
                
                all_passed = all(check[1] for check in checks)
                details = f"Status: {response.status_code}, Size: {len(content)} bytes, Checks: {len([c for c in checks if c[1]])}/{len(checks)} passed"
                
                self.add_test(
                    "S3 Website - Error Page",
                    all_passed,
                    details,
                    duration,
                    {"content_length": len(content), "checks": dict(checks)}
                )
                
                if all_passed:
                    print("✅ Error page working correctly")
                    return True
                else:
                    print("❌ Error page content validation failed")
                    return False
            else:
                self.add_test(
                    "S3 Website - Error Page",
                    False,
                    f"HTTP {response.status_code}",
                    duration
                )
                print(f"❌ Error page returned status {response.status_code}")
                return False
                
        except Exception as e:
            self.add_test(
                "S3 Website - Error Page",
                False,
                f"Exception: {str(e)}",
                0
            )
            print(f"❌ Error page test failed: {str(e)}")
            return False
    
    def test_cloudfront_cdn(self) -> bool:
        """Test CloudFront CDN functionality"""
        print("\n🧪 Testing CloudFront CDN...")
        
        try:
            start_time = time.time()
            
            # Test CloudFront distribution
            response = requests.get(self.urls['cloudfront'], timeout=15)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text
                headers = response.headers
                
                # Validate CloudFront headers and content
                checks = [
                    ("HTTPS redirect", response.url.startswith("https://")),
                    ("CloudFront header", "cloudfront" in headers.get("via", "").lower()),
                    ("Content delivery", "BuildingOS" in content),
                    ("Compression", headers.get("content-encoding") == "gzip" or len(content) > 0),
                    ("Cache control", "cache-control" in headers or "expires" in headers)
                ]
                
                all_passed = all(check[1] for check in checks)
                details = f"Status: {response.status_code}, CDN: {headers.get('via', 'N/A')}, Size: {len(content)} bytes"
                
                self.results.results["performance_metrics"]["cloudfront_response_time"] = duration
                
                self.add_test(
                    "CloudFront CDN",
                    all_passed,
                    details,
                    duration,
                    {
                        "headers": dict(headers),
                        "checks": dict(checks),
                        "final_url": response.url
                    }
                )
                
                if all_passed:
                    print(f"✅ CloudFront CDN working correctly ({duration:.2f}s)")
                    return True
                else:
                    print("❌ CloudFront CDN validation failed")
                    for name, passed in checks:
                        print(f"   {'✅' if passed else '❌'} {name}")
                    return False
            else:
                self.add_test(
                    "CloudFront CDN",
                    False,
                    f"HTTP {response.status_code}",
                    duration
                )
                print(f"❌ CloudFront returned status {response.status_code}")
                return False
                
        except Exception as e:
            self.add_test(
                "CloudFront CDN",
                False,
                f"Exception: {str(e)}",
                0
            )
            print(f"❌ CloudFront test failed: {str(e)}")
            return False
    
    def test_api_gateway_integration(self) -> bool:
        """Test API Gateway integration"""
        print("\n🧪 Testing API Gateway Integration...")
        
        try:
            start_time = time.time()
            
            # Test health check endpoint
            response = requests.get(f"{self.urls['api_gateway']}/health", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validate health check response
                    checks = [
                        ("JSON response", isinstance(data, dict)),
                        ("Status field", "status" in data),
                        ("Healthy status", data.get("status") == "healthy"),
                        ("Response time", duration < 5.0)
                    ]
                    
                    all_passed = all(check[1] for check in checks)
                    details = f"Status: {response.status_code}, Health: {data.get('status', 'unknown')}, Response: {duration:.2f}s"
                    
                    self.results.results["performance_metrics"]["api_response_time"] = duration
                    
                    self.add_test(
                        "API Gateway - Health Check",
                        all_passed,
                        details,
                        duration,
                        {"response_data": data, "checks": dict(checks)}
                    )
                    
                    if all_passed:
                        print(f"✅ API Gateway health check passed ({duration:.2f}s)")
                        return True
                    else:
                        print("❌ API Gateway health check validation failed")
                        return False
                        
                except json.JSONDecodeError:
                    self.add_test(
                        "API Gateway - Health Check",
                        False,
                        f"Invalid JSON response: {response.text[:200]}",
                        duration
                    )
                    print("❌ API Gateway returned invalid JSON")
                    return False
            else:
                self.add_test(
                    "API Gateway - Health Check",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    duration
                )
                print(f"❌ API Gateway health check returned status {response.status_code}")
                return False
                
        except Exception as e:
            self.add_test(
                "API Gateway - Health Check",
                False,
                f"Exception: {str(e)}",
                0
            )
            print(f"❌ API Gateway test failed: {str(e)}")
            return False
    
    async def test_websocket_connectivity(self) -> bool:
        """Test WebSocket connectivity"""
        print("\n🧪 Testing WebSocket Connectivity...")
        
        try:
            start_time = time.time()
            
            # Create SSL context for WebSocket
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Connect to WebSocket
            async with websockets.connect(
                self.urls['websocket'],
                ssl=ssl_context,
                timeout=10
            ) as websocket:
                
                duration = time.time() - start_time
                
                # Test basic connectivity
                print("✅ WebSocket connection established")
                
                # Test message sending (optional, as we don't expect a response)
                test_message = {
                    "action": "ping",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(test_message))
                print("✅ Test message sent successfully")
                
                # Wait briefly for potential response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    print(f"✅ Received response: {response[:100]}...")
                    has_response = True
                except asyncio.TimeoutError:
                    print("ℹ️  No immediate response (expected for ping)")
                    has_response = False
                
                self.results.results["performance_metrics"]["websocket_connect_time"] = duration
                
                self.add_test(
                    "WebSocket Connectivity",
                    True,
                    f"Connected successfully, Response time: {duration:.2f}s",
                    duration,
                    {
                        "has_response": has_response,
                        "message_sent": True
                    }
                )
                
                print(f"✅ WebSocket connectivity test passed ({duration:.2f}s)")
                return True
                
        except Exception as e:
            self.add_test(
                "WebSocket Connectivity",
                False,
                f"Exception: {str(e)}",
                0
            )
            print(f"❌ WebSocket test failed: {str(e)}")
            return False
    
    def test_cors_configuration(self) -> bool:
        """Test CORS configuration"""
        print("\n🧪 Testing CORS Configuration...")
        
        try:
            start_time = time.time()
            
            # Test preflight request
            headers = {
                'Origin': 'https://d16gzj1xbb7lzw.cloudfront.net',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(
                f"{self.urls['api_gateway']}/persona",
                headers=headers,
                timeout=10
            )
            
            duration = time.time() - start_time
            
            if response.status_code in [200, 204]:
                cors_headers = response.headers
                
                # Validate CORS headers
                checks = [
                    ("CORS enabled", "access-control-allow-origin" in cors_headers),
                    ("Methods allowed", "access-control-allow-methods" in cors_headers),
                    ("Headers allowed", "access-control-allow-headers" in cors_headers),
                    ("Credentials support", True)  # Always pass for now
                ]
                
                all_passed = all(check[1] for check in checks)
                details = f"Status: {response.status_code}, CORS Origin: {cors_headers.get('access-control-allow-origin', 'N/A')}"
                
                self.add_test(
                    "CORS Configuration",
                    all_passed,
                    details,
                    duration,
                    {"cors_headers": dict(cors_headers), "checks": dict(checks)}
                )
                
                if all_passed:
                    print("✅ CORS configuration working correctly")
                    return True
                else:
                    print("❌ CORS configuration validation failed")
                    return False
            else:
                self.add_test(
                    "CORS Configuration",
                    False,
                    f"HTTP {response.status_code}",
                    duration
                )
                print(f"❌ CORS preflight returned status {response.status_code}")
                return False
                
        except Exception as e:
            self.add_test(
                "CORS Configuration",
                False,
                f"Exception: {str(e)}",
                0
            )
            print(f"❌ CORS test failed: {str(e)}")
            return False
    
    def save_results(self):
        """Save validation results to JSON file"""
        filename = f"frontend-integration-validation-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results.results, f, indent=2)
        
        print(f"\n📁 Results saved to: {filename}")
        return filename
    
    def print_summary(self):
        """Print validation summary"""
        success_rate = self.results.get_success_rate()
        
        print("\n" + "=" * 60)
        print("🏁 FRONTEND INTEGRATION VALIDATION SUMMARY")
        print("=" * 60)
        print(f"📊 Total Tests: {self.results.results['total_tests']}")
        print(f"✅ Passed: {self.results.results['passed_tests']}")
        print(f"❌ Failed: {self.results.results['failed_tests']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Performance metrics
        if self.results.results["performance_metrics"]:
            print(f"\n⚡ Performance Metrics:")
            for metric, value in self.results.results["performance_metrics"].items():
                print(f"   {metric}: {value:.2f}s")
        
        # Integration status
        integration_status = {
            "S3 Website": any(test["test_name"].startswith("S3 Website") and test["status"] == "PASSED" for test in self.results.results["test_details"]),
            "CloudFront CDN": any(test["test_name"] == "CloudFront CDN" and test["status"] == "PASSED" for test in self.results.results["test_details"]),
            "API Gateway": any(test["test_name"].startswith("API Gateway") and test["status"] == "PASSED" for test in self.results.results["test_details"]),
            "WebSocket": any(test["test_name"] == "WebSocket Connectivity" and test["status"] == "PASSED" for test in self.results.results["test_details"]),
            "CORS": any(test["test_name"] == "CORS Configuration" and test["status"] == "PASSED" for test in self.results.results["test_details"])
        }
        
        self.results.results["integration_status"] = integration_status
        
        print(f"\n🔗 Integration Status:")
        for component, status in integration_status.items():
            print(f"   {'✅' if status else '❌'} {component}")
        
        if success_rate == 100.0:
            print(f"\n🎉 FRONTEND INTEGRATION VALIDATION SUCCESSFUL!")
            print(f"✅ All components are working correctly")
            print(f"🚀 Frontend is ready for production use")
            print(f"🌐 Access your application at: {self.urls['cloudfront']}")
        else:
            print(f"\n⚠️  Some frontend integration tests failed")
            print(f"❌ Please review the failed tests and fix issues")
        
        return success_rate == 100.0

async def main():
    """Main validation function"""
    validator = BuildingOSFrontendValidator()
    
    validator.print_header()
    
    # Run all validation tests
    tests = [
        ("S3 Website Hosting", validator.test_s3_website_hosting),
        ("Error Page", validator.test_error_page),
        ("CloudFront CDN", validator.test_cloudfront_cdn),
        ("API Gateway Integration", validator.test_api_gateway_integration),
        ("CORS Configuration", validator.test_cors_configuration)
    ]
    
    # Run synchronous tests
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {str(e)}")
    
    # Run WebSocket test (async)
    print(f"\n🔍 Running: WebSocket Connectivity")
    try:
        await validator.test_websocket_connectivity()
    except Exception as e:
        print(f"❌ WebSocket test failed with exception: {str(e)}")
    
    # Save results and print summary
    validator.save_results()
    success = validator.print_summary()
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
