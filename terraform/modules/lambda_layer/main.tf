# =============================================================================
# BuildingOS Platform - Lambda Layer Module
# =============================================================================
# 
# **Purpose:** Creates Lambda layers with Python dependencies and utilities
# **Scope:** Builds and deploys Lambda layers with consistent dependency management
# **Usage:** Used by environment configurations to create shared Lambda layers
# 
# **Key Features:**
# - Automated dependency installation from requirements.txt
# - Proper packaging for Lambda runtime environment
# - Version management with source code hash tracking
# - Optimized build process for consistent layer creation
# 
# **Dependencies:** 
# - requirements.txt file with Python dependencies
# - Local pip installation for dependency resolution
# - Archive provider for ZIP creation
# 
# **Integration:** 
# - Used by all Lambda functions requiring shared dependencies
# - Provides common utilities and AWS client management
# - Supports multiple Python runtimes (python3.11, python3.12)
# 
# **Security Considerations:**
# - Dependencies installed in isolated environment
# - Version pinning for security and consistency
# - Clean build process prevents dependency conflicts
# 
# =============================================================================

# Lambda Layer Dependency Build Process
# This resource uses pip to install dependencies and copies utility files
# in an environment that matches the Lambda execution environment
resource "null_resource" "build_lambda_layer" {
  triggers = {
    requirements_md5 = filemd5(var.requirements_file)
    source_dir_hash  = sha256(join("", [for f in fileset(var.source_dir, "**") : filesha256("${var.source_dir}/${f}")]))
  }

  provisioner "local-exec" {
    command     = <<-EOT
      # Create clean build directory
      if (Test-Path "../../.terraform/layers") { Remove-Item -Recurse -Force "../../.terraform/layers" }
      New-Item -ItemType Directory -Force -Path "../../.terraform/layers/python" | Out-Null
      
      # Install dependencies from requirements.txt
      pip install -r ${var.requirements_file} -t ../../.terraform/layers/python
      
      # Copy utility Python files to layer
      Copy-Item -Path "${var.source_dir}/*" -Destination "../../.terraform/layers/python/" -Recurse -Force
    EOT
    interpreter = ["PowerShell", "-Command"]
  }
}

data "archive_file" "lambda_layer_zip" {
  type        = "zip"
  source_dir  = "../../.terraform/layers"
  output_path = "${path.module}/../../.terraform/${var.layer_name}_layer.zip"
  depends_on  = [null_resource.build_lambda_layer]
}

resource "aws_lambda_layer_version" "this" {
  layer_name          = var.layer_name
  filename            = data.archive_file.lambda_layer_zip.output_path
  source_code_hash    = data.archive_file.lambda_layer_zip.output_base64sha256
  compatible_runtimes = [var.runtime]
}
