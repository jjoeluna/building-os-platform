output "websocket_api_execution_arn" {
  value = aws_apigatewayv2_api.websocket.execution_arn
}
output "websocket_api_id" {
  value = aws_apigatewayv2_api.websocket.id
}

output "websocket_api_endpoint" {
  value = aws_apigatewayv2_api.websocket.api_endpoint
}

output "websocket_stage_invoke_url" {
  value = aws_apigatewayv2_stage.prod.invoke_url
}
