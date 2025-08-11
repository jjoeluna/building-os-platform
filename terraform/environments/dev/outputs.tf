# === BuildingOS Infrastructure Outputs ===

# --- API Gateway ---
output "api_gateway_url" {
  description = "The invoke URL for the HTTP API"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "api_gateway_stage_name" {
  description = "The name of the API Gateway stage"
  value       = aws_apigatewayv2_stage.default.name
}

# --- Lambda Functions ---
output "lambda_functions" {
  description = "Lambda function names and ARNs"
  value = {
    agent_persona = {
      name = module.agent_persona.function_name
      arn  = module.agent_persona.function_arn
    }
    agent_director = {
      name = module.agent_director.function_name
      arn  = module.agent_director.function_arn
    }
    agent_coordinator = {
      name = module.agent_coordinator.function_name
      arn  = module.agent_coordinator.function_arn
    }
    agent_elevator = {
      name = module.agent_elevator.function_name
      arn  = module.agent_elevator.function_arn
    }
    agent_health_check = {
      name = module.agent_health_check.function_name
      arn  = module.agent_health_check.function_arn
    }
    agent_psim = {
      name = module.agent_psim.function_name
      arn  = module.agent_psim.function_arn
    }
  }
}

# --- Lambda Layer ---
output "lambda_layer" {
  description = "Lambda layer ARN"
  value = {
    common_utils = {
      arn = module.common_utils_layer.layer_arn
    }
  }
}

# --- IAM Roles ---
output "iam_roles" {
  description = "IAM role ARNs"
  value = {
    lambda_exec_role = module.lambda_iam_role.role_arn
  }
}

# --- SNS Topics ---
output "sns_topics" {
  description = "SNS topic ARNs"
  value = {
    # Novos tópicos com nomenclatura padronizada
    chat_intention_topic             = module.chat_intention_topic.topic_arn
    persona_intention_topic          = module.persona_intention_topic.topic_arn
    director_mission_topic           = module.director_mission_topic.topic_arn
    coordinator_task_topic           = module.coordinator_task_topic.topic_arn
    agent_task_result_topic          = module.agent_task_result_topic.topic_arn
    coordinator_mission_result_topic = module.coordinator_mission_result_topic.topic_arn
    director_response_topic          = module.director_response_topic.topic_arn
    persona_response_topic           = module.persona_response_topic.topic_arn
  }
}

# --- DynamoDB Tables ---
output "dynamodb_tables" {
  description = "DynamoDB table names and ARNs"
  value = {
    short_term_memory = {
      name = module.short_term_memory_db.table_name
      arn  = module.short_term_memory_db.table_arn
    }
    elevator_monitoring = {
      name = module.elevator_monitoring_db.table_name
      arn  = module.elevator_monitoring_db.table_arn
    }
    mission_state = {
      name = module.mission_state_db.table_name
      arn  = module.mission_state_db.table_arn
    }
  }
}

# --- Frontend Website ---
output "frontend_website" {
  description = "Frontend website URLs and bucket information"
  value = {
    s3_bucket_name   = module.frontend_website.bucket_name
    website_endpoint = module.frontend_website.website_endpoint
    cloudfront_url   = module.frontend_website.cloudfront_url
  }
}

# --- Environment Info ---
output "environment_info" {
  description = "Environment and region information"
  value = {
    environment = var.environment
    region      = data.aws_region.current.id
    account_id  = data.aws_caller_identity.current.account_id
  }
}
