variable "environment" {
  description = "Deployment environment (dev, prod)"
  type        = string
}

variable "raw_bucket_arn" {
  description = "ARN of S3 raw bucket"
  type        = string
}

variable "processed_bucket_arn" {
  description = "ARN of S3 processed bucket"
  type        = string
}
