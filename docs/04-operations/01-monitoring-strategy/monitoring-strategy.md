[⬅️ Back to Index](../README.md)

# Monitoring & Alerting Strategy

## 1. Philosophy

Our monitoring philosophy is to focus on user-facing symptoms, not just internal causes. We primarily track the **Four Golden Signals** for our key services:

1.  **Latency:** How long does it take to service a request?
2.  **Traffic:** How much demand is being placed on the system?
3.  **Errors:** The rate of requests that fail.
4.  **Saturation:** How "full" the service is (e.g., CPU utilization, queue depth).

## 2. Architecture Overview

### **Monitoring Stack**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AWS Services  │    │  CloudWatch     │    │   SNS Alerts    │
│                 │    │                 │    │                 │
│ • Lambda        │───▶│ • Metrics       │───▶│ • Email         │
│ • API Gateway   │    │ • Logs          │    │ • SMS           │
│ • DynamoDB      │    │ • Dashboards    │    │ • Webhook       │
│ • SNS           │    │ • Alarms        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Process Flow**
```
AWS Services → CloudWatch Agent → Metrics Collection → Alarm Evaluation → SNS Notification
     ↓              ↓                    ↓                    ↓                    ↓
  • Lambda      • Automatic         • Real-time           • Threshold         • Email
  • API GW      • 5-minute          • Historical          • Comparison        • SMS
  • DynamoDB    • 1-minute          • Aggregated          • Action            • Webhook
```

## 3. Key Dashboards

*A list of the primary dashboards used to observe system health.*

| Dashboard Name | Purpose | Key Metrics | Access |
|---|---|---|---|
| **BuildingOS Main Monitoring** | Centralized view of all infrastructure metrics | Lambda, API Gateway, DynamoDB, SNS metrics | CloudWatch Dashboard: `bos-dev-monitoring` |
| **BuildingOS Performance** | Performance-focused metrics and optimization | Duration, performance, cost optimization | CloudWatch Dashboard: `bos-dev-performance` |
| **BuildingOS API Health** | Tracks the Four Golden Signals for our public API Gateway | Response time, error rate, throughput, availability | CloudWatch Dashboard: `BuildingOS-API-Health-{env}` |
| **Lambda Performance** | Monitors invocation counts, error rates, and durations for all Lambda functions | Invocation count, error rate, duration, concurrent executions | CloudWatch Dashboard: `BuildingOS-Lambda-Performance-{env}` |
| **SNS Event Flow** | Tracks message flow through SNS topics and Lambda triggers | Message count, delivery success rate, dead letter queue | CloudWatch Dashboard: `BuildingOS-SNS-Flow-{env}` |
| **DynamoDB Performance** | Monitors database performance and throttling | Read/Write capacity, throttled requests, consumed capacity | CloudWatch Dashboard: `BuildingOS-DynamoDB-{env}` |
| **Agent Health** | Individual agent performance and health status | Agent response time, error rate, memory usage | CloudWatch Dashboard: `BuildingOS-Agent-Health-{env}` |

### **Dashboard URLs**
- **Main Monitoring**: `https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=bos-dev-monitoring`
- **Performance**: `https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=bos-dev-performance`

## 4. Alerting Rules

*A list of critical alerts that will trigger a notification to the on-call team.*

### **P1 (Critical) - Immediate Response Required**

| Alert Name | Service | Metric | Threshold | Response Time |
|---|---|---|---|---|
| **Lambda Errors** | Lambda | Errors | > 1 error | 5 minutes |
| **API Gateway Errors** | API Gateway | 5XX Errors | > 1 error | 5 minutes |
| **DynamoDB Throttling** | DynamoDB | ThrottledRequests | > 10 requests | 5 minutes |
| **High API Error Rate** | API Gateway | 5XX Errors | > 1% over 5 minutes | 5 minutes |
| **Lambda Function Failure** | Lambda | Error Rate | > 10% over 5 minutes | 5 minutes |
| **SNS Message Loss** | SNS | DeadLetterQueueMessages | > 5 messages | 10 minutes |
| **Agent Unresponsive** | Lambda | Timeout Errors | > 3 timeouts in 5 minutes | 5 minutes |

### **P2 (Warning) - Investigation Required**

| Alert Name | Service | Metric | Threshold | Response Time |
|---|---|---|---|---|
| **Lambda Duration** | Lambda | Duration | > 10 seconds | 15 minutes |
| **API Latency** | API Gateway | Latency | > 500ms | 15 minutes |
| **Lambda Error Rate** | Lambda | Error Rate | > 5 errors | 15 minutes |
| **High API Latency** | API Gateway | p99 Latency | > 500ms over 5 minutes | 15 minutes |
| **High Lambda Error Rate** | Lambda | Error Count | > 5 errors in 1 minute | 15 minutes |
| **Elevator API Slow** | External API | Response Time | > 3 seconds | 15 minutes |
| **PSIM Integration Issues** | External API | Error Rate | > 5% over 10 minutes | 15 minutes |
| **Memory Usage High** | Lambda | Memory Utilization | > 80% | 30 minutes |

### **P3 (Info) - Monitoring**

| Alert Name | Service | Metric | Threshold | Response Time |
|---|---|---|---|---|
| **High Traffic** | API Gateway | Request Count | > 1000 requests | 1 hour |
| **High Traffic** | API Gateway | Request Count | > 1000 requests/minute | 1 hour |
| **Database Growth** | DynamoDB | Table Size | > 80% of capacity | 4 hours |
| **Cost Alert** | AWS Billing | Daily Cost | > $50/day | 4 hours |

