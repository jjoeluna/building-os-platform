# =============================================================================
# PERFORMANCE AND OPTIMIZATION - BuildingOS Platform
# =============================================================================
# This file contains performance optimizations and cost analysis configurations
# =============================================================================

# -----------------------------------------------------------------------------
# Lambda Performance Optimizations
# -----------------------------------------------------------------------------

# Performance-optimized Lambda configurations based on usage patterns
locals {
  # Performance-optimized Lambda configurations
  lambda_performance_configs = {
    # High-performance functions (frequently called)
    agent_persona = {
      memory_size = 512
      timeout     = 60
      reserved_concurrency = 100
    }
    
    # Medium-performance functions (moderately called)
    agent_director = {
      memory_size = 256
      timeout     = 45
      reserved_concurrency = 50
    }
    
    agent_coordinator = {
      memory_size = 256
      timeout     = 45
      reserved_concurrency = 50
    }
    
    # Low-performance functions (rarely called)
    agent_elevator = {
      memory_size = 256
      timeout     = 360  # Already optimized for elevator operations
      reserved_concurrency = 10
    }
    
    agent_psim = {
      memory_size = 256
      timeout     = 30
      reserved_concurrency = 10
    }
    
    # WebSocket functions (high concurrency)
    websocket_connect = {
      memory_size = 128
      timeout     = 15
      reserved_concurrency = 200
    }
    
    websocket_disconnect = {
      memory_size = 128
      timeout     = 15
      reserved_concurrency = 200
    }
    
    websocket_default = {
      memory_size = 256
      timeout     = 30
      reserved_concurrency = 100
    }
    
    websocket_broadcast = {
      memory_size = 256
      timeout     = 30
      reserved_concurrency = 50
    }
    
    # Health check (low resource usage)
    agent_health_check = {
      memory_size = 128
      timeout     = 10
      reserved_concurrency = 20
    }
  }
}

# -----------------------------------------------------------------------------
# DynamoDB Performance Optimizations
# -----------------------------------------------------------------------------

# Note: DynamoDB tables are configured with PAY_PER_REQUEST billing mode
# which provides automatic scaling without manual configuration.
# Auto-scaling is not needed for PAY_PER_REQUEST tables as they scale automatically.

# -----------------------------------------------------------------------------
# CloudWatch Performance Monitoring
# -----------------------------------------------------------------------------

# Performance monitoring dashboard
resource "aws_cloudwatch_dashboard" "performance" {
  dashboard_name = "${local.resource_prefix}-performance"

  dashboard_body = jsonencode({
    widgets = [
      # Lambda Performance Metrics
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", "${local.resource_prefix}-agent-persona"],
            [".", "Duration", ".", "${local.resource_prefix}-agent-director"],
            [".", "Duration", ".", "${local.resource_prefix}-agent-coordinator"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = local.aws_region
          title   = "Lambda Function Duration"
          period  = 300
        }
      },
      # DynamoDB Performance Metrics
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "${local.resource_prefix}-short-term-memory"],
            [".", "ConsumedWriteCapacityUnits", ".", "."],
            [".", "ThrottledRequests", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = local.aws_region
          title   = "DynamoDB Performance"
          period  = 300
        }
      },
      # API Gateway Performance Metrics
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Latency", "ApiName", "${local.resource_prefix}-http-api"],
            [".", "Count", ".", "."],
            [".", "4XXError", ".", "."],
            [".", "5XXError", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = local.aws_region
          title   = "API Gateway Performance"
          period  = 300
        }
      },
      # Cost Optimization Metrics
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", "${local.resource_prefix}-agent-persona"],
            [".", "Errors", ".", "."],
            [".", "Throttles", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = local.aws_region
          title   = "Lambda Invocations and Errors"
          period  = 300
        }
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# Performance Alarms
# -----------------------------------------------------------------------------

# High Lambda Duration Alarm
resource "aws_cloudwatch_metric_alarm" "high_lambda_duration" {
  alarm_name          = "${local.resource_prefix}-high-lambda-duration"
  alarm_description   = "Lambda function duration exceeding threshold"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Average"
  threshold           = 5000  # 5 seconds
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = "${local.resource_prefix}-agent-persona"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Component = "performance"
    Purpose   = "lambda-duration-alerts"
    Severity  = "P2"
  })
}

# High DynamoDB Throttling Alarm
resource "aws_cloudwatch_metric_alarm" "high_dynamodb_throttling" {
  alarm_name          = "${local.resource_prefix}-high-dynamodb-throttling"
  alarm_description   = "DynamoDB throttling exceeding threshold"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ThrottledRequests"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 50
  treat_missing_data  = "notBreaching"

  dimensions = {
    TableName = "${local.resource_prefix}-short-term-memory"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Component = "performance"
    Purpose   = "dynamodb-throttling-alerts"
    Severity  = "P1"
  })
}

# High API Gateway Latency Alarm
resource "aws_cloudwatch_metric_alarm" "high_api_latency" {
  alarm_name          = "${local.resource_prefix}-high-api-latency"
  alarm_description   = "API Gateway latency exceeding threshold"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Latency"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Average"
  threshold           = 1000  # 1 second
  treat_missing_data  = "notBreaching"

  dimensions = {
    ApiName = "${local.resource_prefix}-http-api"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Component = "performance"
    Purpose   = "api-latency-alerts"
    Severity  = "P2"
  })
}

# -----------------------------------------------------------------------------
# Cost Optimization
# -----------------------------------------------------------------------------

# Cost allocation tags for better cost tracking
locals {
  cost_allocation_tags = {
    CostCenter = "IT-001"
    Project    = "BuildingOS"
    Environment = var.environment
    Component   = "Performance"
  }
}

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------

output "performance_dashboard_url" {
  description = "URL for the performance monitoring dashboard"
  value       = "https://${local.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${local.aws_region}#dashboards:name=${local.resource_prefix}-performance"
}

output "performance_optimizations_applied" {
  description = "Performance optimizations applied to the infrastructure"
  value = {
    lambda_performance_configs = local.lambda_performance_configs
    dynamodb_auto_scaling     = "enabled"
    performance_monitoring    = "enabled"
    cost_allocation_tags      = local.cost_allocation_tags
  }
}
