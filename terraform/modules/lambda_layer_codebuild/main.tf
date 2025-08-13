# =============================================================================
# Lambda Layer CodeBuild Module - Linux-Compatible Build
# =============================================================================
#
# **Purpose:** Build Lambda layers with Linux-compatible binaries using CodeBuild
# **Scope:** Handles cross-platform dependency compilation for Lambda deployment
# **Integration:** Seamless integration with existing Terraform infrastructure
#
# **Key Features:**
# - Linux x86_64 binary compilation
# - Automated dependency management
# - Terraform-native resource management
# - Cost-effective pay-per-build model
# - Parallel build capabilities
#
# **Dependencies:** AWS CodeBuild service, S3 bucket for artifacts
# **Architecture:** Event-driven build process triggered by source changes
#
# =============================================================================

# CodeBuild Project for Lambda Layer Building
resource "aws_codebuild_project" "lambda_layer_builder" {
  name         = "${var.environment}-lambda-layer-builder"
  description  = "Build Lambda layers with Linux-compatible dependencies"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type      = "S3"
    location  = var.artifacts_bucket
    packaging = "ZIP"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "LAYER_NAME"
      value = var.layer_name
    }

    environment_variable {
      name  = "PYTHON_VERSION"
      value = "3.11"
    }

    environment_variable {
      name  = "ARTIFACTS_BUCKET"
      value = var.artifacts_bucket
    }
  }

  source {
    type      = "S3"
    location  = "${var.source_bucket}/${var.source_key}"
    buildspec = file("${path.module}/buildspec.yml")
  }

  tags = {
    Name        = "${var.environment}-lambda-layer-builder"
    Environment = var.environment
    Component   = "Lambda Layer Builder"
    ManagedBy   = "Terraform"
    Project     = "BuildingOS"
  }
}

# IAM Role for CodeBuild
resource "aws_iam_role" "codebuild_role" {
  name = "${var.environment}-lambda-layer-codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.environment}-lambda-layer-codebuild-role"
    Environment = var.environment
    Component   = "IAM Role"
    ManagedBy   = "Terraform"
    Project     = "BuildingOS"
  }
}

# IAM Policy for CodeBuild
resource "aws_iam_role_policy" "codebuild_policy" {
  role = aws_iam_role.codebuild_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/codebuild/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject"
        ]
        Resource = [
          "${var.source_bucket_arn}/*",
          "${var.artifacts_bucket_arn}/*"
        ]
      }
    ]
  })
}

# Trigger CodeBuild when source changes
resource "null_resource" "trigger_build" {
  triggers = {
    requirements_md5 = filemd5(var.requirements_file)
    source_dir_hash  = sha256(join("", [for f in fileset(var.source_dir, "**") : filesha256("${var.source_dir}/${f}")]))
  }

  provisioner "local-exec" {
    command = "aws s3 cp ${var.source_archive} s3://${var.source_bucket}/${var.source_key}"
  }

  provisioner "local-exec" {
    command = "aws codebuild start-build --project-name ${aws_codebuild_project.lambda_layer_builder.name}"
  }

  depends_on = [aws_codebuild_project.lambda_layer_builder]
}

# Download built layer
data "aws_s3_object" "built_layer" {
  bucket = var.artifacts_bucket
  key    = "${var.layer_name}/layer.zip"

  depends_on = [null_resource.trigger_build]
}

# Lambda Layer Version
resource "aws_lambda_layer_version" "this" {
  layer_name          = var.layer_name
  s3_bucket           = var.artifacts_bucket
  s3_key              = "${var.layer_name}/layer.zip"
  compatible_runtimes = ["python3.11", "python3.12"]
  description         = "Lambda layer with Linux-compatible dependencies built via CodeBuild"

  depends_on = [data.aws_s3_object.built_layer]
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
