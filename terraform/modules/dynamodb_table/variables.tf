variable "table_name" {
  description = "The name of the DynamoDB table"
  type        = string
}

variable "hash_key" {
  description = "The attribute to use as the hash key (primary key)"
  type        = string
}

variable "attributes" {
  description = "A list of attribute definitions for the table"
  type = list(object({
    name = string
    type = string # S for String, N for Number, B for Binary
  }))
  default = []
}

variable "ttl_attribute" {
  description = "The name of the attribute to use for Time To Live (TTL)"
  type        = string
  default     = null
}

variable "tags" {
  description = "A map of tags to assign to the resource"
  type        = map(string)
  default     = {}
}