## 5. Escalation Process

### **Escalation Matrix**
| Time | P1 (Critical) | P2 (Warning) | P3 (Info) |
|------|---------------|--------------|-----------|
| 0-15min | Immediate response | Monitor | Review |
| 15-30min | Escalate to lead | Response required | Monitor |
| 30-60min | Escalate to manager | Escalate to lead | Response required |
| 1-4h | Escalate to director | Escalate to manager | Escalate to lead |

### **Level 1: On-Call Engineer**
- **Response Time:** 5 minutes for P1, 15 minutes for P2
- **Actions:** Initial investigation, basic troubleshooting
- **Tools:** CloudWatch, AWS Console, logs

### **Level 2: Senior Engineer**
- **Escalation:** If P1 not resolved in 15 minutes, P2 not resolved in 30 minutes
- **Actions:** Deep investigation, code review, temporary fixes
- **Tools:** X-Ray, CloudTrail, development environment

### **Level 3: Tech Lead**
- **Escalation:** If P1 not resolved in 30 minutes, P2 not resolved in 1 hour
- **Actions:** Architectural decisions, rollback planning, stakeholder communication
- **Tools:** Full system access, deployment tools

## 6. Key Metrics Monitored

### **Lambda Functions**
- **Invocations**: Number of function executions
- **Errors**: Failed executions
- **Duration**: Execution time (average, max, min)
- **Throttles**: Rate limiting events
- **Concurrency**: Active executions

### **API Gateway**
- **Count**: Total requests
- **4XXError/5XXError**: Client/server errors
- **Latency**: Response time
- **IntegrationLatency**: Backend response time

### **DynamoDB**
- **ConsumedRead/WriteCapacityUnits**: Capacity usage
- **ThrottledRequests**: Throttled requests
- **ProvisionedRead/WriteCapacityUnits**: Provisioned capacity

### **SNS**
- **NumberOfMessagesPublished**: Messages published
- **NumberOfNotificationsDelivered/Failed**: Delivery status

## 7. Implementation Details

### **CloudWatch Dashboards Setup**

```bash
# Create main monitoring dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "bos-dev-monitoring" \
  --dashboard-body file://dashboards/main-monitoring.json

# Create performance dashboard  
aws cloudwatch put-dashboard \
  --dashboard-name "bos-dev-performance" \
  --dashboard-body file://dashboards/performance.json
```

### **Alert Configuration**

```hcl
# Example CloudWatch Alarm for Lambda Errors
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
```

### **SNS Alert System**
- **Topic Name**: `bos-dev-alerts`
- **Purpose**: Centralized alert notifications
- **Subscriptions**: Email (configurable via `alert_email` variable)

### **Integration with PagerDuty/Slack**

```python
# Lambda function for alert processing
def lambda_handler(event, context):
    alarm = event['detail']
    
    if alarm['state']['value'] == 'ALARM':
        # Send to PagerDuty
        send_pagerduty_alert(alarm)
        
        # Send to Slack
        send_slack_notification(alarm)
        
        # Log for audit
        log_alert(alarm)
```

## 8. Runbook Integration

Each alert is linked to a specific runbook in our [Runbook Templates](../02-runbook-template/runbook-template.md):

- **API Error Rate** → [API Troubleshooting Runbook](../02-runbook-template/api-troubleshooting.md)
- **Lambda Failures** → [Lambda Debugging Runbook](../02-runbook-template/lambda-debugging.md)
- **Database Issues** → [DynamoDB Troubleshooting Runbook](../02-runbook-template/dynamodb-troubleshooting.md)

## 9. Continuous Improvement

### **Weekly Review Process**
1. **Alert Analysis:** Review all triggered alerts
2. **False Positive Reduction:** Tune thresholds and conditions
3. **Response Time Optimization:** Identify bottlenecks
4. **Documentation Updates:** Update runbooks based on incidents

### **Monthly Metrics Review**
- **MTTR (Mean Time to Resolution):** Target < 30 minutes for P1
- **False Positive Rate:** Target < 5%
- **Alert Volume:** Target < 10 alerts per day
- **Coverage:** Ensure all critical paths are monitored

### **Monitoring Improvements**
1. **Metric Expansion**: Add new metrics as needed
2. **Alert Optimization**: Tune thresholds based on experience
3. **Dashboard Enhancement**: Add new widgets and views
4. **Automation**: Automate response actions where possible
5. **Documentation**: Keep documentation updated

### **Process Improvements**
1. **Incident Reviews**: Learn from incidents
2. **Team Training**: Regular monitoring training
3. **Tool Evaluation**: Evaluate new monitoring tools
4. **Integration**: Integrate with other tools (Slack, PagerDuty)
5. **Feedback Loop**: Gather feedback from team

## 10. Support

### **Monitoring Support**
- **Documentation**: This document and related guides
- **Team**: DevOps team for monitoring issues
- **Escalation**: Follow escalation matrix for urgent issues
- **Training**: Regular monitoring training sessions

### **Contact Information**
- **DevOps Team**: [Contact Information]
- **Emergency**: [Emergency Contact]
- **Documentation**: [Documentation Repository]

---

**Navigation:**
⬅️ Back: [Operations](../README.md)  
🏠 Home: [Documentation Index](../../README.md)
