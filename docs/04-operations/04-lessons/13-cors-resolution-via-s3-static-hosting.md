---
date: "2025-08-05"
tags:
  - "CORS"
  - "S3"
  - "Frontend"
  - "Web Development"
---

# Lesson: CORS Resolution via S3 Static Hosting

## Context

During the implementation of the BuildingOS chat interface, we encountered CORS (Cross-Origin Resource Sharing) errors when serving HTML files from the local file system (`file://` protocol) while trying to access API Gateway endpoints.

## Problem

When serving web applications directly from the local file system, browsers enforce strict CORS policies that prevent JavaScript from making HTTP requests to external APIs, even when the API Gateway has CORS configured. The error manifested as:

```
Access to fetch at 'https://api-gateway-url.com/endpoint' from origin 'null' has been blocked by CORS policy
```

## Root Cause

- **File Protocol Limitation**: The `file://` protocol is treated as `null` origin by browsers
- **Browser Security**: Modern browsers block requests from `null` origin to prevent security vulnerabilities
- **API Gateway CORS**: Even with proper CORS configuration on API Gateway, the `null` origin issue persists

## Solution Applied

**S3 Static Website Hosting** proved to be the optimal solution:

1. **S3 Bucket Configuration**:
   ```terraform
   resource "aws_s3_bucket_website_configuration" "frontend_bucket_website" {
     bucket = aws_s3_bucket.frontend_bucket.id
     
     index_document {
       suffix = "chat-working.html"
     }
     
     error_document {
       key = "error.html"
     }
   }
   ```

2. **Public Access Policy**:
   ```terraform
   resource "aws_s3_bucket_policy" "frontend_bucket_policy" {
     bucket = aws_s3_bucket.frontend_bucket.id
     policy = jsonencode({
       Version = "2012-10-17"
       Statement = [{
         Effect = "Allow"
         Principal = "*"
         Action = "s3:GetObject"
         Resource = "${aws_s3_bucket.frontend_bucket.arn}/*"
       }]
     })
   }
   ```

3. **API Gateway CORS Configuration**:
   ```terraform
   cors_configuration {
     allow_credentials = false
     allow_headers     = ["*"]
     allow_methods     = ["*"]
     allow_origins     = ["*"]
     expose_headers    = ["*"]
     max_age          = 86400
   }
   ```

## Why This Works

- **HTTP Origin**: S3 static hosting provides a proper HTTP origin instead of `null`
- **CORS Compliance**: Browsers can properly validate CORS headers from API Gateway
- **Production-Like Environment**: Mimics production deployment scenarios
- **Cost Effective**: S3 static hosting is extremely cost-effective for static assets

## Alternative Solutions Considered

1. **Local HTTP Server**: Running `python -m http.server` or similar
   - ❌ **Downside**: Requires manual setup, not automated
   
2. **Browser Security Flags**: Disabling CORS in browser
   - ❌ **Downside**: Not practical for end users, security risk
   
3. **Proxy Server**: Local proxy to bypass CORS
   - ❌ **Downside**: Complex setup, additional infrastructure

## Implementation Pattern

For future web interface development:

1. **Development Phase**: Use S3 static hosting from the start
2. **Automated Deployment**: Include file upload in Terraform
3. **CORS Configuration**: Always configure both frontend hosting and backend API
4. **Testing**: Use the S3-hosted version for all testing

## Key Takeaway

**Always use proper HTTP hosting for web applications**, even during development. File system serving should only be used for basic HTML preview, not for applications that make API calls.

The S3 static hosting solution provides a production-ready, automated, and cost-effective approach that eliminates CORS issues while maintaining development agility.
