variable "environment" {
  description = "Deployment environment (dev, prod, etc.)"
  type        = string
}

variable "raw_bucket_arn" {
  description = "ARN of raw S3 bucket"
  type        = string
}

variable "processed_bucket_arn" {
  description = "ARN of processed S3 bucket"
  type        = string
}
