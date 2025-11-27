variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "raw_bucket_arn" {
  description = "ARN of the raw data S3 bucket"
  type        = string
}

variable "processed_bucket_arn" {
  description = "ARN of the processed data S3 bucket"
  type        = string
}
