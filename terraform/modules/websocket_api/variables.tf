variable "name" {
  description = "Nome do WebSocket API"
  type        = string
}

variable "stage_name" {
  description = "Nome do stage (ex: prod, dev)"
  type        = string
}

variable "connect_lambda_arn" {
  description = "ARN da Lambda para $connect"
  type        = string
}

variable "disconnect_lambda_arn" {
  description = "ARN da Lambda para $disconnect"
  type        = string
}

variable "default_lambda_arn" {
  description = "ARN da Lambda para $default"
  type        = string
}
