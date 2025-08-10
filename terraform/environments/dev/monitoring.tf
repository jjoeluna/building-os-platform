# =============================================================================
# MONITORING AND ALERTING - BuildingOS Platform
# =============================================================================

# -----------------------------------------------------------------------------
# SNS Topic for Alerts
# -----------------------------------------------------------------------------

resource "aws_sns_topic" "alerts" {
  name = "${local.resource_prefix}-alerts"

  tags = merge(local.common_tags, {
    Component = "monitoring"
    Purpose   = "alert-notifications"
  })
}

resource "aws_sns_topic_subscription" "alerts_email" {
  count     = var.alert_email != null ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# -----------------------------------------------------------------------------
# CloudWatch Dashboards
# -----------------------------------------------------------------------------

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.resource_prefix}-monitoring"

  dashboard_body = jsonencode({
    widgets = [
      # Lambda Function Metrics
      {
        type   = "metric"
        x      = 0
        y      = 0
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
          title   = "Lambda Function Metrics - Agent Persona"
          period  = 300
        }
      },
      # API Gateway Metrics
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", "ApiName", "${local.resource_prefix}-http-api"],
            [".", "4XXError", ".", "."],
            [".", "5XXError", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = local.aws_region
          title   = "API Gateway Metrics"
          period  = 300
        }
      },
      # DynamoDB Performance
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "${local.resource_prefix}-short-term-memory"],
            [".", "ConsumedWriteCapacityUnits", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = local.aws_region
          title   = "DynamoDB Performance"
          period  = 300
        }
      },
      # SNS Topic Metrics
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/SNS", "NumberOfMessagesPublished", "TopicName", "${local.resource_prefix}-persona-intention-topic"],
            [".", "NumberOfNotificationsDelivered", ".", "."],
            [".", "NumberOfNotificationsFailed", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = local.aws_region
          title   = "SNS Topic Metrics"
          period  = 300
        }
      },
      # Recent Lambda Errors Log
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6
        properties = {
          query  = "SOURCE '/aws/lambda/${local.resource_prefix}-agent-persona'\n| fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 20"
          region = local.aws_region
          title  = "Recent Lambda Errors"
          view   = "table"
        }
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# CloudWatch Alarms - P1 (Critical)
# -----------------------------------------------------------------------------

# Lambda Function Errors
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.resource_prefix}-lambda-errors"
  alarm_description   = "Lambda function errors in ${var.environment} environment"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = "${local.resource_prefix}-agent-persona"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Component = "monitoring"
    Purpose   = "lambda-error-alerts"
    Severity  = "P1"
  })
}

# API Gateway Errors
resource "aws_cloudwatch_metric_alarm" "api_errors" {
  alarm_name          = "${local.resource_prefix}-api-errors"
  alarm_description   = "API Gateway errors in ${var.environment} environment"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"

  dimensions = {
    ApiName = "${local.resource_prefix}-http-api"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Component = "monitoring"
    Purpose   = "api-error-alerts"
    Severity  = "P1"
  })
}

# DynamoDB Throttling
resource "aws_cloudwatch_metric_alarm" "dynamodb_throttling" {
  alarm_name          = "${local.resource_prefix}-dynamodb-throttling"
  alarm_description   = "DynamoDB throttling in ${var.environment} environment"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ThrottledRequests"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  treat_missing_data  = "notBreaching"

  dimensions = {
    TableName = "${local.resource_prefix}-short-term-memory"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Component = "monitoring"
    Purpose   = "dynamodb-throttling-alerts"
    Severity  = "P1"
  })
}

# Lambda Function Duration
resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "${local.resource_prefix}-lambda-duration"
  alarm_description   = "Lambda function duration in ${var.environment} environment"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Average"
  threshold           = 10000
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = "${local.resource_prefix}-agent-persona"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Component = "monitoring"
    Purpose   = "lambda-duration-alerts"
    Severity  = "P2"
  })
}

# -----------------------------------------------------------------------------
# CloudWatch Alarms - P2 (Warning)
# -----------------------------------------------------------------------------

# High API Latency
resource "aws_cloudwatch_metric_alarm" "api_latency" {
  alarm_name          = "${local.resource_prefix}-api-latency"
  alarm_description   = "High API latency in ${var.environment} environment"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Latency"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Average"
  threshold           = 500
  treat_missing_data  = "notBreaching"

  dimensions = {
    ApiName = "${local.resource_prefix}-http-api"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Component = "monitoring"
    Purpose   = "api-latency-alerts"
    Severity  = "P2"
  })
}

# High Lambda Error Rate
resource "aws_cloudwatch_metric_alarm" "lambda_error_rate" {
  alarm_name          = "${local.resource_prefix}-lambda-error-rate"
  alarm_description   = "High Lambda error rate in ${var.environment} environment"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = "${local.resource_prefix}-agent-persona"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Component = "monitoring"
    Purpose   = "lambda-error-rate-alerts"
    Severity  = "P2"
  })
}

# -----------------------------------------------------------------------------
# CloudWatch Alarms - P3 (Info)
# -----------------------------------------------------------------------------

# High Traffic
resource "aws_cloudwatch_metric_alarm" "high_traffic" {
  alarm_name          = "${local.resource_prefix}-high-traffic"
  alarm_description   = "High traffic in ${var.environment} environment"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Count"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Sum"
  threshold           = 1000
  treat_missing_data  = "notBreaching"

  dimensions = {
    ApiName = "${local.resource_prefix}-http-api"
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Component = "monitoring"
    Purpose   = "high-traffic-alerts"
    Severity  = "P3"
  })
}

# -----------------------------------------------------------------------------
# Log Groups for Monitoring
# -----------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "lambda_monitoring" {
  for_each = toset([
    "${local.resource_prefix}-agent-persona",
    "${local.resource_prefix}-agent-director",
    "${local.resource_prefix}-agent-coordinator",
    "${local.resource_prefix}-agent-elevator",
    "${local.resource_prefix}-agent-psim",
    "${local.resource_prefix}-agent-health-check"
  ])

  name              = "/aws/lambda/${each.value}"
  retention_in_days = 14

  tags = merge(local.common_tags, {
    Component = "monitoring"
    Purpose   = "lambda-logs"
  })
}

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------

output "monitoring_dashboard_url" {
  description = "URL for the CloudWatch monitoring dashboard"
  value       = "https://${local.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${local.aws_region}#dashboards:name=${local.resource_prefix}-monitoring"
}

output "alerts_sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = aws_sns_topic.alerts.arn
}
