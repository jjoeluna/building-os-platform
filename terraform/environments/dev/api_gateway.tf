# =============================================================================
# API Gateway - BuildingOS Platform
# =============================================================================
# This file contains all API Gateway resources using the global modules
# =============================================================================

# --- WebSocket API Gateway ---
module "websocket_api" {
  source                = "../../modules/websocket_api"
  name                  = "bos-websocket-api-${var.environment}"
  stage_name            = "dev"
  connect_lambda_arn    = module.websocket_connect.function_arn
  disconnect_lambda_arn = module.websocket_disconnect.function_arn
  default_lambda_arn    = module.websocket_default.function_arn
}

# --- HTTP API Gateway ---
resource "aws_apigatewayv2_api" "http_api" {
  name          = local.api_gateway_names.http_api
  protocol_type = local.api_gateway_defaults.protocol_type

  cors_configuration {
    allow_credentials = false
    allow_headers     = local.api_gateway_defaults.cors_configuration.allow_headers
    allow_methods     = local.api_gateway_defaults.cors_configuration.allow_methods
    allow_origins     = local.api_gateway_defaults.cors_configuration.allow_origins
    max_age           = 86400
  }

  tags = merge(local.common_tags, {
    Name      = "http-api"
    Type      = "API Gateway"
    Component = "HTTP API"
    Function  = "REST API"
    ManagedBy = "Terraform"
  })
}

# --- HTTP API Integrations ---

# Health Check Integration
resource "aws_apigatewayv2_integration" "agent_health_check_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = module.agent_health_check.function_invoke_arn
}

resource "aws_apigatewayv2_route" "agent_health_check_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.agent_health_check_integration.id}"
}

# Persona Integration
resource "aws_apigatewayv2_integration" "agent_persona_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = module.agent_persona.function_invoke_arn
}

resource "aws_apigatewayv2_route" "agent_persona_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /persona"
  target    = "integrations/${aws_apigatewayv2_integration.agent_persona_integration.id}"
}

resource "aws_apigatewayv2_route" "agent_persona_get_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /persona/conversations"
  target    = "integrations/${aws_apigatewayv2_integration.agent_persona_integration.id}"
}

# Director Integration
resource "aws_apigatewayv2_integration" "agent_director_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = module.agent_director.function_invoke_arn
}

resource "aws_apigatewayv2_route" "agent_director_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /director"
  target    = "integrations/${aws_apigatewayv2_integration.agent_director_integration.id}"
}

# Elevator Integration
resource "aws_apigatewayv2_integration" "agent_elevator_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = module.agent_elevator.function_invoke_arn
}

resource "aws_apigatewayv2_route" "agent_elevator_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /elevator/call"
  target    = "integrations/${aws_apigatewayv2_integration.agent_elevator_integration.id}"
}

# PSIM Integration
resource "aws_apigatewayv2_integration" "agent_psim_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = module.agent_psim.function_invoke_arn
}

resource "aws_apigatewayv2_route" "agent_psim_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /psim/search"
  target    = "integrations/${aws_apigatewayv2_integration.agent_psim_integration.id}"
}

# Coordinator Integration
resource "aws_apigatewayv2_integration" "agent_coordinator_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = module.agent_coordinator.function_invoke_arn
}

resource "aws_apigatewayv2_route" "agent_coordinator_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /coordinator/missions/{mission_id}"
  target    = "integrations/${aws_apigatewayv2_integration.agent_coordinator_integration.id}"
}

resource "aws_apigatewayv2_route" "agent_coordinator_status_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /coordinator/status"
  target    = "integrations/${aws_apigatewayv2_integration.agent_coordinator_integration.id}"
}

# --- HTTP API Stage ---
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = var.environment
  auto_deploy = true

  tags = merge(local.common_tags, {
    Name      = "http-api-stage"
    Type      = "API Gateway Stage"
    Component = "HTTP API"
    Function  = "Stage"
    ManagedBy = "Terraform"
  })
}

# --- Lambda Permissions for HTTP API ---

# Health Check Permission
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_health_check.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# Persona Permission
resource "aws_lambda_permission" "api_gateway_permission_persona" {
  statement_id  = "AllowAPIGatewayInvokePersona"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_persona.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# Director Permission
resource "aws_lambda_permission" "api_gateway_permission_director" {
  statement_id  = "AllowAPIGatewayInvokeDirector"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_director.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# Elevator Permission
resource "aws_lambda_permission" "api_gateway_permission_elevator" {
  statement_id  = "AllowAPIGatewayInvokeElevator"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_elevator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# PSIM Permission
resource "aws_lambda_permission" "api_gateway_permission_psim" {
  statement_id  = "AllowAPIGatewayInvokePSIM"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_psim.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# Coordinator Permission
resource "aws_lambda_permission" "api_gateway_permission_coordinator" {
  statement_id  = "AllowAPIGatewayInvokeCoordinator"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_coordinator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# --- Lambda Permissions for WebSocket API ---

# WebSocket Connect Permission
resource "aws_lambda_permission" "websocket_connect_apigw" {
  statement_id  = "AllowAPIGatewayInvokeConnect"
  action        = "lambda:InvokeFunction"
  function_name = module.websocket_connect.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${module.websocket_api.websocket_api_execution_arn}/*"
}

# WebSocket Disconnect Permission
resource "aws_lambda_permission" "websocket_disconnect_apigw" {
  statement_id  = "AllowAPIGatewayInvokeDisconnect"
  action        = "lambda:InvokeFunction"
  function_name = module.websocket_disconnect.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${module.websocket_api.websocket_api_execution_arn}/*"
}

# WebSocket Default Permission
resource "aws_lambda_permission" "websocket_default_apigw" {
  statement_id  = "AllowAPIGatewayInvokeDefault"
  action        = "lambda:InvokeFunction"
  function_name = module.websocket_default.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${module.websocket_api.websocket_api_execution_arn}/*"
}
