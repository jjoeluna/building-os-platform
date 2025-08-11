resource "aws_iam_role" "this" {
  name               = var.role_name
  assume_role_policy = var.assume_role_policy
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "managed_policies" {
  for_each = toset(var.policy_arns)

  role       = aws_iam_role.this.name
  policy_arn = each.value
}

resource "aws_iam_role_policy_attachment" "custom_policies" {
  count = length(var.custom_policy_arns)

  role       = aws_iam_role.this.name
  policy_arn = var.custom_policy_arns[count.index]
}
