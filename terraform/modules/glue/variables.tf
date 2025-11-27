variable "environment" {
  description = "Deployment environment (dev, prod, etc.)"
  type        = string
}

variable "raw_bucket_name" {
  description = "Name of the raw S3 bucket"
  type        = string
}

variable "processed_bucket_name" {
  description = "Name of the processed S3 bucket"
  type        = string
}

variable "glue_role_arn" {
  description = "IAM role ARN for Glue service"
  type        = string
}
