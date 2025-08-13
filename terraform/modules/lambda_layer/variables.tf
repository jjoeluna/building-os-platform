variable "layer_name" {
  description = "The name of the Lambda Layer."
  type        = string
}

variable "requirements_file" {
  description = "The path to the requirements.txt file."
  type        = string
}

variable "source_dir" {
  description = "The path to the source directory containing Python utility files to include in the layer."
  type        = string
}

variable "runtime" {
  description = "The Lambda runtime compatible with the layer (e.g., python3.11)."
  type        = string
}
