resource "aws_dynamodb_table" "this" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST" # Ideal for serverless and unpredictable workloads
  hash_key     = var.hash_key

  dynamic "attribute" {
    for_each = var.attributes
    content {
      name = attribute.value.name
      type = attribute.value.type
    }
  }

  dynamic "ttl" {
    for_each = var.ttl_attribute != null ? [1] : []
    content {
      attribute_name = var.ttl_attribute
      enabled        = true
    }
  }

  tags = var.tags
}
