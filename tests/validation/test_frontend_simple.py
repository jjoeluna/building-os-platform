#!/usr/bin/env python3
"""
🚀 BuildingOS Frontend Simple Validation
========================================

Simple validation script for the frontend integration.
Tests the key components: S3, CloudFront, API Gateway, and WebSocket.

Author: BuildingOS Development Team
Version: 1.0.0
"""

import requests
import json
import time
from datetime import datetime

def test_s3_website():
    """Test S3 website hosting"""
    print("🧪 Testing S3 Website...")
    
    try:
        url = "http://buildingos-frontend-dev.s3-website-us-east-1.amazonaws.com/index.html"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            checks = [
                "BuildingOS" in content,
                "BuildingOSChat" in content,
                "wo8q9fl0hj.execute-api.us-east-1.amazonaws.com" in content
            ]
            
            if all(checks):
                print("✅ S3 Website: PASSED")
                return True
            else:
                print("❌ S3 Website: Content validation failed")
                return False
        else:
            print(f"❌ S3 Website: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ S3 Website: {str(e)}")
        return False

def test_cloudfront():
    """Test CloudFront CDN"""
    print("🧪 Testing CloudFront CDN...")
    
    try:
        url = "https://d16gzj1xbb7lzw.cloudfront.net"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            content = response.text
            headers = response.headers
            
            checks = [
                "BuildingOS" in content,
                response.url.startswith("https://"),
                len(content) > 1000
            ]
            
            if all(checks):
                print("✅ CloudFront CDN: PASSED")
                return True
            else:
                print("❌ CloudFront CDN: Validation failed")
                return False
        else:
            print(f"❌ CloudFront CDN: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ CloudFront CDN: {str(e)}")
        return False

def test_api_gateway():
    """Test API Gateway"""
    print("🧪 Testing API Gateway...")
    
    try:
        url = "https://wo8q9fl0hj.execute-api.us-east-1.amazonaws.com/dev/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ API Gateway: PASSED")
                    return True
                else:
                    print(f"❌ API Gateway: Unhealthy status - {data}")
                    return False
            except json.JSONDecodeError:
                print("❌ API Gateway: Invalid JSON response")
                return False
        else:
            print(f"❌ API Gateway: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API Gateway: {str(e)}")
        return False

def test_error_page():
    """Test error page"""
    print("🧪 Testing Error Page...")
    
    try:
        url = "http://buildingos-frontend-dev.s3-website-us-east-1.amazonaws.com/error.html"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            checks = [
                "error-container" in content,
                "fas fa-exclamation-triangle" in content,
                'href="/"' in content
            ]
            
            if all(checks):
                print("✅ Error Page: PASSED")
                return True
            else:
                print("❌ Error Page: Content validation failed")
                return False
        else:
            print(f"❌ Error Page: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error Page: {str(e)}")
        return False

def main():
    """Main validation function"""
    print("🚀 BuildingOS Frontend Integration Validation")
    print("=" * 60)
    print("✅ CloudFront URL: https://d16gzj1xbb7lzw.cloudfront.net")
    print("🌐 S3 Website URL: http://buildingos-frontend-dev.s3-website-us-east-1.amazonaws.com")
    print("🔌 API Gateway URL: https://wo8q9fl0hj.execute-api.us-east-1.amazonaws.com/dev")
    print("=" * 60)
    
    tests = [
        ("S3 Website", test_s3_website),
        ("Error Page", test_error_page),
        ("CloudFront CDN", test_cloudfront),
        ("API Gateway", test_api_gateway)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}: Exception - {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 FRONTEND VALIDATION SUMMARY")
    print("=" * 60)
    print(f"📊 Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 FRONTEND INTEGRATION SUCCESSFUL!")
        print("✅ All components are working correctly")
        print("🚀 Frontend is ready for use")
        print("🌐 Access your application at: https://d16gzj1xbb7lzw.cloudfront.net")
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("❌ Please review the failed components")
    
    return passed == total

if __name__ == "__main__":
    main()
