variable "role_name" {
  description = "The name of the IAM role."
  type        = string
}

variable "assume_role_policy" {
  description = "The JSON policy document that grants an entity permission to assume the role."
  type        = string
}

variable "policy_arns" {
  description = "A list of IAM policy ARNs to attach to the role."
  type        = list(string)
  default     = []
}

variable "custom_policy_arns" {
  description = "A list of custom IAM policy ARNs to attach to the role (for policies created in the same apply)."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "A map of tags to assign to the resource."
  type        = map(string)
  default     = {}
}
