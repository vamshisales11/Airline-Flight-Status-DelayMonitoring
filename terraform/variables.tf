variable "aws_region" {
  description = "AWS region to deploy resources"
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile name"
  default     = "vamshi2"
}

variable "environment" {
  description = "Deployment environment (dev, prod)"
  default     = "dev"
}


variable "redshift_serverless_username" {
  description = "Admin username for Redshift Serverless"
  type        = string
  default     = "admin"
}

variable "redshift_serverless_password" {
  description = "Admin password for Redshift Serverless"
  type        = string
  sensitive   = true
}
