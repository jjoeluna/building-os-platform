[⬅️ Back to Index](../README.md)

# Monitoring & Alerting Strategy

## 1. Philosophy

Our monitoring philosophy is to focus on user-facing symptoms, not just internal causes. We primarily track the **Four Golden Signals** for our key services:

1.  **Latency:** How long does it take to service a request?
2.  **Traffic:** How much demand is being placed on the system?
3.  **Errors:** The rate of requests that fail.
4.  **Saturation:** How "full" the service is (e.g., CPU utilization, queue depth).

## 2. Key Dashboards

*A list of the primary dashboards used to observe system health.*

| Dashboard Name | Link | Purpose |
|---|---|---|
| Main API Health | [Link to CloudWatch Dashboard] | Tracks the Four Golden Signals for our public API Gateway. |
| Lambda Performance | [Link to CloudWatch Dashboard] | Monitors invocation counts, error rates, and durations for all Lambda functions. |
| ... | | |

## 3. Alerting Rules

*A list of critical alerts that will trigger a notification to the on-call team.*

| Alert Name | Service | Metric | Threshold | Severity |
|---|---|---|---|---|
| High API Error Rate | API Gateway | 5XX Errors | > 1% over 5 minutes | P1 (Critical) |
| High API Latency | API Gateway | p99 Latency | > 500ms over 5 minutes | P2 (Warning) |
| High Lambda Error Rate | `persona_agent` | Error Count | > 5 errors in 1 minute | P2 (Warning) |
| DynamoDB Throttling | `short_term_memory` | ThrottledWriteRequests | > 10 over 1 minute | P1 (Critical) |
| ... | | | | |
