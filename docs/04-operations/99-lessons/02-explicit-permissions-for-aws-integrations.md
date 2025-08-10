---
date: "2025-08-04"
tags:
  - "AWS"
  - "IAM"
  - "Permissions"
  - "SNS"
  - "Lambda"
---

# Lesson: AWS Service Integrations Require Explicit Permissions

## Context

After deploying the `director_agent` Lambda and subscribing it to the `intention_topic` SNS, we observed that the Lambda was never being invoked. Publishing messages to the topic had no effect, and no log streams were created in CloudWatch for the function.

## Lesson Learned

In the AWS ecosystem, configuring one service to target another (e.g., an SNS subscription pointing to a Lambda) is only half the process. The *source* service (SNS) must also be given explicit permission to invoke the *destination* service (Lambda). This was resolved by adding an `aws_lambda_permission` resource, which grants the `sns.amazonaws.com` principal the `lambda:InvokeFunction` action on our `director_agent`.

## Suggested Action

For any new event-driven integration between AWS services, always create a mental checklist:
1.  **Configuration:** Have I configured Service A to point to Service B?
2.  **Permission:** Have I created a policy or permission that allows Service A to perform the required action on Service B?
3.  **Network:** (If applicable) Is there a network path (VPC, security groups, NACLs) that allows the services to communicate?
