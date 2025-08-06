# This resource uses a special Docker image provided by AWS to build the dependencies
# in an environment that matches the Lambda execution environment.
resource "null_resource" "build_lambda_layer" {
  triggers = {
    requirements_md5 = filemd5(var.requirements_file)
  }

  provisioner "local-exec" {
    command = <<-EOT
      pip install -r ${var.requirements_file} -t ../../.terraform/layers/python
    EOT
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
